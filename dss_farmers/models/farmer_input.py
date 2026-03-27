from dataclasses import dataclass, field
from typing import Optional
from .soil_conditions import SoilConditions
from .crop_details import CropDetails
from .fertilizers import Fertilizers
from .weather_model import WeatherModel


@dataclass
class FarmerInput:
    """Main data class that contains all farmer input data"""

    location: str
    soil_conditions: SoilConditions = field(default_factory=SoilConditions)
    crop_details: CropDetails = field(default_factory=CropDetails)
    irrigation_method: Optional[str] = None
    fertilizer_pesticide: Fertilizers = field(default_factory=Fertilizers)
    weather_model: WeatherModel = field(default_factory=WeatherModel)
    query: str = ""
    comments: Optional[str] = None
