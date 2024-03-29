import sys
sys.path.append("/home/yyy/Desktop/app_with_git/app")

from typing import Any, Optional
from pydantic import PostgresDsn, field_validator, ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict

def database_uri_make_validator():
    def database_uri_validator(value: Any, info: ValidationInfo):
        return PostgresDsn.build(
            scheme="postgresql",
            username=info.data.get("POSTGRES_USER"),
            password=info.data.get("POSTGRES_PASSWORD"),  
            path=info.data.get("POSTGRES_DB"),
            host=info.data.get("POSTGRES_HOST"),
            port=info.data.get("POSTGRES_PORT")          
        )
    return database_uri_validator

class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    TOKEN: str

    DATABASE_URI: Optional[PostgresDsn] = None

    database_uri_validator = field_validator("DATABASE_URI", mode="before")(database_uri_make_validator())

    model_config = SettingsConfigDict(
        env_file="/home/yyy/Desktop/app_with_git/app/.env",
        # env_file="/usr/src/telegram_bot/database_drivers/.env",
        env_file_encoding="utf-8"
        )

settings = Settings()
