from dataclasses import dataclass
from typing import Optional


@dataclass
class Category:
    name: str
    id: Optional[int] = None
