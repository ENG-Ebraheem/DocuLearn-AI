import json
from datetime import datetime, timezone

from sqlalchemy import String, Text, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.database import Base


class DocumentModel(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(
        String(32), primary_key=True
    )
    name: Mapped[str] = mapped_column(String(255))
    file_type: Mapped[str] = mapped_column(String(10))
    file_path: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )
    pages: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    size: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(20), default="UPLOADED"
    )
    course_id: Mapped[str | None] = mapped_column(
        String(32), nullable=True, index=True
    )
    extra_json: Mapped[str] = mapped_column(
        Text, default="{}", name="metadata_json"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    @property
    def extra_metadata(self) -> dict:
        return json.loads(self.extra_json)

    @extra_metadata.setter
    def extra_metadata(self, value: dict) -> None:
        self.extra_json = json.dumps(value)
