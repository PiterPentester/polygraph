from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str = ""
    bot_username: str = ""
    assets_dir: Path = Path("assets")
    log_level: str = "INFO"

    # Webhook optional configs for k8s / production
    webhook_mode: bool = False
    webhook_url: str = ""
    webhook_path: str = "/webhook"
    host: str = "0.0.0.0"
    port: int = 8080

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
