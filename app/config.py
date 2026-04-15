from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from pydantic import BaseModel, Field
import os


class Settings(BaseModel):
    app_name: str = "Universal Translator ML API"
    app_version: str = "0.1.0"
    app_api_key: str | None = None

    provider: str = Field(default="local_nllb")
    model_name: str = Field(default="facebook/nllb-200-distilled-600M")
    model_device: str = Field(default="cpu")
    default_source_lang: str = Field(default="auto")
    default_target_lang: str = Field(default="en")

    cache_db_path: Path = Field(default=Path("data/translation_cache.sqlite3"))
    max_chars_per_request: int = Field(default=150_000)
    max_items_per_request: int = Field(default=500)
    html_skip_selectors: tuple[str, ...] = (
        "script",
        "style",
        "code",
        "pre",
        "textarea",
        "noscript",
        "svg",
        "math",
    )

    request_timeout_seconds: int = Field(default=120)

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            app_api_key=os.getenv("APP_API_KEY") or None,
            provider=os.getenv("TRANSLATION_PROVIDER", "local_nllb").strip().lower(),
            model_name=os.getenv("TRANSLATION_MODEL_NAME", "facebook/nllb-200-distilled-600M"),
            model_device=os.getenv("TRANSLATION_MODEL_DEVICE", "cpu"),
            default_source_lang=os.getenv("DEFAULT_SOURCE_LANG", "auto"),
            default_target_lang=os.getenv("DEFAULT_TARGET_LANG", "en"),
            cache_db_path=Path(os.getenv("CACHE_DB_PATH", "data/translation_cache.sqlite3")),
            max_chars_per_request=int(os.getenv("MAX_CHARS_PER_REQUEST", "150000")),
            max_items_per_request=int(os.getenv("MAX_ITEMS_PER_REQUEST", "500")),
            request_timeout_seconds=int(os.getenv("REQUEST_TIMEOUT_SECONDS", "120")),
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings.from_env()
    settings.cache_db_path.parent.mkdir(parents=True, exist_ok=True)
    return settings
