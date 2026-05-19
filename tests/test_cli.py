import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BROKEN_SAMPLE = ROOT / "sample_data" / "broken_sample.csv"


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "localint.cli", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_cli_basic_scan_returns_exit_code_0():
    result = run_cli(str(BROKEN_SAMPLE), "--source", "en")

    assert result.returncode == 0
    assert "LocaLint report" in result.stdout
    assert "Critical:" in result.stdout


def test_cli_fail_on_critical_returns_exit_code_1():
    result = run_cli(str(BROKEN_SAMPLE), "--source", "en", "--fail-on-critical")

    assert result.returncode == 1
    assert "LocaLint report" in result.stdout


def test_cli_invalid_file_returns_exit_code_2():
    result = run_cli("missing-file.csv")

    assert result.returncode == 2
    assert "Input file not found" in result.stderr


def test_cli_json_output_is_valid_json():
    result = run_cli(str(BROKEN_SAMPLE), "--source", "en", "--format", "json")

    payload = json.loads(result.stdout)
    assert result.returncode == 0
    assert payload["source_language"] == "en"
    assert payload["total_issues"] > 0
    assert isinstance(payload["issues"], list)


def test_cli_markdown_output_writes_file(tmp_path):
    output_path = tmp_path / "report.md"

    result = run_cli(str(BROKEN_SAMPLE), "--source", "en", "--format", "markdown", "--out", str(output_path))

    assert result.returncode == 0
    assert output_path.exists()
    assert "# LocaLint QA Report" in output_path.read_text(encoding="utf-8")
