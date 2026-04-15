from __future__ import annotations

import requests

API_BASE = "http://127.0.0.1:8000"
API_KEY = ""  # optional


def headers() -> dict[str, str]:
    values = {"Content-Type": "application/json"}
    if API_KEY:
        values["X-API-Key"] = API_KEY
    return values


def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    response = requests.post(
        f"{API_BASE}/translate",
        headers=headers(),
        json={
            "text": text,
            "source_lang": source_lang,
            "target_lang": target_lang,
        },
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["translated"]


def translate_html(html: str, source_lang: str, target_lang: str) -> str:
    response = requests.post(
        f"{API_BASE}/translate-html",
        headers=headers(),
        json={
            "html": html,
            "source_lang": source_lang,
            "target_lang": target_lang,
        },
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["translated_html"]


if __name__ == "__main__":
    print(translate_text("Mirë se vini në faqen time", "sq", "en"))
    print(translate_html("<h1>Mirë se vini</h1><p>Kjo është faqja ime.</p>", "sq", "en"))
