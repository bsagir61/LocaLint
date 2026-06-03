from __future__ import annotations

import hashlib
import json
from pathlib import Path

from localint.models import Issue, Severity
from localint.report import sort_issues_for_action


BASELINE_VERSION = 1


class BaselineError(ValueError):
    """Raised when a baseline file cannot be read or written."""


def issue_fingerprint(issue: Issue) -> str:
    payload = {
        "severity": issue.severity.value,
        "check": issue.check,
        "key": issue.key,
        "locale": issue.locale,
        "message": _normalize_message(issue.message),
    }
    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def issue_record(issue: Issue) -> dict[str, str]:
    return {
        "fingerprint": issue_fingerprint(issue),
        "severity": issue.severity.value,
        "check": issue.check,
        "key": issue.key,
        "locale": issue.locale,
        "message": issue.message,
    }


def build_baseline(issues: list[Issue]) -> dict[str, object]:
    return {
        "version": BASELINE_VERSION,
        "issues": [issue_record(issue) for issue in sort_issues_for_action(issues)],
    }


def write_baseline(path: str | Path, issues: list[Issue]) -> None:
    target = Path(path)
    try:
        target.write_text(json.dumps(build_baseline(issues), indent=2, ensure_ascii=False), encoding="utf-8")
    except OSError as exc:
        raise BaselineError(f"Could not write baseline file: {exc}") from exc


def load_baseline(path: str | Path) -> set[str]:
    baseline_path = Path(path)
    try:
        payload = json.loads(baseline_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BaselineError(f"Could not read baseline file: {exc}") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("issues"), list):
        raise BaselineError("Invalid baseline file. Expected a JSON object with an issues list.")

    fingerprints: set[str] = set()
    for record in payload["issues"]:
        if not isinstance(record, dict) or not isinstance(record.get("fingerprint"), str):
            raise BaselineError("Invalid baseline file. Each issue needs a fingerprint.")
        fingerprints.add(record["fingerprint"])
    return fingerprints


def compare_to_baseline(issues: list[Issue], baseline_fingerprints: set[str]) -> dict[str, object]:
    known: list[Issue] = []
    new: list[Issue] = []
    for issue in issues:
        if issue_fingerprint(issue) in baseline_fingerprints:
            known.append(issue)
        else:
            new.append(issue)
    return {
        "known_issues": known,
        "new_issues": new,
        "known_count": len(known),
        "new_count": len(new),
        "new_critical_count": sum(1 for issue in new if issue.severity == Severity.CRITICAL),
    }


def _normalize_message(message: str) -> str:
    return " ".join(message.split())
