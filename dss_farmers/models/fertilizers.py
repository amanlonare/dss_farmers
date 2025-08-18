from dataclasses import dataclass
from typing import Optional


@dataclass
class Fertilizers:
    """Data class for fertilizer and pesticide information"""

    type_used: Optional[str] = None
    amount: Optional[str] = None
    schedule: Optional[str] = None
