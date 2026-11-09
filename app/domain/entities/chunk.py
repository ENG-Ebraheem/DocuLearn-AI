from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4


@dataclass
class Chunk:
    id: str = field(default_factory=lambda: uuid4().hex)
    document_id: str = ""
    content: str = ""
    chunk_index: int = 0
    metadata: dict = field(default_factory=dict)
    embedding_id: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
