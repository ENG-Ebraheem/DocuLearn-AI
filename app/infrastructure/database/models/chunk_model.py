import json
from datetime import datetime, timezone

from sqlalchemy import String, Text, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.database import Base


class ChunkModel(Base):
    __tablename__ = "chunks"

    id: Mapped[str] = mapped_column(
        String(32), primary_key=True
    )
    document_id: Mapped[str] = mapped_column(
        String(32), index=True
    )
    content: Mapped[str] = mapped_column(Text)
    chunk_index: Mapped[int] = mapped_column(Integer)
    extra_json: Mapped[str] = mapped_column(
        Text, default="{}", name="metadata_json"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )

    @property
    def extra_metadata(self) -> dict:
        return json.loads(self.extra_json)

    @extra_metadata.setter
    def extra_metadata(self, value: dict) -> None:
        self.extra_json = json.dumps(value)
