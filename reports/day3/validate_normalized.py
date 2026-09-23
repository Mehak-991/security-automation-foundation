"""
Validate exported canonical findings against the JSON Schema.
"""

import json
from pathlib import Path

from jsonschema import Draft202012Validator


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SCHEMA_FILE = PROJECT_ROOT / "schemas" / "finding.schema.json"
FINDINGS_FILE = (
    PROJECT_ROOT / "reports" / "day3" / "normalized_findings.json"
)


def main() -> None:
    """Validate every normalized finding."""

    with SCHEMA_FILE.open("r", encoding="utf-8") as file:
        schema = json.load(file)

    with FINDINGS_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    findings = data.get("findings")

    if not isinstance(findings, list):
        raise ValueError("Normalized output must contain a findings list.")

    validator = Draft202012Validator(schema)

    valid_count = 0

    for index, finding in enumerate(findings, start=1):
        errors = sorted(
            validator.iter_errors(finding),
            key=lambda error: list(error.path),
        )

        if errors:
            print(f"Finding {index}: INVALID")

            for error in errors:
                location = ".".join(str(part) for part in error.path)
                location = location or "<root>"
                print(f"  {location}: {error.message}")

            continue

        print(f"Finding {index}: VALID")
        valid_count += 1

    print(f"Validated findings: {len(findings)}")
    print(f"Valid findings: {valid_count}")

    if valid_count != len(findings):
        raise SystemExit(1)

    print("Schema validation: PASS")


if __name__ == "__main__":
    main()
