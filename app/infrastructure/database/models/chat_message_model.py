import json
from datetime import datetime, timezone

from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.database import Base


class ChatMessageModel(Base):
    __tablename__ = "chat_messages"

    id: Mapped[str] = mapped_column(
        String(32), primary_key=True
    )
    conversation_id: Mapped[str] = mapped_column(
        String(32), index=True
    )
    role: Mapped[str] = mapped_column(String(20))
    content: Mapped[str] = mapped_column(Text)
    sources_json: Mapped[str] = mapped_column(
        Text, default="[]"
    )
    extra_json: Mapped[str] = mapped_column(
        Text, default="{}", name="metadata_json"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )

    @property
    def sources(self) -> list:
        return json.loads(self.sources_json)

    @sources.setter
    def sources(self, value: list) -> None:
        self.sources_json = json.dumps(value)

    @property
    def extra_metadata(self) -> dict:
        return json.loads(self.extra_json)

    @extra_metadata.setter
    def extra_metadata(self, value: dict) -> None:
        self.extra_json = json.dumps(value)
