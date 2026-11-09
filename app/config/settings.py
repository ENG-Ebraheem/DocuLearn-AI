from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "DocuLearn AI"
    environment: str = "development"

    database_url: str = "sqlite:///data/app.db"

    uploads_dir: str = "data/uploads"
    vector_store_path: str = "data/vector_store"

    embedding_model: str = "all-MiniLM-L6-v2"

    llm_provider: str = "gemini"
    llm_model: str = "gemini-3.5-flash"
    gemini_api_key: str = ""

    chunk_size: int = 1000
    chunk_overlap: int = 150

    top_k: int = 5
    rag_min_context_score: float = 0.42

    max_upload_size_mb: int = 50
    allowed_extensions: list[str] = [".pdf", ".docx", ".xlsx", ".txt"]
    log_level: str = "INFO"

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    @property
    def api_key(self) -> str:
        return self.gemini_api_key

    @property
    def is_api_key_configured(self) -> bool:
        return bool(self.api_key and self.api_key.strip())

    @property
    def uploads_path(self) -> Path:
        path = Path(self.uploads_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def vector_store_path_obj(self) -> Path:
        path = Path(self.vector_store_path)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def validate_startup(self) -> bool:
        """Validate production configuration paths and return readiness status."""
        self.uploads_path
        self.vector_store_path_obj
        return True


settings = Settings()

