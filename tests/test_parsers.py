import pytest

from localint.parsers import KEY_FALLBACK_WARNING, ParserError, parse_csv, parse_json, parse_po, parse_upload


def test_csv_parser_reads_languages_rows_and_duplicates():
    data = b"key,en,tr\nSTART,Start,Basla\nSTART,Start again,Yeniden basla\n"

    table = parse_csv(data, source_name="test.csv")

    assert table.languages == ["en", "tr"]
    assert table.total_keys == 2
    assert table.rows[0].key == "START"
    assert table.rows[0].translations["tr"] == "Basla"
    assert table.duplicate_keys == ["START"]
    assert table.shape_warnings == []


def test_csv_parser_warns_on_utf8_bom():
    data = b"\xef\xbb\xbfkey,en,tr\nSTART,Start,Basla\n"

    table = parse_csv(data, source_name="bom.csv")

    assert table.encoding_warnings
    assert "without BOM" in table.encoding_warnings[0]


def test_json_parser_reads_flat_dictionary():
    data = b'{"START_GAME": {"en": "Start Game", "tr": "Oyuna Basla"}, "COINS": {"en": "Coins", "tr": "Jeton"}}'

    table = parse_json(data, source_name="sample.json")

    assert table.languages == ["en", "tr"]
    assert table.total_keys == 2
    assert table.rows[0].key == "START_GAME"
    assert table.rows[1].translations["tr"] == "Jeton"


def test_po_parser_reads_basic_entries_and_plural_forms():
    data = (
        b'msgctxt "menu"\n'
        b'msgid "Start Game"\n'
        b'msgstr "Oyuna Basla"\n'
        b"\n"
        b'msgid "You have {count} coin"\n'
        b'msgid_plural "You have {count} coins"\n'
        b'msgstr[0] "{count} jetonun var"\n'
        b'msgstr[1] "{count} jetonun var"\n'
    )

    table = parse_po(data, source_name="sample.po")

    assert table.file_format == "po"
    assert table.languages == ["source", "target"]
    assert table.total_keys == 3
    assert table.rows[0].key == "menu::Start Game"
    assert table.rows[0].translations["source"] == "Start Game"
    assert table.rows[0].translations["target"] == "Oyuna Basla"
    assert table.rows[1].key.endswith("[plural 0]")
    assert table.rows[2].key.endswith("[plural 1]")


def test_po_parser_handles_multiline_strings_and_escapes():
    data = (
        b'msgid ""\n'
        b'"Line one\\n"\n'
        b'"Line two"\n'
        b'msgstr ""\n'
        b'"Satir bir\\n"\n'
        b'"Satir iki"\n'
    )

    table = parse_po(data, source_name="multiline.po")

    assert table.rows[0].translations["source"] == "Line one\nLine two"
    assert table.rows[0].translations["target"] == "Satir bir\nSatir iki"


def test_po_parser_reports_duplicate_context_msgid():
    data = (
        b'msgctxt "menu"\nmsgid "Duplicate"\nmsgstr "Birinci"\n'
        b"\n"
        b'msgctxt "menu"\nmsgid "Duplicate"\nmsgstr "Ikinci"\n'
    )

    table = parse_po(data, source_name="duplicate.po")

    assert table.duplicate_keys == ["menu::Duplicate"]


def test_empty_csv_gets_clear_error():
    with pytest.raises(ParserError, match="CSV file is empty"):
        parse_csv(b"", source_name="empty.csv")


def test_csv_with_only_key_column_gets_clear_error():
    with pytest.raises(ParserError, match="at least one language column"):
        parse_csv(b"key\nSTART_GAME\n", source_name="only_key.csv")


def test_csv_without_key_column_uses_first_column_fallback():
    data = b"id,en,tr\nSTART,Start,Basla\n"

    table = parse_csv(data, source_name="missing_key.csv")

    assert table.languages == ["en", "tr"]
    assert table.rows[0].key == "START"
    assert table.rows[0].translations["tr"] == "Basla"
    assert table.shape_warnings == [KEY_FALLBACK_WARNING]


def test_csv_with_headers_but_no_rows_gets_clear_error():
    with pytest.raises(ParserError, match="headers but no rows"):
        parse_csv(b"key,en,tr\n", source_name="headers_only.csv")


def test_json_invalid_shape_gets_clear_error():
    with pytest.raises(ParserError, match="flat object"):
        parse_json(b'["START_GAME"]', source_name="bad.json")


def test_json_empty_object_gets_clear_error():
    with pytest.raises(ParserError, match="no localization entries"):
        parse_json(b"{}", source_name="empty.json")


def test_invalid_po_gets_clear_error():
    with pytest.raises(ParserError, match="no usable msgid/msgstr entries"):
        parse_po(b"# comments only\n", source_name="empty.po")


def test_unsupported_extension_gets_clear_error():
    with pytest.raises(ParserError, match="Unsupported file type"):
        parse_upload("strings.txt", b"START=Start")
