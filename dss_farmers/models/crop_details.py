from dataclasses import dataclass
from typing import Optional


@dataclass
class CropDetails:
    """Data class for crop information"""

    current_crop: Optional[str] = None
    planned_crop: Optional[str] = None
    growth_stage: Optional[str] = None
