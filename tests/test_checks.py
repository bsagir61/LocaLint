from localint.checks import extract_placeholders, run_checks
from localint.models import LocalizationRow, LocalizationTable, Severity


def test_placeholder_extraction_supports_game_patterns():
    text = "Hi {name} {{count}} %s %d %(score)s <b>[/b] [color=red] $player"

    placeholders = extract_placeholders(text)

    assert "{name}" in placeholders
    assert "{{count}}" in placeholders
    assert "%s" in placeholders
    assert "%d" in placeholders
    assert "%(score)s" in placeholders
    assert "<b>" in placeholders
    assert "[/b]" in placeholders
    assert "[color=red]" in placeholders
    assert "$player" in placeholders


def test_missing_translations_are_critical():
    table = LocalizationTable(
        rows=[LocalizationRow(key="START_GAME", translations={"en": "Start Game", "tr": ""})],
        languages=["en", "tr"],
    )

    issues = run_checks(table, source_language="en")

    assert any(issue.check == "Missing translation" and issue.severity == Severity.CRITICAL for issue in issues)


def test_duplicate_keys_are_critical():
    table = LocalizationTable(
        rows=[
            LocalizationRow(key="QUIT", translations={"en": "Quit", "tr": "Cik"}),
            LocalizationRow(key="QUIT", translations={"en": "Quit Game", "tr": "Oyundan Cik"}),
        ],
        languages=["en", "tr"],
        duplicate_keys=["QUIT"],
    )

    issues = run_checks(table, source_language="en")

    assert any(issue.check == "Duplicate keys" and issue.severity == Severity.CRITICAL for issue in issues)


def test_length_risk_flags_warning_and_critical():
    table = LocalizationTable(
        rows=[
            LocalizationRow(key="WARN", translations={"en": "Open menu", "tr": "Menunun tamamini ac"}),
            LocalizationRow(
                key="CRITICAL",
                translations={"en": "Inventory", "tr": "Envanter penceresini acmak icin buraya tiklayin lutfen"},
            ),
        ],
        languages=["en", "tr"],
    )

    issues = run_checks(table, source_language="en", enabled_checks=["length_risk"], length_warning_ratio=1.8)

    severities_by_key = {issue.key: issue.severity for issue in issues}
    assert severities_by_key["WARN"] == Severity.WARNING
    assert severities_by_key["CRITICAL"] == Severity.CRITICAL


def test_placeholder_mismatch_reports_missing_and_extra_tokens():
    table = LocalizationTable(
        rows=[
            LocalizationRow(key="COINS", translations={"en": "You have {count} coins", "tr": "Jetonun var {total}"})
        ],
        languages=["en", "tr"],
    )

    issues = run_checks(table, source_language="en", enabled_checks=["placeholder_mismatch"])

    assert any(issue.severity == Severity.CRITICAL and "{count}" in issue.message for issue in issues)
    assert any(issue.severity == Severity.WARNING and "{total}" in issue.message for issue in issues)
