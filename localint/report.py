from __future__ import annotations

import html
from collections import Counter

import pandas as pd

from localint.models import Issue, LocalizationTable, Severity


REPORT_COLUMNS = [
    "severity",
    "key",
    "locale",
    "check",
    "message",
    "suggestion",
    "source_text",
    "target_text",
]

SEVERITY_ORDER = {Severity.CRITICAL: 0, Severity.WARNING: 1, Severity.INFO: 2}


def issues_to_dataframe(issues: list[Issue]) -> pd.DataFrame:
    records = []
    for issue in issues:
        record = issue.model_dump()
        record["severity"] = issue.severity.value
        records.append(record)
    return pd.DataFrame(records, columns=REPORT_COLUMNS)


def summarize(table: LocalizationTable, issues: list[Issue], source_language: str) -> dict[str, object]:
    counts = Counter(issue.severity for issue in issues)
    critical = counts[Severity.CRITICAL]
    warning = counts[Severity.WARNING]
    info = counts[Severity.INFO]
    health_score = max(0, 100 - critical * 12 - warning * 5 - info)
    return {
        "total_keys": table.total_keys,
        "languages_detected": table.languages,
        "source_language": source_language,
        "total_issues": len(issues),
        "critical_issues": critical,
        "warning_issues": warning,
        "info_issues": info,
        "health_score": health_score,
    }


def report_to_markdown(table: LocalizationTable, issues: list[Issue], source_language: str) -> str:
    summary = summarize(table, issues, source_language)
    ordered_issues = sort_issues_for_action(issues)
    frame = issues_to_dataframe(ordered_issues)
    targets = table.target_languages(source_language)
    lines = [
        "# LocaLint QA Report",
        "",
        "## Executive Summary",
        "",
        f"**Health score:** {summary['health_score']}/100",
        "",
        "| Metric | Value |",
        "| --- | --- |",
        f"| Source file | {table.source_name} |",
        f"| Source language | {source_language} |",
        f"| Target languages | {', '.join(targets) or 'None'} |",
        f"| Total keys | {summary['total_keys']} |",
        f"| Languages detected | {', '.join(summary['languages_detected'])} |",
        f"| Total issues | {summary['total_issues']} |",
        f"| Critical issues | {summary['critical_issues']} |",
        f"| Warning issues | {summary['warning_issues']} |",
        f"| Info issues | {summary['info_issues']} |",
        "",
        "## What This Means",
        "",
        _meaning_for_summary(summary),
        "",
        "## Next Fixes",
        "",
    ]
    top_issues = ordered_issues[:5]
    if not top_issues:
        lines.append("No fixes needed for the selected checks.")
    else:
        for index, issue in enumerate(top_issues, start=1):
            locale = f" ({issue.locale})" if issue.locale else ""
            lines.append(f"{index}. **{issue.severity.value}** - `{issue.key}`{locale}: {issue.message}")
            if issue.suggestion:
                lines.append(f"   Suggestion: {issue.suggestion}")
    lines.extend(
        [
            "",
            "## Full Issue Table",
            "",
        ]
    )
    if frame.empty:
        lines.append("No issues found.")
    else:
        lines.append(_dataframe_to_markdown(frame))
    return "\n".join(lines)


def sort_issues_for_action(issues: list[Issue]) -> list[Issue]:
    return sorted(
        issues,
        key=lambda issue: (
            SEVERITY_ORDER.get(issue.severity, 9),
            issue.key,
            issue.locale,
            issue.check,
        ),
    )


def _meaning_for_summary(summary: dict[str, object]) -> str:
    if int(summary["critical_issues"]) > 0:
        return (
            "Critical issues should be fixed before release because they can create missing text, broken "
            "runtime formatting, or ambiguous localization keys."
        )
    if int(summary["warning_issues"]) > 0:
        return (
            "No critical issues were found, but warnings should be reviewed for layout risk, untranslated "
            "strings, or inconsistent formatting."
        )
    return "The selected checks did not find release-blocking localization problems."


def summary_to_markdown(table: LocalizationTable, issues: list[Issue], source_language: str) -> str:
    summary = summarize(table, issues, source_language)
    return "\n".join(
        [
            "# LocaLint Summary",
            "",
            f"Health score: **{summary['health_score']}/100**",
            "",
            f"- Total keys: {summary['total_keys']}",
            f"- Languages detected: {', '.join(summary['languages_detected'])}",
            f"- Total issues: {summary['total_issues']}",
            f"- Critical issues: {summary['critical_issues']}",
            f"- Warning issues: {summary['warning_issues']}",
            f"- Info issues: {summary['info_issues']}",
        ]
    )


def summary_to_html(table: LocalizationTable, issues: list[Issue], source_language: str) -> str:
    summary = summarize(table, issues, source_language)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>LocaLint Summary</title>
  <style>
    body {{ font-family: Inter, system-ui, sans-serif; margin: 40px; color: #15171a; }}
    .score {{ font-size: 44px; font-weight: 800; }}
    li {{ margin: 8px 0; }}
  </style>
</head>
<body>
  <h1>LocaLint Summary</h1>
  <p class="score">{summary["health_score"]}/100</p>
  <ul>
    <li>Total keys: {summary["total_keys"]}</li>
    <li>Languages detected: {html.escape(", ".join(summary["languages_detected"]))}</li>
    <li>Total issues: {summary["total_issues"]}</li>
    <li>Critical issues: {summary["critical_issues"]}</li>
    <li>Warning issues: {summary["warning_issues"]}</li>
    <li>Info issues: {summary["info_issues"]}</li>
  </ul>
</body>
</html>"""


def _dataframe_to_markdown(frame: pd.DataFrame) -> str:
    columns = list(frame.columns)
    escaped_rows = []
    for _, row in frame.iterrows():
        escaped_rows.append([_escape_markdown_cell(str(row[column])) for column in columns])

    header = "| " + " | ".join(columns) + " |"
    divider = "| " + " | ".join("---" for _ in columns) + " |"
    body = ["| " + " | ".join(row) + " |" for row in escaped_rows]
    return "\n".join([header, divider, *body])


def _escape_markdown_cell(value: str) -> str:
    return value.replace("\n", "<br>").replace("|", "\\|")
