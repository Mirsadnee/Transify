from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from app.config import Settings, get_settings
from app.language_map import get_language, normalize_language_code
from app.services.cache import TranslationCache
from app.services.providers import DummyProvider, LocalNLLBProvider, TranslationProvider
from app.utils.html import extract_translatable_segments
from app.utils.language import detect_language
from app.utils.text import is_blank, is_probably_non_linguistic, total_characters


@dataclass
class TextTranslationResult:
    translated: list[str]
    source_lang: str
    detected_source_lang: str | None
    cache_hits: int


@dataclass
class HtmlTranslationResult:
    translated_html: str
    source_lang: str
    detected_source_lang: str | None
    cache_hits: int
    segments_translated: int


class TranslationEngine:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.cache = TranslationCache(settings.cache_db_path)
        self.provider = self._build_provider(settings)

    @property
    def provider_name(self) -> str:
        return self.provider.provider_name

    @property
    def model_name(self) -> str:
        return self.provider.model_name

    @staticmethod
    def _build_provider(settings: Settings) -> TranslationProvider:
        if settings.provider == "dummy":
            return DummyProvider()
        if settings.provider == "local_nllb":
            return LocalNLLBProvider(settings)
        raise ValueError(f"Unsupported provider: {settings.provider}")

    def _validate_languages(self, source_lang: str, target_lang: str) -> tuple[str, str]:
        source_lang = normalize_language_code(source_lang)
        target_lang = normalize_language_code(target_lang)

        if source_lang != "auto" and get_language(source_lang) is None:
            raise ValueError(f"Unsupported source language: {source_lang}")
        if get_language(target_lang) is None:
            raise ValueError(f"Unsupported target language: {target_lang}")
        return source_lang, target_lang

    def _enforce_limits(self, texts: list[str]) -> None:
        if len(texts) > self.settings.max_items_per_request:
            raise ValueError(
                f"Too many items in one request. Maximum allowed is {self.settings.max_items_per_request}."
            )
        total_chars = total_characters(texts)
        if total_chars > self.settings.max_chars_per_request:
            raise ValueError(
                f"Request is too large. Maximum allowed is {self.settings.max_chars_per_request} characters."
            )

    def _detect_source_language(self, texts: list[str]) -> str:
        sample_parts: list[str] = []
        current_length = 0
        for text in texts:
            stripped = text.strip()
            if not stripped:
                continue
            sample_parts.append(stripped)
            current_length += len(stripped)
            if current_length >= 4000 or len(sample_parts) >= 20:
                break
        sample = "\n".join(sample_parts)
        if not sample:
            return self.settings.default_source_lang
        return detect_language(sample)

    def translate_texts(
        self,
        texts: list[str],
        *,
        source_lang: str,
        target_lang: str,
    ) -> TextTranslationResult:
        self._enforce_limits(texts)
        source_lang, target_lang = self._validate_languages(source_lang, target_lang)

        detected_source_lang: str | None = None
        if source_lang == "auto":
            detected_source_lang = self._detect_source_language(texts)
            source_lang = detected_source_lang

        if source_lang == target_lang:
            return TextTranslationResult(
                translated=texts[:],
                source_lang=source_lang,
                detected_source_lang=detected_source_lang,
                cache_hits=0,
            )

        results: list[str] = ["" for _ in texts]
        misses_indices: list[int] = []
        misses_texts: list[str] = []
        cache_hits = 0

        for index, text in enumerate(texts):
            if is_blank(text) or is_probably_non_linguistic(text):
                results[index] = text
                continue

            cache_key = self.cache.build_key(source_lang, target_lang, self.model_name, text)
            cached_value = self.cache.get(cache_key)
            if cached_value is not None:
                results[index] = cached_value
                cache_hits += 1
                continue

            misses_indices.append(index)
            misses_texts.append(text)

        if misses_texts:
            translated_misses = self.provider.translate_batch(
                misses_texts,
                source_lang=source_lang,
                target_lang=target_lang,
            )
            if len(translated_misses) != len(misses_texts):
                raise RuntimeError("Translation provider returned an unexpected number of results.")

            for index, source_text, translated_text in zip(
                misses_indices,
                misses_texts,
                translated_misses,
                strict=True,
            ):
                results[index] = translated_text
                cache_key = self.cache.build_key(source_lang, target_lang, self.model_name, source_text)
                self.cache.set(
                    key=cache_key,
                    source_lang=source_lang,
                    target_lang=target_lang,
                    model_name=self.model_name,
                    source_text=source_text,
                    translated_text=translated_text,
                )

        return TextTranslationResult(
            translated=results,
            source_lang=source_lang,
            detected_source_lang=detected_source_lang,
            cache_hits=cache_hits,
        )

    def translate_html(
        self,
        html: str,
        *,
        source_lang: str,
        target_lang: str,
    ) -> HtmlTranslationResult:
        self._enforce_limits([html])
        source_lang, target_lang = self._validate_languages(source_lang, target_lang)

        soup, segments = extract_translatable_segments(html, self.settings)
        if not segments:
            return HtmlTranslationResult(
                translated_html=str(soup),
                source_lang=source_lang,
                detected_source_lang=None,
                cache_hits=0,
                segments_translated=0,
            )

        detected_source_lang: str | None = None
        if source_lang == "auto":
            detected_source_lang = self._detect_source_language([segment.core for segment in segments])
            source_lang = detected_source_lang

        translation_result = self.translate_texts(
            [segment.core for segment in segments],
            source_lang=source_lang,
            target_lang=target_lang,
        )

        for segment, translated_text in zip(segments, translation_result.translated, strict=True):
            segment.node.replace_with(f"{segment.prefix_ws}{translated_text}{segment.suffix_ws}")

        return HtmlTranslationResult(
            translated_html=str(soup),
            source_lang=translation_result.source_lang,
            detected_source_lang=detected_source_lang or translation_result.detected_source_lang,
            cache_hits=translation_result.cache_hits,
            segments_translated=len(segments),
        )


@lru_cache(maxsize=1)
def get_engine() -> TranslationEngine:
    return TranslationEngine(get_settings())
