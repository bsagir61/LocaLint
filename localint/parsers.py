from __future__ import annotations

import ast
import io
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd

from localint.models import LocalizationRow, LocalizationTable
from localint.utils import as_text


UTF8_BOM = b"\xef\xbb\xbf"
KEY_FALLBACK_WARNING = "No column named 'key' was found. LocaLint is using the first column as localization keys."
PO_FIELD_RE = re.compile(r'^(msgctxt|msgid|msgid_plural|msgstr)(?:\[(\d+)\])?\s+(".*")\s*$')
PO_FORMAT_WARNING = "PO file parsed as source/target rows from msgid/msgstr. Comments and headers are ignored."
PO_CONTEXT_WARNING = "PO context is included in keys when msgctxt is present."
PO_PLURAL_WARNING = "PO plural entries are shown as separate rows using msgstr[n]."


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
    raise ParserError("Unsupported file type. Upload a CSV, JSON, or PO localization file.")


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
        file_format="csv",
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

    return LocalizationTable(rows=rows, languages=languages, file_format="json", source_name=source_name)


def parse_po(data: bytes, source_name: str = "uploaded.po") -> LocalizationTable:
    if not data or not data.strip():
        raise ParserError("This PO file is empty. Upload a PO file with msgid/msgstr entries.")

    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ParserError("Could not read this PO file. Please save it as UTF-8 and try again.") from exc

    entries = _read_po_entries(text)
    rows: list[LocalizationRow] = []
    entry_keys: list[str] = []
    saw_context = False
    saw_plural = False

    for entry in entries:
        msgid = entry.get("msgid")
        msgctxt = entry.get("msgctxt")
        msgid_plural = entry.get("msgid_plural")
        if msgid is None:
            raise ParserError("Invalid PO file. Each translation entry needs a msgid.")
        if msgid == "" and msgctxt is None and msgid_plural is None:
            continue

        base_key = _po_key(msgctxt, msgid)
        entry_keys.append(base_key)
        saw_context = saw_context or msgctxt is not None

        plural_targets = entry.get("msgstr_plural", {})
        if msgid_plural is not None:
            saw_plural = True
            plural_indices = _po_plural_indices(plural_targets)
            for plural_index in plural_indices:
                source_text = msgid if plural_index == 0 else msgid_plural
                target_text = plural_targets.get(plural_index, "")
                rows.append(
                    LocalizationRow(
                        key=f"{base_key} [plural {plural_index}]",
                        translations={"source": source_text, "target": target_text},
                        row_number=entry.get("line_number"),
                    )
                )
            continue

        rows.append(
            LocalizationRow(
                key=base_key,
                translations={"source": msgid, "target": entry.get("msgstr") or ""},
                row_number=entry.get("line_number"),
            )
        )

    if not rows:
        raise ParserError("This PO file has no usable msgid/msgstr entries.")

    counts = Counter(entry_keys)
    duplicate_keys = sorted(key for key, count in counts.items() if count > 1)
    shape_warnings = [PO_FORMAT_WARNING]
    if saw_context:
        shape_warnings.append(PO_CONTEXT_WARNING)
    if saw_plural:
        shape_warnings.append(PO_PLURAL_WARNING)

    return LocalizationTable(
        rows=rows,
        languages=["source", "target"],
        file_format="po",
        duplicate_keys=duplicate_keys,
        shape_warnings=shape_warnings,
        source_name=source_name,
    )


def _read_po_entries(text: str) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    entry = _new_po_entry(1)
    entry_started = False
    current_field: tuple[str, int | None] | None = None

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            if entry_started:
                entries.append(entry)
                entry = _new_po_entry(line_number + 1)
                entry_started = False
                current_field = None
            continue
        if line.startswith("#"):
            continue

        match = PO_FIELD_RE.match(line)
        if match:
            field, plural_index_text, quoted_value = match.groups()
            plural_index = int(plural_index_text) if plural_index_text is not None else None
            if plural_index is not None and field != "msgstr":
                raise ParserError("Invalid PO file. Only msgstr entries may use plural indexes.")
            if not entry_started:
                entry = _new_po_entry(line_number)
                entry_started = True
            _set_po_value(entry, field, plural_index, _decode_po_string(quoted_value, line_number))
            current_field = (field, plural_index)
            continue

        if line.startswith('"'):
            if current_field is None:
                raise ParserError("Invalid PO file. Found a continued string before any PO field.")
            field, plural_index = current_field
            _append_po_value(entry, field, plural_index, _decode_po_string(line, line_number))
            continue

        if line.startswith(("msgctxt", "msgid", "msgid_plural", "msgstr")):
            raise ParserError("Invalid PO file. PO fields must use quoted strings.")
        raise ParserError("Could not read this PO file. LocaLint supports msgctxt, msgid, msgid_plural, msgstr, and msgstr[n].")

    if entry_started:
        entries.append(entry)
    return entries


def _new_po_entry(line_number: int) -> dict[str, Any]:
    return {
        "msgctxt": None,
        "msgid": None,
        "msgid_plural": None,
        "msgstr": None,
        "msgstr_plural": {},
        "line_number": line_number,
    }


def _decode_po_string(value: str, line_number: int) -> str:
    try:
        decoded = ast.literal_eval(value)
    except (SyntaxError, ValueError) as exc:
        raise ParserError(f"Invalid PO string on line {line_number}.") from exc
    if not isinstance(decoded, str):
        raise ParserError(f"Invalid PO string on line {line_number}.")
    return decoded


def _set_po_value(entry: dict[str, Any], field: str, plural_index: int | None, value: str) -> None:
    if field == "msgstr" and plural_index is not None:
        entry["msgstr_plural"][plural_index] = value
        return
    entry[field] = value


def _append_po_value(entry: dict[str, Any], field: str, plural_index: int | None, value: str) -> None:
    if field == "msgstr" and plural_index is not None:
        entry["msgstr_plural"][plural_index] = entry["msgstr_plural"].get(plural_index, "") + value
        return
    entry[field] = (entry.get(field) or "") + value


def _po_key(msgctxt: str | None, msgid: str) -> str:
    msgid_key = _po_key_part(msgid)
    if msgctxt:
        return f"{_po_key_part(msgctxt)}::{msgid_key}"
    return msgid_key


def _po_key_part(value: str) -> str:
    return value.replace("\r", "\\r").replace("\n", "\\n")


def _po_plural_indices(plural_targets: dict[int, str]) -> list[int]:
    if not plural_targets:
        return [0, 1]
    max_index = max(max(plural_targets), 1)
    return list(range(max_index + 1))


def table_to_frame(table: LocalizationTable) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    for row in table.rows:
        record: dict[str, Any] = {"key": row.key}
        record.update(row.translations)
        records.append(record)
    return pd.DataFrame(records, columns=["key", *table.languages])
