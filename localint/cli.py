from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from localint import __version__
from localint.baseline import BaselineError, compare_to_baseline, load_baseline, write_baseline
from localint.config import ConfigError, init_config, load_config
from localint.locales import (
    choose_default_source_locale,
    display_locale_codes,
    normalize_locale_code,
    resolve_locale,
)
from localint.models import Issue, LocalizationTable, Severity
from localint.parsers import ParserError, parse_upload
from localint.report import (
    issues_to_dataframe,
    release_gate_explanation,
    report_to_markdown,
    sort_issues_for_action,
    summarize,
)


EXIT_OK = 0
EXIT_CRITICAL = 1
EXIT_INVALID = 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m localint.cli",
        description="Run LocaLint localization QA checks from the terminal.",
    )
    parser.add_argument("file", nargs="?", help="CSV, JSON, or PO localization file to analyze.")
    parser.add_argument("--source", help="Source locale. Defaults to en, then en-US, then the first detected locale.")
    parser.add_argument("--config", help="Optional .localint.toml config file.")
    parser.add_argument("--init-config", action="store_true", help="Create a starter .localint.toml in the current folder.")
    parser.add_argument("--force", action="store_true", help="Overwrite .localint.toml when used with --init-config.")
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
    parser.add_argument("--write-baseline", help="Write current issue fingerprints to a baseline JSON file.")
    parser.add_argument("--baseline", help="Compare current issues against a baseline JSON file.")
    parser.add_argument(
        "--fail-on-new-critical",
        action="store_true",
        help="Exit with code 1 only when critical issues are new compared with --baseline.",
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

    if args.init_config:
        try:
            created_path = init_config(force=args.force)
        except ConfigError as exc:
            print(f"Could not initialize config: {exc}", file=sys.stderr)
            return EXIT_INVALID
        print(f"Created config: {created_path}")
        return EXIT_OK
    if args.force:
        parser.error("--force can only be used with --init-config")
    if args.max_issues is not None and args.max_issues < 0:
        parser.error("--max-issues must be 0 or greater")
    if not args.file:
        parser.error("file is required unless --init-config is used")

    config = None
    if args.config:
        try:
            config = load_config(args.config)
        except ConfigError as exc:
            print(f"Could not load config: {exc}", file=sys.stderr)
            return EXIT_INVALID

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

    requested_source = args.source or (config.source_language if config and config.source_language else None)
    source_language = _resolve_source_language(table, requested_source)
    if source_language is None:
        detected = ", ".join(display_locale_codes(table.languages)) or "none"
        if requested_source:
            print(f"Source language '{requested_source}' was not found. Available locales: {detected}.", file=sys.stderr)
        else:
            print(f"Source language not found. Available locales: {detected}.", file=sys.stderr)
        return EXIT_INVALID

    enabled_checks = config.enabled_checks if config and config.enabled_checks is not None else None
    length_warning_ratio = config.length_warning_ratio if config and config.length_warning_ratio is not None else 1.8
    issues = run_analysis(table, source_language, enabled_checks, length_warning_ratio)

    baseline_result = None
    if args.baseline:
        try:
            baseline_result = compare_to_baseline(issues, load_baseline(args.baseline))
        except BaselineError as exc:
            print(f"Could not use baseline: {exc}", file=sys.stderr)
            return EXIT_INVALID
    if args.fail_on_new_critical and baseline_result is None:
        print("--fail-on-new-critical requires --baseline.", file=sys.stderr)
        return EXIT_INVALID
    if config and config.gate_fail_on == "new_critical" and baseline_result is None:
        print("Config gate.fail_on = 'new_critical' requires --baseline.", file=sys.stderr)
        return EXIT_INVALID

    if args.write_baseline:
        try:
            write_baseline(args.write_baseline, issues)
        except BaselineError as exc:
            print(f"Could not write baseline: {exc}", file=sys.stderr)
            return EXIT_INVALID

    output = build_output(
        args.format,
        table,
        issues,
        source_language,
        str(input_path),
        args.max_issues,
        baseline_result=baseline_result,
    )

    if args.out:
        try:
            Path(args.out).write_text(output, encoding="utf-8", newline="")
        except OSError as exc:
            print(f"Could not write output file: {exc}", file=sys.stderr)
            return EXIT_INVALID
    else:
        print(output)

    has_critical = any(issue.severity == Severity.CRITICAL for issue in issues)
    new_critical_count = int(baseline_result["new_critical_count"]) if baseline_result else 0
    if args.fail_on_new_critical and new_critical_count:
        return EXIT_CRITICAL
    if config and config.gate_fail_on == "new_critical" and new_critical_count:
        return EXIT_CRITICAL
    if (args.fail_on_critical or (config and config.gate_fail_on == "critical")) and has_critical:
        return EXIT_CRITICAL
    return EXIT_OK


def run_analysis(
    table: LocalizationTable,
    source_language: str,
    enabled_checks: list[str] | None = None,
    length_warning_ratio: float = 1.8,
) -> list[Issue]:
    from localint.checks import run_checks

    return run_checks(
        table,
        source_language=source_language,
        enabled_checks=enabled_checks,
        length_warning_ratio=length_warning_ratio,
    )


def build_output(
    output_format: str,
    table: LocalizationTable,
    issues: list[Issue],
    source_language: str,
    display_file: str,
    max_issues: int | None = None,
    baseline_result: dict[str, object] | None = None,
) -> str:
    if output_format == "markdown":
        return report_to_markdown(table, issues, source_language, baseline_result=baseline_result)
    if output_format == "json":
        return json.dumps(
            build_json_report(table, issues, source_language, display_file, baseline_result=baseline_result),
            indent=2,
            ensure_ascii=False,
        )
    if output_format == "csv":
        return issues_to_dataframe(sort_issues_for_action(issues)).to_csv(index=False)
    return build_text_report(
        table,
        issues,
        source_language,
        display_file,
        max_issues=max_issues,
        baseline_result=baseline_result,
    )


def build_json_report(
    table: LocalizationTable,
    issues: list[Issue],
    source_language: str,
    display_file: str,
    baseline_result: dict[str, object] | None = None,
) -> dict[str, object]:
    summary = summarize(table, issues, source_language)
    payload: dict[str, object] = {
        "file": display_file,
        "source_language": normalize_locale_code(source_language),
        "target_languages": display_locale_codes(table.target_languages(source_language)),
        "total_keys": summary["total_keys"],
        "total_issues": summary["total_issues"],
        "release_gate": summary["release_gate"],
        "severity_counts": {
            "critical": summary["critical_issues"],
            "warning": summary["warning_issues"],
            "info": summary["info_issues"],
        },
        "health_score": summary["health_score"],
        "issues": [_issue_to_json(issue) for issue in sort_issues_for_action(issues)],
    }
    if baseline_result:
        payload["baseline"] = {
            "known_issues": baseline_result["known_count"],
            "new_issues": baseline_result["new_count"],
            "new_critical_issues": baseline_result["new_critical_count"],
        }
    return payload


def build_text_report(
    table: LocalizationTable,
    issues: list[Issue],
    source_language: str,
    display_file: str,
    max_issues: int | None = None,
    baseline_result: dict[str, object] | None = None,
) -> str:
    summary = summarize(table, issues, source_language)
    ordered_issues = sort_issues_for_action(issues)
    if max_issues is not None:
        ordered_issues = ordered_issues[:max_issues]

    lines = [
        "LocaLint report",
        f"File: {display_file}",
        f"Source language: {normalize_locale_code(source_language)}",
        f"Target languages: {', '.join(display_locale_codes(table.target_languages(source_language))) or 'None'}",
        f"Total keys: {summary['total_keys']}",
        f"Total issues: {summary['total_issues']}",
        f"Critical: {summary['critical_issues']}",
        f"Warning: {summary['warning_issues']}",
        f"Info: {summary['info_issues']}",
        f"Health score: {summary['health_score']}/100",
        f"Release gate: {summary['release_gate']} - {release_gate_explanation(str(summary['release_gate']))}",
    ]
    if baseline_result:
        lines.extend(
            [
                f"Known issues: {baseline_result['known_count']}",
                f"New issues: {baseline_result['new_count']}",
                f"New critical issues: {baseline_result['new_critical_count']}",
            ]
        )
    lines.extend(["", "Top fixes:"])

    if not ordered_issues:
        lines.append("No issues found.")
    else:
        lines.extend(_format_text_issue(issue) for issue in ordered_issues)
    return "\n".join(lines)


def _resolve_source_language(table: LocalizationTable, requested_source: str | None) -> str | None:
    if requested_source:
        return resolve_locale(table.languages, requested_source)
    return choose_default_source_locale(table.languages)


def _format_text_issue(issue: Issue) -> str:
    location = issue.key
    if issue.locale:
        location = f"{location} / {normalize_locale_code(issue.locale)}"
    return f"[{issue.severity.value}] {location} - {issue.check}: {issue.message} Suggestion: {issue.suggestion}"


def _issue_to_json(issue: Issue) -> dict[str, str]:
    record = issue.model_dump()
    record["severity"] = issue.severity.value
    record["locale"] = normalize_locale_code(issue.locale)
    return record


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
