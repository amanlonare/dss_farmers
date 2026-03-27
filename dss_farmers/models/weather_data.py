from dataclasses import dataclass
from typing import Optional


@dataclass
class WeatherData:
    """Weather data model for farmer decision support"""
    temperature_c: float
    humidity_percent: float
    precipitation_mm: float
    wind_speed_kmh: float
    weather_condition: str
    forecast_days: int
    is_severe_alert: bool
