from dataclasses import dataclass, field
from typing import List, Optional

from .tag import Tag


@dataclass
class FileItem:
    name: str
    absolute_path: str
    extension: str
    id: Optional[int] = None

    category_id: Optional[int] = None
    tags: List[Tag] = field(default_factory=list)

    image_name: Optional[str] = None
    image_id: Optional[int] = None
