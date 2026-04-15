from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app import __version__
from app.auth import require_api_key
from app.config import get_settings
from app.language_map import list_languages
from app.schemas import (
    DetectLanguageRequest,
    DetectLanguageResponse,
    HealthResponse,
    LanguagesResponse,
    LanguageInfo,
    TranslateHtmlRequest,
    TranslateHtmlResponse,
    TranslateRequest,
    TranslateResponse,
)
from app.services.engine import TranslationEngine, get_engine
from app.utils.language import LanguageDetectionError, UnsupportedLanguageError, detect_language

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=__version__,
    description=(
        "Universal Translation API for plain text and rendered HTML. "
        "Designed for integration from PHP, JavaScript, Python, and other languages via HTTP."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
def root() -> str:
    return """
    <html>
      <head><title>Universal Translator ML API</title></head>
      <body style="font-family: sans-serif; max-width: 800px; margin: 40px auto; line-height: 1.5;">
        <h1>Universal Translator ML API</h1>
        <p>API is running.</p>
        <ul>
          <li><a href="/docs">Swagger UI</a></li>
          <li><a href="/redoc">ReDoc</a></li>
          <li><a href="/health">Health</a></li>
          <li><a href="/languages">Languages</a></li>
        </ul>
      </body>
    </html>
    """


@app.get("/health", response_model=HealthResponse)
def health(engine: TranslationEngine = Depends(get_engine)) -> HealthResponse:
    return HealthResponse(
        provider=engine.provider_name,
        model_name=engine.model_name,
        model_loaded=engine.provider.is_model_loaded(),
    )


@app.get("/languages", response_model=LanguagesResponse)
def languages(engine: TranslationEngine = Depends(get_engine)) -> LanguagesResponse:
    items = [
        LanguageInfo(code=lang.code, label=lang.label, provider_code=lang.provider_code)
        for lang in list_languages()
    ]
    return LanguagesResponse(provider=engine.provider_name, total=len(items), languages=items)


@app.post("/detect-language", response_model=DetectLanguageResponse, dependencies=[Depends(require_api_key)])
def detect_language_route(payload: DetectLanguageRequest) -> DetectLanguageResponse:
    try:
        detected = detect_language(payload.text)
    except (LanguageDetectionError, UnsupportedLanguageError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return DetectLanguageResponse(detected_language=detected)


@app.post("/translate", response_model=TranslateResponse, dependencies=[Depends(require_api_key)])
def translate_route(
    payload: TranslateRequest,
    engine: TranslationEngine = Depends(get_engine),
) -> TranslateResponse:
    texts = payload.text if isinstance(payload.text, list) else [payload.text]
    try:
        result = engine.translate_texts(
            texts,
            source_lang=payload.source_lang,
            target_lang=payload.target_lang,
        )
    except (ValueError, RuntimeError, LanguageDetectionError, UnsupportedLanguageError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    translated: str | list[str]
    if isinstance(payload.text, list):
        translated = result.translated
    else:
        translated = result.translated[0] if result.translated else ""

    return TranslateResponse(
        provider=engine.provider_name,
        model_name=engine.model_name,
        source_lang=result.source_lang,
        target_lang=payload.target_lang,
        translated=translated,
        detected_source_lang=result.detected_source_lang,
        cache_hits=result.cache_hits,
        items_translated=len(texts),
    )


@app.post("/translate-html", response_model=TranslateHtmlResponse, dependencies=[Depends(require_api_key)])
def translate_html_route(
    payload: TranslateHtmlRequest,
    engine: TranslationEngine = Depends(get_engine),
) -> TranslateHtmlResponse:
    try:
        result = engine.translate_html(
            payload.html,
            source_lang=payload.source_lang,
            target_lang=payload.target_lang,
        )
    except (ValueError, RuntimeError, LanguageDetectionError, UnsupportedLanguageError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return TranslateHtmlResponse(
        provider=engine.provider_name,
        model_name=engine.model_name,
        source_lang=result.source_lang,
        target_lang=payload.target_lang,
        translated_html=result.translated_html,
        detected_source_lang=result.detected_source_lang,
        cache_hits=result.cache_hits,
        segments_translated=result.segments_translated,
    )
