from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from localint import __version__
from localint.models import Issue, LocalizationTable, Severity
from localint.parsers import ParserError, parse_upload
from localint.report import issues_to_dataframe, report_to_markdown, sort_issues_for_action, summarize


EXIT_OK = 0
EXIT_CRITICAL = 1
EXIT_INVALID = 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m localint.cli",
        description="Run LocaLint localization QA checks from the terminal.",
    )
    parser.add_argument("file", help="CSV or JSON localization file to analyze.")
    parser.add_argument("--source", help="Source language. Defaults to en when available, otherwise first locale.")
    parser.add_argument(
        "--format",
        choices=["text", "markdown", "json", "csv"],
        default="text",
        help="Output format. Default: text.",
    )
    parser.add_argument("--out", help="Optional output file path. Prints to terminal when omitted.")
    parser.add_argument(
        "--fail-on-critical",
        action="store_true",
        help="Exit with code 1 when critical issues are found.",
    )
    parser.add_argument(
        "--max-issues",
        type=int,
        help="Limit number of printed issues in terminal text mode.",
    )
    parser.add_argument("--version", action="version", version=f"LocaLint {__version__}")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.max_issues is not None and args.max_issues < 0:
        parser.error("--max-issues must be 0 or greater")

    input_path = Path(args.file)
    if not input_path.exists() or not input_path.is_file():
        print(f"Input file not found: {input_path}", file=sys.stderr)
        return EXIT_INVALID

    try:
        data = input_path.read_bytes()
        table = parse_upload(str(input_path), data)
    except (OSError, ParserError) as exc:
        print(f"Could not analyze file: {exc}", file=sys.stderr)
        return EXIT_INVALID

    source_language = _resolve_source_language(table, args.source)
    if source_language is None:
        detected = ", ".join(table.languages) or "none"
        print(f"Source language not found. Detected languages: {detected}", file=sys.stderr)
        return EXIT_INVALID

    issues = run_analysis(table, source_language)
    output = build_output(args.format, table, issues, source_language, str(input_path), args.max_issues)

    if args.out:
        try:
            Path(args.out).write_text(output, encoding="utf-8", newline="")
        except OSError as exc:
            print(f"Could not write output file: {exc}", file=sys.stderr)
            return EXIT_INVALID
    else:
        print(output)

    has_critical = any(issue.severity == Severity.CRITICAL for issue in issues)
    if args.fail_on_critical and has_critical:
        return EXIT_CRITICAL
    return EXIT_OK


def run_analysis(table: LocalizationTable, source_language: str) -> list[Issue]:
    from localint.checks import run_checks

    return run_checks(table, source_language=source_language)


def build_output(
    output_format: str,
    table: LocalizationTable,
    issues: list[Issue],
    source_language: str,
    display_file: str,
    max_issues: int | None = None,
) -> str:
    if output_format == "markdown":
        return report_to_markdown(table, issues, source_language)
    if output_format == "json":
        return json.dumps(
            build_json_report(table, issues, source_language, display_file),
            indent=2,
            ensure_ascii=False,
        )
    if output_format == "csv":
        return issues_to_dataframe(sort_issues_for_action(issues)).to_csv(index=False)
    return build_text_report(table, issues, source_language, display_file, max_issues=max_issues)


def build_json_report(
    table: LocalizationTable,
    issues: list[Issue],
    source_language: str,
    display_file: str,
) -> dict[str, object]:
    summary = summarize(table, issues, source_language)
    return {
        "file": display_file,
        "source_language": source_language,
        "target_languages": table.target_languages(source_language),
        "total_keys": summary["total_keys"],
        "total_issues": summary["total_issues"],
        "severity_counts": {
            "critical": summary["critical_issues"],
            "warning": summary["warning_issues"],
            "info": summary["info_issues"],
        },
        "health_score": summary["health_score"],
        "issues": [_issue_to_json(issue) for issue in sort_issues_for_action(issues)],
    }


def build_text_report(
    table: LocalizationTable,
    issues: list[Issue],
    source_language: str,
    display_file: str,
    max_issues: int | None = None,
) -> str:
    summary = summarize(table, issues, source_language)
    ordered_issues = sort_issues_for_action(issues)
    if max_issues is not None:
        ordered_issues = ordered_issues[:max_issues]

    lines = [
        "LocaLint report",
        f"File: {display_file}",
        f"Source language: {source_language}",
        f"Target languages: {', '.join(table.target_languages(source_language)) or 'None'}",
        f"Total keys: {summary['total_keys']}",
        f"Total issues: {summary['total_issues']}",
        f"Critical: {summary['critical_issues']}",
        f"Warning: {summary['warning_issues']}",
        f"Info: {summary['info_issues']}",
        f"Health score: {summary['health_score']}/100",
        "",
        "Top issues:",
    ]
    if not ordered_issues:
        lines.append("No issues found.")
    else:
        lines.extend(_format_text_issue(issue) for issue in ordered_issues)
    return "\n".join(lines)


def _resolve_source_language(table: LocalizationTable, requested_source: str | None) -> str | None:
    if requested_source:
        return requested_source if requested_source in table.languages else None
    if "en" in table.languages:
        return "en"
    return table.languages[0] if table.languages else None


def _format_text_issue(issue: Issue) -> str:
    location = issue.key
    if issue.locale:
        location = f"{location} / {issue.locale}"
    return f"[{issue.severity.value}] {location} - {issue.check}: {issue.message}"


def _issue_to_json(issue: Issue) -> dict[str, str]:
    record = issue.model_dump()
    record["severity"] = issue.severity.value
    return record


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
