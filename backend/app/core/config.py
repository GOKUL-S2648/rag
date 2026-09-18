import os
from pydantic_settings import BaseSettings
from groq import Groq


class Settings(BaseSettings):
    DATABASE_URL: str = ""
    GROQ_API_KEY: str = ""
    JWT_SECRET: str = "default-jwt-secret-key-change-in-env"
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"

    @property
    def sync_database_url(self) -> str:
        url = self.DATABASE_URL
        if not url:
            return ""
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()


def get_groq_client() -> Groq:
    api_key = settings.GROQ_API_KEY or os.getenv("GROQ_API_KEY") or "dummy_key_for_boot"
    return Groq(api_key=api_key)