"""
Parsers for JSON, XML, and CSV security finding fixtures.

Each parser returns raw source records while preserving the original
record content for later normalization and traceability.
"""

import csv
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


class ParseError(ValueError):
    """Raised when scanner fixture data cannot be parsed safely."""


def _validate_mapping(record: dict[str, Any], source_format: str) -> dict[str, Any]:
    """Validate that a parsed record is a dictionary."""

    if not isinstance(record, dict):
        raise ParseError(
            f"{source_format} record must be an object/mapping."
        )

    return record


def parse_json_file(file_path: Path) -> list[dict[str, Any]]:
    """Parse JSON findings and preserve each raw source record."""

    try:
        with file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, json.JSONDecodeError) as exc:
        raise ParseError(
            f"Unable to parse JSON file: {file_path}"
        ) from exc

    if not isinstance(data, dict):
        raise ParseError("JSON root must be an object.")

    findings = data.get("findings")

    if not isinstance(findings, list):
        raise ParseError("JSON file must contain a 'findings' list.")

    records = []

    for index, finding in enumerate(findings, start=1):
        record = _validate_mapping(finding, "JSON")

        source_record_id = record.get(
            "source_record_id",
            f"JSON-{index:03d}",
        )

        records.append(
            {
                "source_format": "JSON",
                "source_record_id": str(source_record_id),
                "raw_record": dict(record),
            }
        )

    return records


def parse_xml_file(file_path: Path) -> list[dict[str, Any]]:
    """Parse XML findings and preserve each raw source record."""

    try:
        tree = ET.parse(file_path)
    except (OSError, ET.ParseError) as exc:
        raise ParseError(
            f"Unable to parse XML file: {file_path}"
        ) from exc

    root = tree.getroot()

    if root.tag != "findings":
        raise ParseError("XML root element must be 'findings'.")

    records = []

    for index, finding in enumerate(root.findall("finding"), start=1):
        record: dict[str, Any] = {}

        for child in finding:
            record[child.tag] = (child.text or "").strip()

        source_record_id = record.get(
            "source_record_id",
            f"XML-{index:03d}",
        )

        records.append(
            {
                "source_format": "XML",
                "source_record_id": str(source_record_id),
                "raw_record": dict(record),
            }
        )

    return records


def parse_csv_file(file_path: Path) -> list[dict[str, Any]]:
    """Parse CSV findings and preserve each raw source record."""

    try:
        with file_path.open(
            "r",
            encoding="utf-8",
            newline="",
        ) as file:
            reader = csv.DictReader(file)
            rows = list(reader)
    except OSError as exc:
        raise ParseError(
            f"Unable to read CSV file: {file_path}"
        ) from exc

    if not reader.fieldnames:
        raise ParseError("CSV file must contain a header row.")

    records = []

    for index, row in enumerate(rows, start=1):
        if not any(value not in (None, "") for value in row.values()):
            continue

        record = {
            str(key): (value or "").strip()
            for key, value in row.items()
            if key is not None
        }

        source_record_id = record.get(
            "source_record_id",
            f"CSV-{index:03d}",
        )

        records.append(
            {
                "source_format": "CSV",
                "source_record_id": str(source_record_id),
                "raw_record": dict(record),
            }
        )

    return records
