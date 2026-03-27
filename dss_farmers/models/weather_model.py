from dataclasses import dataclass
from typing import Optional


@dataclass
class WeatherModel:
    """Weather data model for agricultural decision support"""
    temperature: float  # Temperature in degrees Celsius
    humidity: float  # Humidity percentage (0-100)
    precipitation: float  # Precipitation amount in mm
    wind_speed: float  # Wind speed in km/h
    forecast: str  # Weather forecast description
