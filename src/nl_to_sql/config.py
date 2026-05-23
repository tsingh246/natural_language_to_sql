from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    DB_URI: Optional[str] = None
    DB_DIALECT: str = "postgresql"
    DB_USER: str = ""
    DB_PASSWORD: str = ""
    DB_HOST: str = "localhost"
    DB_NAME: str = ""
    DB_PORT: int = 5432
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    OPENAI_TEMPERATURE: float = 0.0

    class Config:
        env_file = ".env"


def get_settings() -> Settings:
    return Settings()
