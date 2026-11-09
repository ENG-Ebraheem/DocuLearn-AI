from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Session,
    sessionmaker,
)

from app.config.settings import settings


def _ensure_sqlite_dir(url: str) -> None:
    if url.startswith("sqlite:///"):
        db_path_str = url[10:]
        if db_path_str and db_path_str != ":memory:":
            Path(db_path_str).parent.mkdir(parents=True, exist_ok=True)


_ensure_sqlite_dir(settings.database_url)


class Base(DeclarativeBase):
    pass


engine = create_engine(
    settings.database_url,
    echo=False,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


def get_session() -> Session:
    return SessionLocal()


def init_db() -> None:
    from app.infrastructure.database.models import (
        document_model,
        chunk_model,
        conversation_model,
        chat_message_model,
        learning_models,
        course_model,
    )

    Base.metadata.create_all(bind=engine)
