from localint.parsers import parse_csv, parse_json


def test_csv_parser_reads_languages_rows_and_duplicates():
    data = b"key,en,tr\nSTART,Start,Basla\nSTART,Start again,Yeniden basla\n"

    table = parse_csv(data, source_name="test.csv")

    assert table.languages == ["en", "tr"]
    assert table.total_keys == 2
    assert table.rows[0].key == "START"
    assert table.rows[0].translations["tr"] == "Basla"
    assert table.duplicate_keys == ["START"]


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
