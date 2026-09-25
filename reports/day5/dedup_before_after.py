import json
from pathlib import Path

from app.prioritizer import deduplicate_findings


INPUT_FILE = Path("tests/fixtures/day5/sample_findings.json")


def main() -> None:
    findings = json.loads(INPUT_FILE.read_text())

    unique_findings, duplicate_count = deduplicate_findings(findings)

    print("Before deduplication :", len(findings))
    print("After deduplication  :", len(unique_findings))
    print("Duplicates removed   :", duplicate_count)

    print("\nRemaining findings:")
    for finding in unique_findings:
        print(
            f"- {finding['asset']} | "
            f"{finding['endpoint']} | "
            f"{finding['issue_type']} | "
            f"duplicates={finding['duplicate_count']}"
        )


if __name__ == "__main__":
    main()
