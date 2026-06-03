from localint.locales import (
    choose_default_source_locale,
    is_locale_like,
    language_display_name,
    locale_label,
    normalize_locale_code,
    resolve_locale,
    rtl_locales,
)


def test_normalizes_underscore_locale_for_display():
    assert normalize_locale_code("en_US") == "en-US"
    assert normalize_locale_code("pt_BR") == "pt-BR"


def test_recognizes_common_locale_variants():
    assert is_locale_like("en-US")
    assert is_locale_like("pt_PT")
    assert is_locale_like("zh-Hant")
    assert is_locale_like("id")


def test_language_display_names_are_lightweight_and_safe():
    assert language_display_name("en") == "English"
    assert language_display_name("tr") == "Turkish"
    assert language_display_name("zh-CN") == "Chinese (Simplified)"
    assert language_display_name("pt-BR") == "Portuguese (Brazil)"
    assert language_display_name("zz") == "zz"
    assert locale_label("he") == "he \u2014 Hebrew"


def test_source_default_prefers_english_variants_then_first_locale():
    assert choose_default_source_locale(["tr", "en-US", "fr"]) == "en-US"
    assert choose_default_source_locale(["tr", "es"]) == "tr"


def test_resolve_locale_matches_hyphen_and_underscore_variants_only():
    assert resolve_locale(["en_US", "tr"], "en-US") == "en_US"
    assert resolve_locale(["en-US", "tr"], "en_US") == "en-US"
    assert resolve_locale(["en-US", "tr"], "en") is None


def test_rtl_locale_detection_uses_language_code():
    assert rtl_locales(["en", "ar", "he-IL", "pt-BR"]) == ["ar", "he-IL"]
