from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class DjangoSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env')

    DEBUG: bool
    SECRET_KEY: str

    SOCIAL_AUTH_GITHUB_KEY: str
    SOCIAL_AUTH_GITHUB_SECRET: str


class PostgresSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='postgres.env')

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

@lru_cache
def get_django_settings() -> DjangoSettings:
    return DjangoSettings() # type: ignore

@lru_cache
def get_postgres_settings() -> PostgresSettings:
    return PostgresSettings() # type: ignore

