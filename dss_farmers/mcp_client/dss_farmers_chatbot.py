import logging
from typing import Dict, Any
import json
import asyncio
import torch
from transformers import LlamaTokenizer, LlamaForCausalLM
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from dotenv import load_dotenv
from mcp_use import MCPClient
from mcp import ClientSession
from mcp.client.sse import sse_client

# Import from our modular project structure
from dss_farmers.models.soil_conditions import SoilConditions
from dss_farmers.models.crop_details import CropDetails
from dss_farmers.models.fertilizers import Fertilizers
from dss_farmers.models.farmer_input import FarmerInput
from dss_farmers.models.demographic_info import DemographicInfo
from dss_farmers.prompts.prompt_template_dss import FarmerPromptTemplates
from dss_farmers.config.config import MCP_SERVERS, LLM_CONFIG

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dss-farmers-chatbot")

# Load environment variables
load_dotenv()


def extract_weather_data(response):
    """Extract weather data from the response object.

    The response comes in a complex format where the actual JSON is inside the
    content[0].text field as a string that needs to be parsed.
    """
    try:
        if hasattr(response, "content") and response.content:
            text_content = response.content[0].text
            # Parse the text as JSON
            weather_data = json.loads(text_content)
            return weather_data
        return {"error": "No content in response"}
    except Exception as e:
        return {"error": f"Failed to parse response: {str(e)}"}


def optimize_weather_data_for_llm(weather_data: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce the size of weather data to fit within LLM context limits."""
    try:
        if "error" in weather_data:
            return weather_data

        compact_data = {"forecast": {"forecastday": []}, "alerts": {"alert": []}}

        # Only keep 3 days of forecast instead of 7
        for day in weather_data.get("forecast", {}).get("forecastday", [])[:3]:
            compact_day = {
                "date": day.get("date"),
                "day": {
                    "condition": day.get("day", {}).get("condition", {}),
                    "maxtemp_c": day.get("day", {}).get("maxtemp_c"),
                    "mintemp_c": day.get("day", {}).get("mintemp_c"),
                    "totalprecip_mm": day.get("day", {}).get("totalprecip_mm"),
                    "daily_chance_of_rain": day.get("day", {}).get(
                        "daily_chance_of_rain"
                    ),
                    "maxwind_kph": day.get("day", {}).get("maxwind_kph"),
                    "avghumidity": day.get("day", {}).get("avghumidity"),
                    "uv": day.get("day", {}).get("uv"),
                },
            }
            compact_data["forecast"]["forecastday"].append(compact_day)

        # Copy any alerts
        compact_data["alerts"]["alert"] = weather_data.get("alerts", {}).get(
            "alert", []
        )

        return compact_data
    except Exception as e:
        logger.error(f"Error optimizing weather data: {e}")
        return {"error": str(e), "forecast": {}, "alerts": {}}


# We can't use MCPAgent with PLLaMa-7b-base as it lacks agentic abilities
# Instead, we'll create MCPClients for each server
# TODO: Search for small LLMs on HuggingFace with Agentic abilities
def initialize_mcp_clients():
    """Initialize MCP clients from configuration"""
    clients = {}
    for server_name, server_config in MCP_SERVERS.items():
        # Create a proper config dictionary for each server
        server_config_dict = {
            "mcpServers": {server_name: {"url": server_config["url"]}}
        }
        clients[server_name] = MCPClient(config=server_config_dict)
    return clients


def load_agriqbot_model():
    """Load the AgriQBot model and tokenizer"""
    model_name = LLM_CONFIG["model_name"]
    logger.info(f"Loading model {model_name}... this may take a few minutes")

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    return model, tokenizer


def get_farmer_input() -> FarmerInput:
    """Collect input from the farmer through console interface"""
    logger.info("Getting farmer input")
    print("\n===== DSS Farmers Assistant =====\n")

    name = input("Enter farmer's name: ")
    location = input("Enter farmer's location: ")

    # Collect demographic information
    age = int(input("Enter farmer's age: "))
    gender = input("Enter farmer's gender: ")
    education_level = input("Enter farmer's education level: ")

    # Get crop details
    current_crop = input("What crop are you currently growing? (press Enter if none): ")
    planned_crop = input("What crop are you planning to grow? (press Enter if none): ")
    growth_stage = input(
        "What is the current growth stage? (e.g., sowing, flowering): "
    )

    # Get irrigation method
    irrigation = input(
        "What irrigation method do you use? (drip/sprinkler/manual/rain-fed): "
    )

    # Get soil conditions (optional)
    print("\nSoil Conditions (optional, press Enter to skip)")
    npk = input("NPK values (if known): ")
    ph = input("pH Level (if known): ")
    ph_level = float(ph) if ph and ph.replace(".", "", 1).isdigit() else None
    soil_type = input("Soil Type (if known): ")

    # Get fertilizer and pesticide information
    print("\nFertilizer and Pesticide (optional, press Enter to skip)")
    fert_type = input("Type and name: ")
    amount = input("Amount used: ")
    schedule = input("Application schedule: ")

    # Get farmer's query
    print("\nWhat is your concern or question?")
    query = input("> ")

    comments = input("\nAny additional comments? ")

    # Create and return the farmer input object
    return FarmerInput(
        name=name,
        location=location,
        demographic_info=DemographicInfo(
            age=age,
            gender=gender,
            education_level=education_level
        ),
        soil_conditions=SoilConditions(npk=npk, ph_level=ph_level, soil_type=soil_type),
        crop_details=CropDetails(
            current_crop=current_crop,
            planned_crop=planned_crop,
            growth_stage=growth_stage,
        ),
        irrigation_method=irrigation,
        fertilizer_pesticide=Fertilizers(
            type_used=fert_type, amount=amount, schedule=schedule
        ),
        query=query,
        comments=comments,
    )


async def get_weather_forecast_async(
    server_url: str, location: str, forecast_days: int = 3
) -> Dict[str, Any]:
    """Get weather forecast using the SSE weather client."""
    logger.info(f"Getting weather forecast for {location} via SSE")
    try:
        async with sse_client(server_url) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()

                # Call the get_weather tool with the provided arguments
                response = await session.call_tool(
                    "get_weather",
                    arguments={"city": location, "forecast_days": forecast_days},
                )

                # Extract the weather data from the response
                weather_data = extract_weather_data(response)

                # Optimize the data for LLM context
                optimized_data = optimize_weather_data_for_llm(weather_data)

                return optimized_data
    except Exception as e:
        logger.error(f"Error getting weather data via SSE: {e}")
        return {"error": str(e), "forecast": {}, "alerts": {}}


# Create a synchronous wrapper for the asynchronous function
def get_weather_forecast(client, location: str) -> Dict[str, Any]:
    """Synchronous wrapper for the asynchronous weather forecast function."""
    logger.info(f"Getting weather forecast for {location}")
    try:
        # Instead of using client.call, we'll use the async function
        # Extract the server URL from the client config
        server_url = list(client.config["mcpServers"].values())[0]["url"]

        # If the URL points to /mcp endpoint, change it to /sse for SSE transport
        if server_url.endswith("/mcp"):
            server_url = server_url.replace("/mcp", "/sse")

        # Run the async function
        return asyncio.run(get_weather_forecast_async(server_url, location, 3))
    except Exception as e:
        logger.error(f"Error getting weather data: {e}")
        return {"error": str(e), "forecast": {}, "alerts": {}}


async def query_agricultural_database_async(
    server_url: str, query: str, top_k: int = 3
) -> Dict[str, Any]:
    """Query the agricultural database using the SSE client."""
    logger.info(f"Querying agricultural database with: {query} via SSE")
    try:
        async with sse_client(server_url) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()

                # Call the query_book tool with the provided arguments
                response = await session.call_tool(
                    "query_book",
                    arguments={"query": query, "top_k": top_k},
                )

                # Extract the result
                if hasattr(response, "content") and response.content:
                    try:
                        # Try to parse the response as JSON if it's in text format
                        text_content = response.content[0].text
                        return json.loads(text_content)
                    except (AttributeError, IndexError, json.JSONDecodeError):
                        # If it's not in text format, return the raw result
                        return response.result

                return {"error": "No content in response", "matches": []}
    except Exception as e:
        logger.error(f"Error querying document database via SSE: {e}")
        return {"error": str(e), "matches": []}


def query_agricultural_database(client, query: str, top_k: int = 3) -> Dict[str, Any]:
    """Query the agricultural database using the RAG MCP server"""
    logger.info(f"Querying agricultural database with: {query}")
    try:
        # Extract the server URL from the client config
        server_config = next(iter(client.config["mcpServers"].values()))
        server_url = server_config["url"]

        # If the URL points to /mcp endpoint, change it to /sse for SSE transport
        if not server_url.endswith("/sse"):
            base_url = server_url.rsplit("/", 1)[0]
            server_url = f"{base_url}/sse"
            logger.info(f"Adjusted RAG server URL to SSE endpoint: {server_url}")

        # Run the async function
        return asyncio.run(query_agricultural_database_async(server_url, query, top_k))
    except Exception as e:
        logger.error(f"Error querying document database: {e}")
        return {"error": str(e), "matches": []}


def generate_llm_response(prompt: str, model, tokenizer) -> str:
    """Generate a response using the AgriQBot model"""
    logger.info("Generating LLM response")
    try:
        input_ids = tokenizer.encode(prompt, return_tensors="pt")
        generation_params = LLM_CONFIG["generation_params"]
        output_ids = model.generate(input_ids, **generation_params)
        response = tokenizer.decode(output_ids[0], skip_special_tokens=True)
        return response
    except Exception as e:
        logger.error(f"Error generating LLM response: {e}")
        return "I'm sorry, I encountered a problem generating a response. Please try again."


def format_farmer_input_for_rag(farmer_input: FarmerInput) -> str:
    """Create a query string for the RAG system based on farmer input"""
    query_components = [farmer_input.query]

    if farmer_input.crop_details.current_crop:
        query_components.append(
            f"current crop: {farmer_input.crop_details.current_crop}"
        )

    if farmer_input.crop_details.growth_stage:
        query_components.append(
            f"growth stage: {farmer_input.crop_details.growth_stage}"
        )

    if farmer_input.soil_conditions.soil_type:
        query_components.append(f"soil type: {farmer_input.soil_conditions.soil_type}")

    return " ".join(query_components)


def main():
    """Main function to run the DSS Farmers Chatbot"""
    logger.info("Starting DSS Farmers Chatbot")

    # Initialize MCP clients from configuration
    clients = initialize_mcp_clients()
    weather_client = clients["weather-server"]
    rag_client = clients["document-rag-server"]

    # Load the model and tokenizer
    model, tokenizer = load_agriqbot_model()

    while True:
        try:
            # Get farmer input
            farmer_input = get_farmer_input()

            # Get weather data using the SSE-based implementation
            print(f"\nFetching weather data for {farmer_input.location}...")
            weather_data = get_weather_forecast(weather_client, farmer_input.location)

            # Log the size of the weather data
            logger.info(
                f"Retrieved weather data with {len(json.dumps(weather_data))} characters"
            )

            # Create RAG query
            rag_query = format_farmer_input_for_rag(farmer_input)

            # Get relevant book information
            print("Searching agricultural database for relevant information...")
            book_data = query_agricultural_database(rag_client, rag_query)

            # Create the comprehensive prompt for the LLM
            prompt = FarmerPromptTemplates.create_agricultural_advisor_prompt(
                farmer_query=farmer_input.query,
                location=farmer_input.location,
                crop_details={
                    "current_crop": farmer_input.crop_details.current_crop,
                    "planned_crop": farmer_input.crop_details.planned_crop,
                    "growth_stage": farmer_input.crop_details.growth_stage,
                },
                soil_details={
                    "npk": farmer_input.soil_conditions.npk,
                    "ph_level": farmer_input.soil_conditions.ph_level,
                    "soil_type": farmer_input.soil_conditions.soil_type,
                    "organic_carbon": farmer_input.soil_conditions.organic_carbon,
                    "moisture_content": farmer_input.soil_conditions.moisture_content,
                },
                weather_data=weather_data,
                book_data=book_data,
                additional_info={
                    "irrigation_method": farmer_input.irrigation_method,
                    "fertilizer_type": farmer_input.fertilizer_pesticide.type_used,
                    "fertilizer_amount": farmer_input.fertilizer_pesticide.amount,
                    "fertilizer_schedule": farmer_input.fertilizer_pesticide.schedule,
                    "comments": farmer_input.comments,
                },
            )

            # Generate the response
            print("\nGenerating personalized recommendation...")
            response = generate_llm_response(prompt, model, tokenizer)

            # Display the prompt and response
            print("\n===== Prompt =====\n")
            print(prompt)
            print("\n===== Recommendation =====\n")
            print(response)

            # Ask if the user wants to continue
            if input("\nDo you want to ask another question? (y/n): ").lower() != "y":
                break

        except KeyboardInterrupt:
            print("\nExiting the DSS Farmers Assistant...")
            break
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            print(f"\nAn error occurred: {e}")
            print("Please try again.")

    print("\nThank you for using the DSS Farmers Assistant!")


if __name__ == "__main__":
    main()
