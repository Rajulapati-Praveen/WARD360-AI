
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./ward360.db"

    SECRET_KEY: str
    DEVICE_API_KEY: str

    CORS_ORIGINS: str = (
        "http://localhost:5173,http://127.0.0.1:5173,"
        "http://localhost:5174,http://127.0.0.1:5174"
    )

    TOKEN_MINUTES: int = 480
    ESCALATION_SECONDS: int = 60
    DEVICE_TIMEOUT_SECONDS: int = 20
    ALERT_COOLDOWN_SECONDS: int = 120

    SIM_INTERVAL_SECONDS: float = 2.0
    DISABLE_BACKGROUND: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
