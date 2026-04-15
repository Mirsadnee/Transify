from __future__ import annotations

from app.language_map import get_language, normalize_language_code


class LanguageDetectionError(RuntimeError):
    pass


class UnsupportedLanguageError(RuntimeError):
    pass


def detect_language(text: str) -> str:
    """
    Detect a language code and normalize it to the API's short language codes.
    Requires the optional `langdetect` package at runtime.
    """
    try:
        from langdetect import detect  # type: ignore
    except ImportError as exc:  # pragma: no cover - runtime dependency
        raise LanguageDetectionError(
            "Automatic language detection requires the `langdetect` package. "
            "Install dependencies from requirements.txt or set source_lang explicitly."
        ) from exc

    try:
        code = normalize_language_code(detect(text))
    except Exception as exc:  # pragma: no cover - third-party internals
        raise LanguageDetectionError("Unable to detect the source language for this text.") from exc

    if not get_language(code):
        raise UnsupportedLanguageError(
            f"Detected language '{code}' is not in the configured language map."
        )
    return code
