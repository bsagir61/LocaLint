from __future__ import annotations

import re
from collections.abc import Iterable

from localint.models import Issue, LocalizationTable, Severity
from localint.utils import is_blank, looks_non_localizable


CHECKS = {
    "missing_translation": "Missing translation",
    "placeholder_mismatch": "Placeholder mismatch",
    "duplicate_keys": "Duplicate keys",
    "invalid_keys": "Empty or invalid keys",
    "untranslated_text": "Suspicious untranslated text",
    "length_risk": "Length expansion risk",
    "line_break_mismatch": "Line break mismatch",
    "whitespace": "Leading/trailing whitespace",
    "punctuation_mismatch": "Punctuation mismatch",
    "csv_bom": "CSV encoding/BOM warning",
}

KEY_RE = re.compile(r"^[A-Za-z0-9_.\-/]+$")
PRINTF_NAMED_RE = re.compile(r"%\([A-Za-z_][A-Za-z0-9_]*\)[#0\- +]?\d*(?:\.\d+)?[diouxXeEfFgGcrs]")
PRINTF_RE = re.compile(r"%(?!%)(?:[#0\- +]?\d*(?:\.\d+)?[sdf])")
DOUBLE_BRACE_RE = re.compile(r"\{\{[A-Za-z_][A-Za-z0-9_.:-]*\}\}")
BRACE_RE = re.compile(r"(?<!\{)\{[A-Za-z_][A-Za-z0-9_.:-]*\}(?!\})")
HTML_TAG_RE = re.compile(r"</?[A-Za-z][A-Za-z0-9]*(?:\s+[^<>]*?)?>")
RICH_TAG_RE = re.compile(r"\[/?[A-Za-z][A-Za-z0-9]*(?:=[^\]\s]+)?\]")
DOLLAR_VAR_RE = re.compile(r"\$[A-Za-z_][A-Za-z0-9_]*")


def extract_placeholders(text: str) -> set[str]:
    """Extract game/UI placeholders and lightweight markup tokens from text."""
    value = text or ""
    patterns = [
        PRINTF_NAMED_RE,
        PRINTF_RE,
        DOUBLE_BRACE_RE,
        BRACE_RE,
        HTML_TAG_RE,
        RICH_TAG_RE,
        DOLLAR_VAR_RE,
    ]
    found: set[str] = set()
    for pattern in patterns:
        found.update(match.group(0) for match in pattern.finditer(value))
    return found


def run_checks(
    table: LocalizationTable,
    source_language: str = "en",
    enabled_checks: Iterable[str] | None = None,
    length_warning_ratio: float = 1.8,
) -> list[Issue]:
    enabled = set(enabled_checks or CHECKS)
    issues: list[Issue] = []
    targets = table.target_languages(source_language)

    if "csv_bom" in enabled:
        for warning in table.encoding_warnings:
            issues.append(
                Issue(
                    severity=Severity.WARNING,
                    key="",
                    locale="",
                    check=CHECKS["csv_bom"],
                    message=warning,
                    suggestion="Export CSV as UTF-8 without BOM before importing into Godot.",
                )
            )

    if "duplicate_keys" in enabled:
        for key in table.duplicate_keys:
            issues.append(
                Issue(
                    severity=Severity.CRITICAL,
                    key=key,
                    locale="",
                    check=CHECKS["duplicate_keys"],
                    message=f"Key '{key}' appears more than once.",
                    suggestion="Keep one row per key so the game does not load an unexpected translation.",
                )
            )

    for row in table.rows:
        display_key = row.key if row.key.strip() else "<empty>"
        source_text = row.translations.get(source_language, "")

        if table.file_format != "po" and "invalid_keys" in enabled and (not row.key.strip() or not KEY_RE.match(row.key)):
            issues.append(
                Issue(
                    severity=Severity.WARNING,
                    key=display_key,
                    locale="",
                    check=CHECKS["invalid_keys"],
                    message="Key is empty or contains unsupported characters.",
                    suggestion="Use stable keys like START_GAME, menu.start, ui-start, or quests/main.",
                    source_text=source_text,
                )
            )

        if "whitespace" in enabled:
            for locale, value in row.translations.items():
                if value and value != value.strip():
                    issues.append(
                        Issue(
                            severity=Severity.INFO,
                            key=display_key,
                            locale=locale,
                            check=CHECKS["whitespace"],
                            message="Text has leading or trailing whitespace.",
                            suggestion="Trim accidental spaces unless they are intentional for layout.",
                            source_text=source_text,
                            target_text=value,
                        )
                    )

        for locale in targets:
            target_text = row.translations.get(locale, "")

            if "missing_translation" in enabled and is_blank(target_text):
                issues.append(
                    Issue(
                        severity=Severity.CRITICAL,
                        key=display_key,
                        locale=locale,
                        check=CHECKS["missing_translation"],
                        message="Target translation is missing.",
                        suggestion="Add a localized value before shipping.",
                        source_text=source_text,
                        target_text=target_text,
                    )
                )
                continue

            if "placeholder_mismatch" in enabled:
                issues.extend(_placeholder_issues(display_key, locale, source_text, target_text))

            if (
                "untranslated_text" in enabled
                and target_text == source_text
                and len(source_text.strip()) > 3
                and not looks_non_localizable(source_text)
            ):
                issues.append(
                    Issue(
                        severity=Severity.WARNING,
                        key=display_key,
                        locale=locale,
                        check=CHECKS["untranslated_text"],
                        message="Target text is identical to the source text.",
                        suggestion="Confirm this is intentionally untranslated.",
                        source_text=source_text,
                        target_text=target_text,
                    )
                )

            if "length_risk" in enabled and len(source_text) > 8:
                ratio = len(target_text) / max(len(source_text), 1)
                if ratio > 2.5:
                    severity = Severity.CRITICAL
                elif ratio > length_warning_ratio:
                    severity = Severity.WARNING
                else:
                    severity = None
                if severity:
                    issues.append(
                        Issue(
                            severity=severity,
                            key=display_key,
                            locale=locale,
                            check=CHECKS["length_risk"],
                            message="May overflow UI labels/buttons.",
                            suggestion="Shorten the translation or verify the UI can wrap/resize it.",
                            source_text=source_text,
                            target_text=target_text,
                        )
                    )

            if "line_break_mismatch" in enabled and source_text.count("\n") != target_text.count("\n"):
                issues.append(
                    Issue(
                        severity=Severity.WARNING,
                        key=display_key,
                        locale=locale,
                        check=CHECKS["line_break_mismatch"],
                        message="Line break count differs from the source.",
                        suggestion="Preserve intentional line breaks or confirm the layout handles the change.",
                        source_text=source_text,
                        target_text=target_text,
                    )
                )

            if "punctuation_mismatch" in enabled and _has_punctuation_mismatch(source_text, target_text):
                issues.append(
                    Issue(
                        severity=Severity.INFO,
                        key=display_key,
                        locale=locale,
                        check=CHECKS["punctuation_mismatch"],
                        message="Ending punctuation differs from the source.",
                        suggestion="Check whether the target should preserve the same prompt or emphasis.",
                        source_text=source_text,
                        target_text=target_text,
                    )
                )

    return issues


def _placeholder_issues(key: str, locale: str, source_text: str, target_text: str) -> list[Issue]:
    source_placeholders = extract_placeholders(source_text)
    target_placeholders = extract_placeholders(target_text)
    issues: list[Issue] = []

    missing = sorted(source_placeholders - target_placeholders)
    extra = sorted(target_placeholders - source_placeholders)

    if missing:
        issues.append(
            Issue(
                severity=Severity.CRITICAL,
                key=key,
                locale=locale,
                check=CHECKS["placeholder_mismatch"],
                message=f"Target is missing placeholder(s): {', '.join(missing)}.",
                suggestion="Copy every required variable, printf token, and markup tag from the source.",
                source_text=source_text,
                target_text=target_text,
            )
        )
    if extra:
        issues.append(
            Issue(
                severity=Severity.WARNING,
                key=key,
                locale=locale,
                check=CHECKS["placeholder_mismatch"],
                message=f"Target has extra placeholder(s): {', '.join(extra)}.",
                suggestion="Remove unexpected variables or confirm the game runtime supports them.",
                source_text=source_text,
                target_text=target_text,
            )
        )

    return issues


def _has_punctuation_mismatch(source_text: str, target_text: str) -> bool:
    source = source_text.strip()
    target = target_text.strip()
    if not source or not target:
        return False
    if source.endswith("..."):
        return not (target.endswith("...") or target.endswith("\u2026"))
    equivalents = {
        "?": ("?", "\u061f"),
        "!": ("!", "\u00a1"),
        ":": (":", "\uff1a"),
    }
    for punctuation, allowed in equivalents.items():
        if source.endswith(punctuation):
            return not target.endswith(allowed)
    return False
