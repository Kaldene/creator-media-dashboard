from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Вычисляем путь к корню проекта (на две папки выше, чем config.py)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"

class Settings(BaseSettings):
    jwt_algorithm: str = "HS256"
    jwt_secret_key: str
    hf_token: str | None = None

    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()