from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    GEMINI_API_KEY: str = ""
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/wikiquiz"
    ALLOWED_ORIGINS: str = "http://127.0.0.1:5500,http://localhost:5500"

    @property
    def allowed_origins_list(self):
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()