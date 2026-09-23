from pathlib import Path

from parsers.output_parsers import (
    parse_csv_file,
    parse_json_file,
    parse_xml_file,
)


BASE_DIR = Path("tests/fixtures/day3")


def test_json_parser_reads_two_records():
    records = parse_json_file(BASE_DIR / "sample_findings.json")

    assert len(records) == 2
    assert records[0]["source_format"] == "JSON"
    assert records[0]["source_record_id"] == "JSON-001"
    assert records[1]["source_record_id"] == "JSON-002"


def test_xml_parser_reads_two_records():
    records = parse_xml_file(BASE_DIR / "sample_findings.xml")

    assert len(records) == 2
    assert records[0]["source_format"] == "XML"
    assert records[0]["source_record_id"] == "XML-001"
    assert records[1]["source_record_id"] == "XML-002"


def test_csv_parser_reads_one_record():
    records = parse_csv_file(BASE_DIR / "sample_findings.csv")

    assert len(records) == 1
    assert records[0]["source_format"] == "CSV"
    assert records[0]["source_record_id"] == "CSV-001"


def test_parsers_preserve_raw_source_records():
    json_records = parse_json_file(
        BASE_DIR / "sample_findings.json"
    )

    xml_records = parse_xml_file(
        BASE_DIR / "sample_findings.xml"
    )

    csv_records = parse_csv_file(
        BASE_DIR / "sample_findings.csv"
    )

    assert "title" in json_records[0]["raw_record"]
    assert "title" in xml_records[0]["raw_record"]
    assert "title" in csv_records[0]["raw_record"]
