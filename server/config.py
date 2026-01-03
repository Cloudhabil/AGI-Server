"""Application configuration using Pydantic settings.

For CI/tests, `.env.local` can inject many unrelated keys. To avoid
validation errors from extra keys, loading of the dotenv file is opt-in via
`LOAD_DOTENV=1`.
"""

import os
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Config values loaded from environment or ``.env.local``.

    Unknown environment keys are ignored to avoid failures on CI runners
    that inject unrelated variables (e.g., ``APP_ENV``).
    """

    API_PORT: int = 8000
    CORS_ORIGINS: List[str] = ["http://localhost:5173"]
    REDIS_URL: str = "redis://localhost:6379/0"
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/cloudhabil"
    API_TOKEN: str = "dev-token"

    # Accept but ignore common environment knobs not used by the app.
    APP_ENV: Optional[str] = None
    app_env: Optional[str] = None

    _env_file = ".env.local" if os.getenv("LOAD_DOTENV", "0").lower() in ("1", "true", "yes", "on") else None

    model_config = SettingsConfigDict(
        env_file=_env_file,
        env_file_encoding="utf-8",
        extra="allow",
        case_sensitive=False,
    )


settings = Settings()
