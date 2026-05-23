from typing import Optional
import os

from pydantic import BaseModel


class Settings(BaseModel):
    DB_URI: Optional[str] = None
    DB_DIALECT: str = "postgresql"
    DB_USER: str = ""
    DB_PASSWORD: str = ""
    DB_HOST: str = "localhost"
    DB_NAME: str = ""
    DB_PORT: int = 5432
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    OPENAI_TEMPERATURE: float = 0.0


def get_settings() -> Settings:
    return Settings(
        DB_URI=os.getenv("DB_URI") or None,
        DB_DIALECT=os.getenv("DB_DIALECT", "postgresql"),
        DB_USER=os.getenv("DB_USER", ""),
        DB_PASSWORD=os.getenv("DB_PASSWORD", ""),
        DB_HOST=os.getenv("DB_HOST", "localhost"),
        DB_NAME=os.getenv("DB_NAME", ""),
        DB_PORT=int(os.getenv("DB_PORT", "5432")),
        OPENAI_MODEL=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
        OPENAI_TEMPERATURE=float(os.getenv("OPENAI_TEMPERATURE", "0.0")),
    )
