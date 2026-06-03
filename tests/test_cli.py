import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BROKEN_SAMPLE = ROOT / "sample_data" / "broken_sample.csv"
PO_SAMPLE = ROOT / "sample_data" / "sample.po"


def run_cli(*args: str, cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    return subprocess.run(
        [sys.executable, "-m", "localint.cli", *args],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_cli_basic_scan_returns_exit_code_0():
    result = run_cli(str(BROKEN_SAMPLE), "--source", "en")

    assert result.returncode == 0
    assert "LocaLint report" in result.stdout
    assert "Critical:" in result.stdout
    assert "Release gate: BLOCK" in result.stdout


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
    assert payload["release_gate"] == "BLOCK"
    assert payload["total_issues"] > 0
    assert isinstance(payload["issues"], list)


def test_cli_po_scan_returns_exit_code_0():
    result = run_cli(str(PO_SAMPLE))

    assert result.returncode == 0
    assert "LocaLint report" in result.stdout
    assert "Source language: source" in result.stdout


def test_cli_po_markdown_output_writes_file(tmp_path):
    output_path = tmp_path / "po_report.md"

    result = run_cli(str(PO_SAMPLE), "--format", "markdown", "--out", str(output_path))

    assert result.returncode == 0
    assert output_path.exists()
    assert "# LocaLint QA Report" in output_path.read_text(encoding="utf-8")


def test_cli_markdown_output_writes_file(tmp_path):
    output_path = tmp_path / "report.md"

    result = run_cli(str(BROKEN_SAMPLE), "--source", "en", "--format", "markdown", "--out", str(output_path))

    assert result.returncode == 0
    assert output_path.exists()
    assert "# LocaLint QA Report" in output_path.read_text(encoding="utf-8")


def test_cli_version_returns_050():
    result = run_cli("--version")

    assert result.returncode == 0
    assert result.stdout.strip() == "LocaLint 0.5.0"


def test_cli_init_config_creates_file(tmp_path):
    result = run_cli("--init-config", cwd=tmp_path)

    assert result.returncode == 0
    assert (tmp_path / ".localint.toml").exists()


def test_cli_config_can_default_source_language(tmp_path):
    config_path = tmp_path / ".localint.toml"
    config_path.write_text('[source]\nlanguage = "en"\n', encoding="utf-8")

    result = run_cli(str(BROKEN_SAMPLE), "--config", str(config_path))

    assert result.returncode == 0
    assert "Source language: en" in result.stdout


def test_cli_accepts_source_locale_variant(tmp_path):
    sample_path = tmp_path / "variant.csv"
    sample_path.write_text("key,en_US,tr_TR\nSTART,Start,Basla\n", encoding="utf-8")

    result = run_cli(str(sample_path), "--source", "en-US")

    assert result.returncode == 0
    assert "Source language: en-US" in result.stdout
    assert "Target languages: tr-TR" in result.stdout


def test_cli_config_accepts_source_locale_variant(tmp_path):
    sample_path = tmp_path / "variant.csv"
    config_path = tmp_path / ".localint.toml"
    sample_path.write_text("key,en_US,tr_TR\nSTART,Start,Basla\n", encoding="utf-8")
    config_path.write_text('[source]\nlanguage = "en-US"\n', encoding="utf-8")

    result = run_cli(str(sample_path), "--config", str(config_path))

    assert result.returncode == 0
    assert "Source language: en-US" in result.stdout


def test_cli_missing_requested_source_lists_available_locales(tmp_path):
    sample_path = tmp_path / "missing-source.csv"
    sample_path.write_text("key,tr,es\nSTART,Basla,Iniciar\n", encoding="utf-8")

    result = run_cli(str(sample_path), "--source", "en")

    assert result.returncode == 2
    assert "Source language 'en' was not found. Available locales: tr, es." in result.stderr


def test_cli_write_and_compare_baseline(tmp_path):
    baseline_path = tmp_path / ".localint-baseline.json"

    write_result = run_cli(str(BROKEN_SAMPLE), "--source", "en", "--write-baseline", str(baseline_path))
    compare_result = run_cli(str(BROKEN_SAMPLE), "--source", "en", "--baseline", str(baseline_path))

    assert write_result.returncode == 0
    assert baseline_path.exists()
    assert compare_result.returncode == 0
    assert "Known issues: 10" in compare_result.stdout
    assert "New issues: 0" in compare_result.stdout


def test_cli_fail_on_new_critical_ignores_known_critical_issues(tmp_path):
    baseline_path = tmp_path / ".localint-baseline.json"

    write_result = run_cli(str(BROKEN_SAMPLE), "--source", "en", "--write-baseline", str(baseline_path))
    compare_result = run_cli(
        str(BROKEN_SAMPLE),
        "--source",
        "en",
        "--baseline",
        str(baseline_path),
        "--fail-on-new-critical",
    )

    assert write_result.returncode == 0
    assert compare_result.returncode == 0


def test_cli_fail_on_new_critical_returns_1_for_new_critical(tmp_path):
    baseline_path = tmp_path / ".localint-baseline.json"
    baseline_path.write_text('{"version": 1, "issues": []}', encoding="utf-8")

    result = run_cli(str(BROKEN_SAMPLE), "--source", "en", "--baseline", str(baseline_path), "--fail-on-new-critical")

    assert result.returncode == 1
    assert "New critical issues: 5" in result.stdout
