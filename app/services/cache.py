from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import sqlite3
from threading import Lock


@dataclass(frozen=True)
class CacheItem:
    key: str
    translated_text: str


class TranslationCache:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._lock = Lock()
        self._ensure_db()

    @staticmethod
    def build_key(source_lang: str, target_lang: str, model_name: str, text: str) -> str:
        payload = f"{source_lang}\n{target_lang}\n{model_name}\n{text}".encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _ensure_db(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS translations (
                    cache_key TEXT PRIMARY KEY,
                    source_lang TEXT NOT NULL,
                    target_lang TEXT NOT NULL,
                    model_name TEXT NOT NULL,
                    source_text TEXT NOT NULL,
                    translated_text TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def get(self, key: str) -> str | None:
        with self._lock, self._connect() as conn:
            row = conn.execute(
                "SELECT translated_text FROM translations WHERE cache_key = ?",
                (key,),
            ).fetchone()
        return None if row is None else str(row["translated_text"])

    def set(
        self,
        *,
        key: str,
        source_lang: str,
        target_lang: str,
        model_name: str,
        source_text: str,
        translated_text: str,
    ) -> None:
        with self._lock, self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO translations (
                    cache_key, source_lang, target_lang, model_name,
                    source_text, translated_text, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    key,
                    source_lang,
                    target_lang,
                    model_name,
                    source_text,
                    translated_text,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
            conn.commit()
