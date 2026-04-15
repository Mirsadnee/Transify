from __future__ import annotations

from app.services.providers.base import TranslationProvider


class DummyProvider(TranslationProvider):
    provider_name = "dummy"
    model_name = "dummy-echo-model"

    def is_model_loaded(self) -> bool:
        return True

    def translate_batch(self, texts: list[str], source_lang: str, target_lang: str) -> list[str]:
        return [f"[{target_lang}] {text}" for text in texts]
