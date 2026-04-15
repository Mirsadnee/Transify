from __future__ import annotations

from dataclasses import dataclass
from bs4 import BeautifulSoup, NavigableString, Tag

from app.config import Settings
from app.utils.text import is_probably_non_linguistic, split_edge_whitespace


@dataclass
class HtmlSegment:
    node: NavigableString
    original: str
    prefix_ws: str
    core: str
    suffix_ws: str


def _has_no_translate_ancestor(node: NavigableString) -> bool:
    parent = node.parent
    while isinstance(parent, Tag):
        if parent.get("translate") == "no":
            return True
        classes = set(parent.get("class", []))
        if {"notranslate", "no-translate", "skip-translate"} & classes:
            return True
        if parent.attrs.get("data-no-translate") is not None:
            return True
        parent = parent.parent
    return False


def _is_skipped_parent(node: NavigableString, settings: Settings) -> bool:
    parent = node.parent
    if not isinstance(parent, Tag):
        return False
    return parent.name in settings.html_skip_selectors


def extract_translatable_segments(html: str, settings: Settings) -> tuple[BeautifulSoup, list[HtmlSegment]]:
    soup = BeautifulSoup(html, "html.parser")
    segments: list[HtmlSegment] = []

    for node in soup.find_all(string=True):
        if not isinstance(node, NavigableString):
            continue
        if _is_skipped_parent(node, settings):
            continue
        if _has_no_translate_ancestor(node):
            continue

        original = str(node)
        prefix_ws, core, suffix_ws = split_edge_whitespace(original)
        if is_probably_non_linguistic(core):
            continue

        segments.append(
            HtmlSegment(
                node=node,
                original=original,
                prefix_ws=prefix_ws,
                core=core,
                suffix_ws=suffix_ws,
            )
        )

    return soup, segments
