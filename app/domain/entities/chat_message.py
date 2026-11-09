from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


@dataclass
class ChatMessage:
    id: str = field(default_factory=lambda: uuid4().hex)
    conversation_id: str = ""
    role: str = "user"
    content: str = ""
    sources: list = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict = field(default_factory=dict)
