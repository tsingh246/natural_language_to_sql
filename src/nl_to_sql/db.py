from typing import Optional
from urllib.parse import quote_plus

from langchain_community.utilities import SQLDatabase

from .config import Settings, get_settings


def create_db_connection(settings: Optional[Settings] = None) -> SQLDatabase:
    settings = settings or get_settings()
    if settings.DB_URI:
        uri = settings.DB_URI
    else:
        if not settings.DB_USER or not settings.DB_NAME:
            raise ValueError("Database user and database name are required.")

        dialect = settings.DB_DIALECT.strip().lower()
        user = quote_plus(settings.DB_USER)
        password = quote_plus(settings.DB_PASSWORD)
        host = settings.DB_HOST.strip() or "localhost"
        name = quote_plus(settings.DB_NAME)
        uri = f"{dialect}://{user}:{password}@{host}:{settings.DB_PORT}/{name}"

    return SQLDatabase.from_uri(uri)
