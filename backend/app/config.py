from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env", "../.env"), extra="ignore")

    database_url: str
    seed_rooms: list[str] = ["Room 1", "Room 2", "Room 3"]
    warn_below_c: float = 18.0
    critical_below_c: float = 16.0
    clear_deadband_c: float = 0.5


settings = Settings()