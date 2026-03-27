from dataclasses import dataclass
from typing import Optional


@dataclass
class WeatherModel:
    """Weather data model for agricultural decision support"""
    temperature: float = 0.0  # Temperature in degrees Celsius
    humidity: float = 0.0  # Humidity percentage (0-100)
    precipitation: float = 0.0  # Precipitation amount in mm
    wind_speed: float = 0.0  # Wind speed in km/h
    forecast: str = "No forecast available"  # Weather forecast description
