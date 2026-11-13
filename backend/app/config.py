from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env", "../.env"), extra="ignore")

    database_url: str
    seed_rooms: list[str] = ["Room 1", "Room 2", "Room 3"]
    warn_below_c: float = 18.0
    critical_below_c: float = 16.0
    clear_deadband_c: float = 0.5
    heater_escalate_after_s: int = 30
    heater_min_rise_c: float = 0.5
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 480
    device_api_key: str
    seed_staff_username: str | None = None
    seed_staff_password: str | None = None
    login_max_failures: int = 5
    login_window_s: int = 300
    cors_origins: list[str] = []
    app_db_user: str | None = None
    app_db_password: str | None = None


settings = Settings()