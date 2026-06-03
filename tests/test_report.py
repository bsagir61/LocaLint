from localint.models import Issue, LocalizationRow, LocalizationTable, Severity
from localint.report import (
    RELEASE_GATE_BLOCK,
    RELEASE_GATE_PASS,
    RELEASE_GATE_REVIEW,
    release_gate_for_counts,
    report_to_markdown,
    sort_issues_for_action,
)


def test_sort_issues_for_action_prioritizes_critical_then_warning_then_info():
    issues = [
        Issue(severity=Severity.INFO, key="A", locale="tr", check="Info", message="Info"),
        Issue(severity=Severity.WARNING, key="B", locale="tr", check="Warning", message="Warning"),
        Issue(severity=Severity.CRITICAL, key="C", locale="tr", check="Critical", message="Critical"),
    ]

    ordered = sort_issues_for_action(issues)

    assert [issue.severity for issue in ordered] == [Severity.CRITICAL, Severity.WARNING, Severity.INFO]


def test_release_gate_states_are_deterministic():
    assert release_gate_for_counts(0, 0, 0) == RELEASE_GATE_PASS
    assert release_gate_for_counts(0, 1, 0) == RELEASE_GATE_REVIEW
    assert release_gate_for_counts(0, 0, 1) == RELEASE_GATE_REVIEW
    assert release_gate_for_counts(1, 0, 0) == RELEASE_GATE_BLOCK


def test_markdown_report_includes_professional_sections_and_escaped_table_cells():
    table = LocalizationTable(
        rows=[LocalizationRow(key="START", translations={"en": "Start", "tr": ""})],
        languages=["en", "tr"],
        source_name="sample.csv",
    )
    issues = [
        Issue(
            severity=Severity.CRITICAL,
            key="START",
            locale="tr",
            check="Missing translation",
            message="Target translation is missing.",
            suggestion="Add a localized value before shipping.",
            source_text="Start | Begin",
            target_text="",
        )
    ]

    markdown = report_to_markdown(table, issues, "en")

    assert "## Executive Summary" in markdown
    assert "**Release gate:** BLOCK" in markdown
    assert "## What This Means" in markdown
    assert "## Fix Plan" in markdown
    assert "## Full Issue Table" in markdown
    assert "Start \\| Begin" in markdown
