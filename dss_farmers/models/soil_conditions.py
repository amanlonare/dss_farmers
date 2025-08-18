from dataclasses import dataclass
from typing import Optional


@dataclass
class SoilConditions:
    """Data class for soil condition parameters"""

    npk: Optional[str] = None
    ph_level: Optional[float] = None
    soil_type: Optional[str] = None
    organic_carbon: Optional[str] = None
    moisture_content: Optional[str] = None
