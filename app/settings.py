from functools import lru_cache
import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = os.getenv("ENV_FILE", ".env.local")

load_dotenv(ENV_FILE)


class Settings(BaseSettings):
    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_host: str = "127.0.0.1"
    postgres_port: int = 5432
    redis_host: str = "127.0.0.1"
    redis_port: int = 6379
    local_storage_root: str = ".local_storage"
    local_storage_bucket: str = "local"
    local_file_max_bytes: int = 50 * 1024 * 1024
    ai_provider: str = "mock"
    ai_model: str = "mock-scene-v1"
    ai_timeout_seconds: int = 30
    ai_max_retries: int = 2
    ai_image_max_bytes: int = 5 * 1024 * 1024
    embedding_provider: str = "mock"
    embedding_model: str = "mock-embedding-v1"
    embedding_dimension: int = 8
    openai_api_key: str | None = None
    gemini_api_key: str | None = None
    similar_records_limit: int = 5
    similarity_threshold: float = 0.70

    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    @property
    def postgres_dsn(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
