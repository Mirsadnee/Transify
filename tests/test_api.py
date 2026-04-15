from __future__ import annotations

import importlib

from fastapi.testclient import TestClient


def build_client(tmp_path, monkeypatch) -> TestClient:
    monkeypatch.setenv("TRANSLATION_PROVIDER", "dummy")
    monkeypatch.setenv("CACHE_DB_PATH", str(tmp_path / "cache.sqlite3"))
    monkeypatch.delenv("APP_API_KEY", raising=False)

    from app.config import get_settings
    from app.services.engine import get_engine

    get_settings.cache_clear()
    get_engine.cache_clear()

    main = importlib.import_module("app.main")
    main = importlib.reload(main)
    return TestClient(main.app)


def test_health_endpoint(tmp_path, monkeypatch):
    client = build_client(tmp_path, monkeypatch)
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["provider"] == "dummy"


def test_translate_text(tmp_path, monkeypatch):
    client = build_client(tmp_path, monkeypatch)
    response = client.post(
        "/translate",
        json={
            "text": "Mirë se vini",
            "source_lang": "sq",
            "target_lang": "en",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["translated"] == "[en] Mirë se vini"
    assert payload["items_translated"] == 1


def test_translate_html_preserves_no_translate_nodes(tmp_path, monkeypatch):
    client = build_client(tmp_path, monkeypatch)
    response = client.post(
        "/translate-html",
        json={
            "html": '<h1>Mirë se vini</h1><div translate="no">BrandName</div>',
            "source_lang": "sq",
            "target_lang": "en",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert "[en] Mirë se vini" in payload["translated_html"]
    assert "BrandName" in payload["translated_html"]
    assert "[en] BrandName" not in payload["translated_html"]


def test_cache_hits_on_second_request(tmp_path, monkeypatch):
    client = build_client(tmp_path, monkeypatch)
    request_body = {
        "text": "Kjo është një fjali.",
        "source_lang": "sq",
        "target_lang": "en",
    }
    first = client.post("/translate", json=request_body)
    second = client.post("/translate", json=request_body)

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["cache_hits"] == 0
    assert second.json()["cache_hits"] == 1
