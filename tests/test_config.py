from localint.config import init_config, load_config


def test_init_config_creates_safe_starter_file(tmp_path):
    config_path = tmp_path / ".localint.toml"

    init_config(config_path)

    text = config_path.read_text(encoding="utf-8")
    assert '[source]' in text
    assert 'language = "en"' in text
    assert "secret" not in text.lower()


def test_load_config_reads_source_length_and_checks(tmp_path):
    config_path = tmp_path / ".localint.toml"
    config_path.write_text(
        """
[source]
language = "en"

[checks]
missing_translation = true
placeholder_mismatch = false

[length]
warning_ratio = 2.0
""".strip(),
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config.source_language == "en"
    assert config.length_warning_ratio == 2.0
    assert "missing_translation" in config.enabled_checks
    assert "placeholder_mismatch" not in config.enabled_checks
