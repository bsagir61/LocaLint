from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path


DEFAULT_CONFIG_PATH = ".localint.toml"
DEFAULT_CONFIG_TEXT = """[source]
language = "en"

[gate]
fail_on = "critical"

[checks]
missing_translation = true
placeholder_mismatch = true
duplicate_keys = true
unchanged_text = true
length_expansion = true
line_break_mismatch = true
whitespace = true
punctuation = true
encoding = true

[length]
warning_ratio = 1.8
"""

CHECK_CONFIG_TO_ID = {
    "missing_translation": "missing_translation",
    "placeholder_mismatch": "placeholder_mismatch",
    "duplicate_keys": "duplicate_keys",
    "unchanged_text": "untranslated_text",
    "length_expansion": "length_risk",
    "line_break_mismatch": "line_break_mismatch",
    "whitespace": "whitespace",
    "punctuation": "punctuation_mismatch",
    "encoding": "csv_bom",
}


class ConfigError(ValueError):
    """Raised when a LocaLint config file is invalid."""


@dataclass(frozen=True)
class LocaLintConfig:
    source_language: str | None = None
    gate_fail_on: str | None = None
    enabled_checks: list[str] | None = None
    length_warning_ratio: float | None = None


def load_config(path: str | Path) -> LocaLintConfig:
    config_path = Path(path)
    try:
        payload = tomllib.loads(config_path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ConfigError(f"Could not read config file: {exc}") from exc
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(f"Could not parse config file: {exc}") from exc

    source_language = _optional_string(payload.get("source", {}), "language", "source.language")
    gate_fail_on = _optional_string(payload.get("gate", {}), "fail_on", "gate.fail_on")
    if gate_fail_on is not None and gate_fail_on not in {"critical", "new_critical"}:
        raise ConfigError("Config gate.fail_on must be 'critical' or 'new_critical'.")

    enabled_checks = _checks_from_config(payload.get("checks"))
    length_warning_ratio = _optional_number(payload.get("length", {}), "warning_ratio", "length.warning_ratio")
    if length_warning_ratio is not None and length_warning_ratio <= 0:
        raise ConfigError("Config length.warning_ratio must be greater than 0.")

    return LocaLintConfig(
        source_language=source_language,
        gate_fail_on=gate_fail_on,
        enabled_checks=enabled_checks,
        length_warning_ratio=length_warning_ratio,
    )


def init_config(path: str | Path = DEFAULT_CONFIG_PATH, force: bool = False) -> Path:
    config_path = Path(path)
    if config_path.exists() and not force:
        raise ConfigError(f"Config file already exists: {config_path}")
    try:
        config_path.write_text(DEFAULT_CONFIG_TEXT, encoding="utf-8", newline="")
    except OSError as exc:
        raise ConfigError(f"Could not write config file: {exc}") from exc
    return config_path


def _checks_from_config(checks_payload: object) -> list[str] | None:
    if checks_payload is None:
        return None
    if not isinstance(checks_payload, dict):
        raise ConfigError("Config checks section must be a table.")

    enabled = set(CHECK_CONFIG_TO_ID.values())
    for config_name, check_id in CHECK_CONFIG_TO_ID.items():
        if config_name not in checks_payload:
            continue
        value = checks_payload[config_name]
        if not isinstance(value, bool):
            raise ConfigError(f"Config checks.{config_name} must be true or false.")
        if value:
            enabled.add(check_id)
        else:
            enabled.discard(check_id)
    return sorted(enabled)


def _optional_string(section: object, key: str, label: str) -> str | None:
    if not isinstance(section, dict) or key not in section:
        return None
    value = section[key]
    if not isinstance(value, str):
        raise ConfigError(f"Config {label} must be a string.")
    return value


def _optional_number(section: object, key: str, label: str) -> float | None:
    if not isinstance(section, dict) or key not in section:
        return None
    value = section[key]
    if not isinstance(value, int | float):
        raise ConfigError(f"Config {label} must be a number.")
    return float(value)
