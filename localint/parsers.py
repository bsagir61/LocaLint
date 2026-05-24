from __future__ import annotations

import io
import json
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd

from localint.models import LocalizationRow, LocalizationTable
from localint.utils import as_text


UTF8_BOM = b"\xef\xbb\xbf"
KEY_FALLBACK_WARNING = "No column named 'key' was found. LocaLint is using the first column as localization keys."


class ParserError(ValueError):
    """Raised when LocaLint cannot parse an uploaded localization file."""


def parse_upload(filename: str, data: bytes) -> LocalizationTable:
    suffix = Path(filename).suffix.lower()
    if suffix == ".csv":
        return parse_csv(data, source_name=filename)
    if suffix == ".json":
        return parse_json(data, source_name=filename)
    if suffix == ".po":
        return parse_po(data, source_name=filename)
    raise ParserError("Unsupported file type. Upload a CSV or JSON localization file.")


def parse_csv(data: bytes, source_name: str = "uploaded.csv") -> LocalizationTable:
    if not data or not data.strip():
        raise ParserError(
            "This CSV file is empty. Upload a CSV with a key column and at least one language column."
        )

    warnings: list[str] = []
    shape_warnings: list[str] = []
    if data.startswith(UTF8_BOM):
        warnings.append(
            "Godot CSV localization commonly expects UTF-8 without BOM. Re-save from LibreOffice or Google Sheets."
        )

    try:
        frame = pd.read_csv(
            io.BytesIO(data),
            encoding="utf-8-sig",
            dtype=str,
            keep_default_na=False,
            na_filter=False,
        )
    except Exception as exc:  # pragma: no cover - pandas error messages vary
        raise ParserError(
            "Could not read this CSV file. Please check that it has a key column and at least one language column."
        ) from exc

    columns = [str(column).strip() for column in frame.columns]
    frame.columns = columns
    if not columns:
        raise ParserError(
            "Could not read this CSV file. Please check that it has a key column and at least one language column."
        )

    key_columns = [column for column in columns if column.lower() == "key"]
    if key_columns:
        key_column = key_columns[0]
    else:
        key_column = columns[0]
        shape_warnings.append(KEY_FALLBACK_WARNING)

    languages = [column for column in columns if column != key_column]
    if not languages:
        raise ParserError("CSV needs at least one language column after the key column, such as en or tr.")

    if frame.empty:
        raise ParserError("This CSV has headers but no rows. Add at least one localization key to check.")

    rows: list[LocalizationRow] = []
    for index, record in frame.iterrows():
        key = as_text(record.get(key_column, ""))
        translations = {language: as_text(record.get(language, "")) for language in languages}
        rows.append(LocalizationRow(key=key, translations=translations, row_number=int(index) + 2))

    counts = Counter(row.key for row in rows if row.key.strip())
    duplicate_keys = sorted(key for key, count in counts.items() if count > 1)

    return LocalizationTable(
        rows=rows,
        languages=languages,
        duplicate_keys=duplicate_keys,
        encoding_warnings=warnings,
        shape_warnings=shape_warnings,
        source_name=source_name,
    )


def parse_json(data: bytes, source_name: str = "uploaded.json") -> LocalizationTable:
    if not data or not data.strip():
        raise ParserError(
            "This JSON file is empty. Upload a flat object like {'START_GAME': {'en': 'Start Game'}}."
        )

    try:
        payload = json.loads(data.decode("utf-8-sig"))
    except Exception as exc:  # pragma: no cover - JSON error messages vary
        raise ParserError(
            "Could not read this JSON file. Please check that it is valid JSON and uses the supported flat dictionary shape."
        ) from exc

    if not isinstance(payload, dict):
        raise ParserError("JSON must be a flat object where each key maps to locale values.")
    if not payload:
        raise ParserError("JSON has no localization entries. Add at least one key with locale values.")

    languages: list[str] = []
    rows: list[LocalizationRow] = []
    for key, locale_values in payload.items():
        if not isinstance(locale_values, dict):
            raise ParserError("JSON values must be objects like {'en': 'Start Game', 'tr': 'Oyuna Basla'}.")
        if not locale_values:
            raise ParserError(f"JSON key '{key}' has no locale values. Add at least one language entry.")
        translations: dict[str, str] = {}
        for locale, text in locale_values.items():
            locale_name = str(locale)
            translations[locale_name] = as_text(text)
            if locale_name not in languages:
                languages.append(locale_name)
        rows.append(LocalizationRow(key=str(key), translations=translations))

    if not languages:
        raise ParserError("JSON needs at least one language code, such as en or tr.")

    return LocalizationTable(rows=rows, languages=languages, source_name=source_name)


def parse_po(data: bytes, source_name: str = "uploaded.po") -> LocalizationTable:
    # TODO: Add optional polib support after the CSV/JSON MVP is validated with users.
    raise ParserError(".po parsing is planned but not included in this MVP yet.")


def table_to_frame(table: LocalizationTable) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    for row in table.rows:
        record: dict[str, Any] = {"key": row.key}
        record.update(row.translations)
        records.append(record)
    return pd.DataFrame(records, columns=["key", *table.languages])
