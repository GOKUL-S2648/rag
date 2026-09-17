from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    GROQ_API_KEY: str
    JWT_SECRET: str
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"

    class Config:
        env_file = ".env"


settings = Settings()