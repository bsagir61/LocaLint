from __future__ import annotations

import re


URL_RE = re.compile(r"^(https?://|www\.)\S+$", re.IGNORECASE)
NUMBER_RE = re.compile(r"^[\d\s.,:+\-/%]+$")
FILE_PATH_RE = re.compile(r"(^[A-Za-z]:\\|[/\\]|^[\w.-]+\.[A-Za-z0-9]{1,5}$)")
CODE_TOKEN_RE = re.compile(r"^[A-Z0-9_.:/\\-]+$")


def as_text(value: object) -> str:
    if value is None:
        return ""
    return str(value)


def is_blank(value: object) -> bool:
    return as_text(value).strip() == ""


def looks_non_localizable(value: str) -> bool:
    """Heuristic for strings that are expected to stay identical across locales."""
    text = value.strip()
    if not text:
        return True
    if len(text) <= 3:
        return True
    if URL_RE.match(text) or NUMBER_RE.match(text) or FILE_PATH_RE.search(text):
        return True
    if CODE_TOKEN_RE.match(text):
        return True
    if " " not in text and text[:1].isupper() and text[1:].islower():
        return True
    return False
