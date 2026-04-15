from __future__ import annotations

from app.services.providers.base import TranslationProvider


class DeepTranslatorProvider(TranslationProvider):
    provider_name = "deep_translator"
    model_name = "google-web"

    _LANGUAGE_OVERRIDES: dict[str, str] = {
        "zh": "zh-CN",
        "zh-hant": "zh-TW",
    }

    def is_model_loaded(self) -> bool:
        # This provider uses a web translator and does not load a local model into memory.
        return True

    def _map_language(self, lang: str) -> str:
        normalized = lang.strip().lower()
        return self._LANGUAGE_OVERRIDES.get(normalized, normalized)

    def translate_batch(self, texts: list[str], source_lang: str, target_lang: str) -> list[str]:
        if not texts:
            return []

        source = "auto" if source_lang == "auto" else self._map_language(source_lang)
        target = self._map_language(target_lang)

        try:
            from deep_translator import GoogleTranslator
        except ImportError as exc:  # pragma: no cover - optional runtime dependency
            raise RuntimeError(
                "Deep translator provider requires `deep-translator`. Install dependencies from requirements.txt."
            ) from exc

        translator = GoogleTranslator(source=source, target=target)
        translated: list[str] = []
        for text in texts:
            translated.append(translator.translate(text))
        return translated
