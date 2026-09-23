from pathlib import Path

import pytest

from parsers.normalizer import NormalizationError, normalize_record
from parsers.output_parsers import (
    ParseError,
    parse_json_file,
    parse_xml_file,
)


BASE_DIR = Path("tests/fixtures/day3")


def test_malformed_json_is_rejected():
    with pytest.raises(ParseError, match="Unable to parse JSON"):
        parse_json_file(BASE_DIR / "malformed.json")


def test_malformed_xml_is_rejected():
    with pytest.raises(ParseError, match="Unable to parse XML"):
        parse_xml_file(BASE_DIR / "malformed.xml")


def test_missing_required_field_is_rejected():
    record = {
        "source_format": "JSON",
        "source_record_id": "JSON-003",
        "raw_record": {
            "title": "Missing Severity",
            "asset": "127.0.0.1",
            "endpoint": "/test",
            "cvss": 5.0,
            "cwe": "CWE-200",
            "evidence": "Synthetic evidence",
            "impact": "Synthetic impact",
            "remediation": "Synthetic remediation",
            "references": [
                "https://example.com/reference"
            ],
            "status": "Open"
        }
    }

    with pytest.raises(
        NormalizationError,
        match="Missing required field: severity",
    ):
        normalize_record(record)


def test_invalid_cvss_is_rejected():
    record = {
        "source_format": "JSON",
        "source_record_id": "JSON-004",
        "raw_record": {
            "title": "Invalid CVSS",
            "asset": "127.0.0.1",
            "endpoint": "/test",
            "severity": "High",
            "cvss": 15.0,
            "cwe": "CWE-200",
            "evidence": "Synthetic evidence",
            "impact": "Synthetic impact",
            "remediation": "Synthetic remediation",
            "references": [
                "https://example.com/reference"
            ],
            "status": "Open"
        }
    }

    with pytest.raises(
        NormalizationError,
        match="CVSS must be between 0 and 10",
    ):
        normalize_record(record)
