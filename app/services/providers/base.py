from __future__ import annotations

from abc import ABC, abstractmethod


class TranslationProvider(ABC):
    provider_name: str = "base"
    model_name: str = "unknown"

    @abstractmethod
    def is_model_loaded(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def translate_batch(self, texts: list[str], source_lang: str, target_lang: str) -> list[str]:
        raise NotImplementedError
