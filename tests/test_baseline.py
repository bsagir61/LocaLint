from localint.baseline import compare_to_baseline, load_baseline, write_baseline
from localint.models import Issue, Severity


def test_baseline_write_and_compare_detects_known_and_new(tmp_path):
    known_issue = Issue(
        severity=Severity.CRITICAL,
        key="START",
        locale="tr",
        check="Missing translation",
        message="Target translation is missing.",
    )
    new_issue = Issue(
        severity=Severity.WARNING,
        key="EXIT",
        locale="tr",
        check="Suspicious untranslated text",
        message="Target text is identical to the source text.",
    )
    baseline_path = tmp_path / "baseline.json"

    write_baseline(baseline_path, [known_issue])
    fingerprints = load_baseline(baseline_path)
    result = compare_to_baseline([known_issue, new_issue], fingerprints)

    assert result["known_count"] == 1
    assert result["new_count"] == 1
    assert result["new_critical_count"] == 0
