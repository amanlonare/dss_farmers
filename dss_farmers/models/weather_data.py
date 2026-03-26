from dataclasses import dataclass
from typing import List

@dataclass
class WeatherData:
    temperature: float
    humidity: float
    precipitation: float
    wind_speed: float
    pressure: float
    uv_index: float
    forecast_7day: List[dict]
