from typing import Dict, Any


class FarmerPromptTemplates:
    """Collection of prompt templates for farmer-related interactions"""

    @staticmethod
    def create_agricultural_advisor_prompt(
        farmer_query: str,
        location: str,
        crop_details: Dict[str, Any],
        soil_details: Dict[str, Any],
        weather_data: Dict[str, Any],
        book_data: Dict[str, Any],
        additional_info: Dict[str, Any] = None,
    ) -> str:
        """
        Create a comprehensive prompt for the agricultural advisor model

        Args:
            farmer_query: The main question or concern from the farmer
            location: The farmer's location
            crop_details: Details about crops (current, planned, stage)
            soil_details: Soil condition information
            weather_data: Weather forecast and alerts
            book_data: Relevant information from agricultural resources
            additional_info: Any other relevant information

        Returns:
            A formatted prompt string
        """
        # Format weather data
        weather_section = "No weather data available."
        if "forecast" in weather_data and "forecastday" in weather_data["forecast"]:
            forecast_days = weather_data["forecast"]["forecastday"]
            weather_section = "Weather Forecast:\n"
            for day in forecast_days:
                date = day.get("date", "Unknown date")
                condition = (
                    day.get("day", {}).get("condition", {}).get("text", "Unknown")
                )
                max_temp = day.get("day", {}).get("maxtemp_c", "Unknown")
                min_temp = day.get("day", {}).get("mintemp_c", "Unknown")
                rain_chance = day.get("day", {}).get("daily_chance_of_rain", "Unknown")

                weather_section += f"- {date}: {condition}, Temp: {min_temp}°C to {max_temp}°C, Rain chance: {rain_chance}%\n"

        # Format alerts
        alerts_section = "No weather alerts."
        if (
            "alerts" in weather_data
            and "alert" in weather_data["alerts"]
            and weather_data["alerts"]["alert"]
        ):
            alerts = weather_data["alerts"]["alert"]
            alerts_section = "Weather Alerts:\n"
            for alert in alerts:
                event = alert.get("event", "Unknown alert")
                desc = alert.get("desc", "No description")
                alerts_section += f"- {event}: {desc}\n"

        # Format book information
        book_section = "No relevant information found in our agricultural guide."
        if "matches" in book_data and book_data["matches"]:
            book_section = "Relevant agricultural information:\n"
            for i, match in enumerate(book_data["matches"], 1):
                text = match.get("text", "No text")
                source = match.get("source", "Unknown source")
                book_section += f"Reference {i} from {source}:\n{text}\n\n"

        # Format soil conditions
        soil_section = "Soil Conditions:"
        for key, value in soil_details.items():
            if value:
                formatted_key = key.replace("_", " ").title()
                soil_section += f"\n- {formatted_key}: {value}"

        # Format crop details
        crop_section = "Crop Information:"
        for key, value in crop_details.items():
            if value:
                formatted_key = key.replace("_", " ").title()
                crop_section += f"\n- {formatted_key}: {value}"

        # Format additional info
        other_info = ""
        if additional_info:
            for key, value in additional_info.items():
                if value:
                    formatted_key = key.replace("_", " ").title()
                    other_info += f"{formatted_key}: {value}\n"

        # Create the final prompt
        prompt = f"""You are an agricultural expert assistant. A farmer from {location} has a question or concern.
Please provide helpful, practical advice based on the following information:

FARMER'S QUESTION:
{farmer_query}

{crop_section}

{soil_section}

{other_info}

{weather_section}

{alerts_section}

{book_section}

Based on all this information, please provide detailed, practical advice to help the farmer. 
Include specific recommendations for actions the farmer should take, considering the weather forecast, 
soil conditions, and crop details. If there are any risks or warnings based on the weather alerts, 
emphasize those.
"""
        return prompt

    @staticmethod
    def create_rag_query_prompt(
        farmer_query: str, crop_info: str = "", additional_context: str = ""
    ) -> str:
        """
        Create a prompt specifically for querying the RAG system

        Args:
            farmer_query: The farmer's question
            crop_info: Information about the crop (optional)
            additional_context: Any additional context (optional)

        Returns:
            A formatted prompt string for RAG queries
        """
        prompt = farmer_query

        if crop_info:
            prompt += f" Crop information: {crop_info}."

        if additional_context:
            prompt += f" Additional context: {additional_context}."

        return prompt
