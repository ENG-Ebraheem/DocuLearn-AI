from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Document:
    name: str
    file_type: str
    content: str
    pages: Optional[int] = None
    size: Optional[int] = None
    metadata: dict = field(default_factory=dict)