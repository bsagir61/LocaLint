from __future__ import annotations

import re
from collections.abc import Iterable, Sequence


LANGUAGE_NAMES = {
    "ar": "Arabic",
    "da": "Danish",
    "de": "German",
    "en": "English",
    "es": "Spanish",
    "fa": "Persian",
    "fi": "Finnish",
    "fr": "French",
    "he": "Hebrew",
    "hi": "Hindi",
    "id": "Indonesian",
    "it": "Italian",
    "ja": "Japanese",
    "ko": "Korean",
    "nl": "Dutch",
    "no": "Norwegian",
    "pl": "Polish",
    "pt": "Portuguese",
    "ru": "Russian",
    "sv": "Swedish",
    "th": "Thai",
    "tr": "Turkish",
    "uk": "Ukrainian",
    "ur": "Urdu",
    "vi": "Vietnamese",
    "zh": "Chinese",
}

REGION_NAMES = {
    "BR": "Brazil",
    "CN": "China",
    "DE": "Germany",
    "ES": "Spain",
    "FR": "France",
    "GB": "United Kingdom",
    "MX": "Mexico",
    "PT": "Portugal",
    "TR": "Turkey",
    "TW": "Taiwan",
    "US": "United States",
}

LOCALE_DISPLAY_OVERRIDES = {
    "pt-BR": "Portuguese (Brazil)",
    "pt-PT": "Portuguese (Portugal)",
    "zh-CN": "Chinese (Simplified)",
    "zh-Hans": "Chinese (Simplified)",
    "zh-Hant": "Chinese (Traditional)",
    "zh-TW": "Chinese (Traditional)",
}

SPECIAL_LOCALE_NAMES = {
    "source": "Source strings",
    "target": "PO target",
    "po-target": "PO target",
}

RTL_LANGUAGE_CODES = {"ar", "fa", "he", "ur"}

METADATA_COLUMN_NAMES = {
    "character",
    "comment",
    "comments",
    "context",
    "description",
    "max_length",
    "maxlen",
    "note",
    "notes",
    "screenshot",
    "speaker",
}

AMBIGUOUS_METADATA_NAMES = {"id"}
LOCALE_RE = re.compile(r"^[A-Za-z]{2,3}(?:[-_][A-Za-z0-9]{2,8}){0,3}$")
ID_LIKE_RE = re.compile(r"^[A-Za-z0-9_.:/\\-]+$")


def normalize_locale_code(locale: object) -> str:
    """Return a display-safe locale code without changing file column names."""
    raw = str(locale or "").strip()
    if not raw:
        return ""
    if raw in SPECIAL_LOCALE_NAMES:
        return raw

    hyphenated = raw.replace("_", "-")
    parts = [part for part in hyphenated.split("-") if part]
    if not parts:
        return hyphenated

    language = parts[0].lower()
    if len(parts) == 1:
        if language in LANGUAGE_NAMES or len(language) in (2, 3):
            return language
        return hyphenated

    normalized = [language]
    for part in parts[1:]:
        if len(part) == 4 and part.isalpha():
            normalized.append(part.title())
        elif len(part) in (2, 3) and part.isalpha():
            normalized.append(part.upper())
        else:
            normalized.append(part)
    return "-".join(normalized)


def language_display_name(locale: object) -> str:
    normalized = normalize_locale_code(locale)
    if not normalized:
        return ""
    if normalized in SPECIAL_LOCALE_NAMES:
        return SPECIAL_LOCALE_NAMES[normalized]
    if normalized in LOCALE_DISPLAY_OVERRIDES:
        return LOCALE_DISPLAY_OVERRIDES[normalized]

    parts = normalized.split("-")
    language = parts[0]
    base_name = LANGUAGE_NAMES.get(language)
    if not base_name:
        return normalized
    if len(parts) == 1:
        return base_name

    variant = parts[1]
    if variant in REGION_NAMES:
        return f"{base_name} ({REGION_NAMES[variant]})"
    return normalized


def locale_label(locale: object) -> str:
    normalized = normalize_locale_code(locale)
    display_name = language_display_name(locale)
    if not normalized:
        return ""
    if not display_name or display_name == normalized:
        return normalized
    return f"{normalized} \u2014 {display_name}"


def locale_list_label(locales: Iterable[object], limit: int | None = None) -> str:
    labels = [locale_label(locale) for locale in locales if str(locale or "").strip()]
    if limit is not None and len(labels) > limit:
        hidden_count = len(labels) - limit
        labels = labels[:limit] + [f"+{hidden_count} more"]
    return ", ".join(labels) if labels else "None"


def display_locale_codes(locales: Iterable[object]) -> list[str]:
    return [normalize_locale_code(locale) for locale in locales if str(locale or "").strip()]


def resolve_locale(available_locales: Sequence[str], requested_locale: str | None) -> str | None:
    if not requested_locale:
        return None
    requested = str(requested_locale).strip()
    if requested in available_locales:
        return requested

    requested_normalized = normalize_locale_code(requested)
    for locale in available_locales:
        if normalize_locale_code(locale) == requested_normalized:
            return locale
    return None


def choose_default_source_locale(available_locales: Sequence[str]) -> str | None:
    if not available_locales:
        return None
    if "source" in available_locales:
        return "source"

    for locale in available_locales:
        if normalize_locale_code(locale) == "en":
            return locale
    for locale in available_locales:
        if normalize_locale_code(locale).startswith("en-"):
            return locale
    return available_locales[0]


def is_locale_like(value: object) -> bool:
    raw = str(value or "").strip()
    if not raw:
        return False
    if raw in SPECIAL_LOCALE_NAMES:
        return True
    if not LOCALE_RE.match(raw):
        return False
    language = normalize_locale_code(raw).split("-", 1)[0]
    return language in LANGUAGE_NAMES or len(language) in (2, 3)


def is_metadata_column(column: object, values: Iterable[object] | None = None) -> bool:
    normalized_name = _metadata_name(column)
    if normalized_name in METADATA_COLUMN_NAMES:
        return True
    if normalized_name in AMBIGUOUS_METADATA_NAMES:
        return _values_look_like_ids(values or [])
    return False


def normalization_notes(locales: Iterable[object]) -> list[str]:
    notes: list[str] = []
    for locale in locales:
        raw = str(locale or "").strip()
        normalized = normalize_locale_code(raw)
        if raw and normalized and raw != normalized:
            notes.append(f"{raw} -> {normalized}")
    return notes


def rtl_locales(locales: Iterable[object]) -> list[str]:
    detected: list[str] = []
    for locale in locales:
        normalized = normalize_locale_code(locale)
        language = normalized.split("-", 1)[0]
        if language in RTL_LANGUAGE_CODES and normalized not in detected:
            detected.append(normalized)
    return detected


def _metadata_name(column: object) -> str:
    raw = str(column or "").strip().lower()
    raw = raw.replace("-", "_")
    raw = re.sub(r"\s+", "_", raw)
    return raw


def _values_look_like_ids(values: Iterable[object]) -> bool:
    checked = 0
    for value in values:
        text = str(value or "").strip()
        if not text:
            continue
        checked += 1
        if not ID_LIKE_RE.match(text):
            return False
        if not (re.search(r"[0-9_.:/\\-]", text) or text.upper() == text):
            return False
    return checked > 0
