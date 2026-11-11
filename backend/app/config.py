from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env", "../.env"), extra="ignore")

    database_url: str
    seed_rooms: list[str] = ["Room 1", "Room 2", "Room 3"]


settings = Settings()