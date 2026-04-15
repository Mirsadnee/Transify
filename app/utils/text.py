from __future__ import annotations

import re
from typing import Iterable


PUNCT_OR_DIGITS_RE = re.compile(r"^[\W\d_]+$", re.UNICODE)
URL_RE = re.compile(r"^(https?://|www\.)", re.IGNORECASE)


def is_blank(value: str) -> bool:
    return not value or not value.strip()


def split_edge_whitespace(value: str) -> tuple[str, str, str]:
    match = re.match(r"^(\s*)(.*?)(\s*)$", value, re.DOTALL)
    if not match:
        return "", value, ""
    return match.group(1), match.group(2), match.group(3)


def is_probably_non_linguistic(value: str) -> bool:
    stripped = value.strip()
    if not stripped:
        return True
    if URL_RE.match(stripped):
        return True
    if PUNCT_OR_DIGITS_RE.fullmatch(stripped):
        return True
    if stripped.startswith("{{") and stripped.endswith("}}"):
        return True
    if stripped.startswith("<?") and stripped.endswith("?>"):
        return True
    return False


def total_characters(items: Iterable[str]) -> int:
    return sum(len(item) for item in items)
