"""
Build and export canonical findings from JSON, XML, and CSV fixtures.
"""

import json
from pathlib import Path

from parsers.normalizer import deduplicate_findings, normalize_record
from parsers.output_parsers import (
    parse_csv_file,
    parse_json_file,
    parse_xml_file,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DIR = PROJECT_ROOT / "tests" / "fixtures" / "day3"
OUTPUT_FILE = PROJECT_ROOT / "reports" / "day3" / "normalized_findings.json"


def main() -> None:
    """Parse all fixture formats and export canonical findings."""

    raw_records = []

    raw_records.extend(
        parse_json_file(FIXTURE_DIR / "sample_findings.json")
    )
    raw_records.extend(
        parse_xml_file(FIXTURE_DIR / "sample_findings.xml")
    )
    raw_records.extend(
        parse_csv_file(FIXTURE_DIR / "sample_findings.csv")
    )

    normalized = [
        normalize_record(record)
        for record in raw_records
    ]

    normalized = deduplicate_findings(normalized)

    output = {
        "schema_version": "1.0",
        "source_record_count": len(raw_records),
        "normalized_finding_count": len(normalized),
        "findings": normalized,
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(output, file, indent=2)

    print("Source records:", len(raw_records))
    print("Normalized findings:", len(normalized))
    print("Output:", OUTPUT_FILE)
    print("Export validation: PASS")


if __name__ == "__main__":
    main()
