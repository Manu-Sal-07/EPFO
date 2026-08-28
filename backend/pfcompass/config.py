import os
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    LOG_LEVEL: str = "INFO"

    DATABASE_URL: str = "postgresql+asyncpg://pfcompass:changeme@localhost:5432/pfcompass"
    REDIS_URL: str = "redis://:changeme@localhost:6379/0"

    SECRET_KEY: str = "dev-secret-key-replace-in-production-must-be-long-and-secure"
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 900  # 15 minutes
    REFRESH_TOKEN_EXPIRE_SECONDS: int = 604800  # 7 days

    LLM_PROVIDER: Literal["groq", "openai"] = "groq"
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"

    SEED_DEMO: bool = True
    CORS_ORIGINS: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        origins = [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
        for env_var in ("VERCEL_URL", "VERCEL_PROJECT_PRODUCTION_URL"):
            val = os.getenv(env_var)
            if val:
                url = val if val.startswith("http") else f"https://{val}"
                if url not in origins:
                    origins.append(url)
        return origins


settings = Settings()
