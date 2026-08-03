from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="TOKTRADE_")
    cors_origins: str = (
        "http://localhost:3000,http://localhost:3001,http://localhost:5173,https://tokmarket-front.vercel.app"
    )
    refresh_hours: int = 24

    @property
    def origins(self) -> list[str]:
        if not self.cors_origins:
            return ["*"]
        items = [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
        return items if items else ["*"]


@lru_cache
def get_settings() -> Settings:
    return Settings()

