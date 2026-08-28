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
        raw = self.CORS_ORIGINS.strip()
        origins: list[str] = []

        if raw.startswith("[") and raw.endswith("]"):
            import json
            try:
                parsed = json.loads(raw)
                items = [str(item) for item in parsed] if isinstance(parsed, list) else [raw]
            except Exception:
                items = raw.split(",")
        else:
            items = raw.split(",")

        for item in items:
            cleaned = item.strip().strip("'\"")
            if not cleaned:
                continue
            if cleaned == "*":
                if "*" not in origins:
                    origins.append("*")
                continue
            base_url = cleaned.rstrip("/")
            if base_url and base_url not in origins:
                origins.append(base_url)
            with_slash = f"{base_url}/"
            if with_slash not in origins:
                origins.append(with_slash)

        for env_var in ("VERCEL_URL", "VERCEL_PROJECT_PRODUCTION_URL"):
            val = os.getenv(env_var)
            if val:
                url = val if val.startswith("http") else f"https://{val}"
                base_url = url.rstrip("/")
                if base_url not in origins:
                    origins.append(base_url)
                with_slash = f"{base_url}/"
                if with_slash not in origins:
                    origins.append(with_slash)

        prod_frontend = "https://epfo-tan.vercel.app"
        if prod_frontend not in origins:
            origins.append(prod_frontend)
            origins.append(f"{prod_frontend}/")

        return origins



settings = Settings()
