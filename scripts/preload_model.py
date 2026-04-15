from __future__ import annotations

from app.services.engine import get_engine


if __name__ == "__main__":
    engine = get_engine()
    provider = engine.provider
    if hasattr(provider, "_load_bundle"):
        provider._load_bundle()  # type: ignore[attr-defined]
    print(f"Provider: {engine.provider_name}")
    print(f"Model: {engine.model_name}")
    print(f"Loaded: {provider.is_model_loaded()}")
