from dataclasses import dataclass

@dataclass
class WeatherDetails:
    temperature: float
    humidity: float
    precipitation: float
    wind_speed: float
