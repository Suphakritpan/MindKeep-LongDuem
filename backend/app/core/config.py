"""Application settings loaded from environment (no secrets committed)."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database (PostgreSQL + pgvector) — source of truth + retrieval index
    database_url: str = "postgresql+psycopg://mindkeep:change_me@db:5432/mindkeep"

    # Auth
    jwt_secret: str = "change_me"
    jwt_expire_minutes: int = 720

    # Local AI (Ollama) — local-first, no external AI by default
    ollama_base_url: str = "http://ollama:11434"
    ollama_model: str = "llama3.1:8b"
    embedding_model: str = "nomic-embed-text"

    # Storage (StorageService) — local filesystem first
    storage_backend: str = "local"
    storage_local_path: str = "./private/uploads"


settings = Settings()
