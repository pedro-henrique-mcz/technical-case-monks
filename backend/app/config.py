from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str 
    cors_origins: str


settings = Settings()