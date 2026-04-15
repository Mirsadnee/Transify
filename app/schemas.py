from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field, field_validator


class TranslateRequest(BaseModel):
    text: str | list[str] = Field(..., description="Text or list of texts to translate")
    source_lang: str = Field(default="auto", min_length=2, max_length=32)
    target_lang: str = Field(..., min_length=2, max_length=32)

    @field_validator("source_lang", "target_lang")
    @classmethod
    def normalize_lang_code(cls, value: str) -> str:
        return value.strip().lower()


class TranslateResponse(BaseModel):
    provider: str
    model_name: str
    source_lang: str
    target_lang: str
    translated: str | list[str]
    detected_source_lang: str | None = None
    cache_hits: int = 0
    items_translated: int = 0


class TranslateHtmlRequest(BaseModel):
    html: str = Field(..., description="Rendered HTML to translate")
    source_lang: str = Field(default="auto", min_length=2, max_length=32)
    target_lang: str = Field(..., min_length=2, max_length=32)

    @field_validator("source_lang", "target_lang")
    @classmethod
    def normalize_lang_code(cls, value: str) -> str:
        return value.strip().lower()


class TranslateHtmlResponse(BaseModel):
    provider: str
    model_name: str
    source_lang: str
    target_lang: str
    translated_html: str
    detected_source_lang: str | None = None
    cache_hits: int = 0
    segments_translated: int = 0


class DetectLanguageRequest(BaseModel):
    text: str = Field(..., min_length=1)


class DetectLanguageResponse(BaseModel):
    detected_language: str


class HealthResponse(BaseModel):
    status: str = "ok"
    provider: str
    model_name: str
    model_loaded: bool


class LanguageInfo(BaseModel):
    code: str
    label: str
    provider_code: str


class LanguagesResponse(BaseModel):
    provider: str
    total: int
    languages: list[LanguageInfo]


class ErrorResponse(BaseModel):
    detail: str
    meta: dict[str, Any] | None = None
