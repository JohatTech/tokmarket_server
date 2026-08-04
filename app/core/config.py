from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="TOKTRADE_")
<<<<<<< HEAD
    cors_origins: str = "http://localhost:3000,https://tokmarket-front.vercel.app,*"
=======
    cors_origins: str = "*"
>>>>>>> 9134695a30bd64a1dc049ca797971b053060dbe7
    refresh_hours: int = 24

    @property
    def origins(self) -> list[str]:
        if not self.cors_origins or self.cors_origins.strip() == "*":
            return ["*"]
        items = [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
        return items if items else ["*"]



@lru_cache
def get_settings() -> Settings:
    return Settings()

