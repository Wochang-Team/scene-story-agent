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
    def postgres_connection_kwargs(self) -> dict[str, str | int]:
        return {
            "dbname": self.postgres_db,
            "user": self.postgres_user,
            "password": self.postgres_password,
            "host": self.postgres_host,
            "port": self.postgres_port,
        }

    @property
    def postgres_log_environment(self) -> dict[str, str | int]:
        return {
            "POSTGRES_DB": self.postgres_db,
            "POSTGRES_USER": self.postgres_user,
            "POSTGRES_PASSWORD": (
                "[configured]" if self.postgres_password else "[not configured]"
            ),
            "POSTGRES_HOST": self.postgres_host,
            "POSTGRES_PORT": self.postgres_port,
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()
