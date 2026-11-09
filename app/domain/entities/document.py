from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4


@dataclass
class Document:
    id: str = field(default_factory=lambda: uuid4().hex)
    name: str = ""
    file_type: str = ""
    content: str = ""
    file_path: Optional[str] = None
    pages: Optional[int] = None
    size: Optional[int] = None
    status: str = "UPLOADED"
    course_id: Optional[str] = None
    metadata: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
