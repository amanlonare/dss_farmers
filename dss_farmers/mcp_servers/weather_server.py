import requests
import os
import logging
from dotenv import load_dotenv

import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Route, Mount

from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport

# Load environment variables once
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("weather-app")

# Create MCP server instance
mcp = FastMCP("weather-app", host="127.0.0.1", port=8000)


@mcp.tool()
def get_weather(city: str, forecast_days: int = 1):
    """
    Get the weather for a given city
    """
    api_key = os.getenv("WEATHER_API")
    if not api_key:
        logger.error("WEATHER_API key not found in environment variables.")
        return {"error": "API key missing"}

    if not city:
        logger.error("City parameter is required.")
        return {"error": "City parameter is required"}

    url = (
        f"http://api.weatherapi.com/v1/forecast.json"
        f"?key={api_key}&q={city}&days={forecast_days}&aqi=no&alerts=yes"
    )
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        # Only return forecast and alerts
        return {"forecast": data.get("forecast", {}), "alerts": data.get("alerts", {})}
    except requests.RequestException as e:
        logger.error(f"Could not load the data: {e}")
        return {"error": "Failed to fetch weather data"}


# Set up the SSE transport for MCP communication
sse = SseServerTransport("/messages/")


async def handle_sse(request: Request) -> None:
    """Handle SSE connections from clients"""
    _server = mcp._mcp_server
    async with sse.connect_sse(
        request.scope,
        request.receive,
        request._send,
    ) as (reader, writer):
        await _server.run(reader, writer, _server.create_initialization_options())


# Create the Starlette app with multiple endpoints
app = Starlette(
    debug=True,
    routes=[
        # SSE endpoint for clients that use SSE transport
        Route("/sse", endpoint=handle_sse),
        Mount("/messages/", app=sse.handle_post_message),
        # The regular MCP endpoint remains at /mcp
        # This is handled internally by FastMCP
    ],
)


if __name__ == "__main__":
    # This runs both the streamable-http transport (at /mcp) and the SSE transport
    port = int(os.getenv("PORT", "8000"))
    logger.info(f"Starting weather server on port {port}")

    # Run the app with uvicorn
    uvicorn.run(app, host="127.0.0.1", port=port)
