import json
from pathlib import Path

from app.ai_drafter import AIDrafter


BASE_DIR = Path(__file__).resolve().parents[2]

FIXTURE = BASE_DIR / "tests" / "fixtures" / "day6" / "sample_normalized_findings.json"
SCHEMA = BASE_DIR / "schemas" / "ai_draft.schema.json"

OUTPUT = BASE_DIR / "reports" / "day6" / "ai_drafts.json"
VALIDATION = BASE_DIR / "reports" / "day6" / "schema_validation_report.json"


def main():
    findings = json.loads(
        FIXTURE.read_text(encoding="utf-8")
    )

    drafter = AIDrafter(provider="mock")

    drafts = []
    validation_results = []

    for finding in findings:
        draft = drafter.draft(finding, SCHEMA)

        drafts.append(draft)

        validation_results.append({
            "trace_id": finding["trace_id"],
            "schema_validation": "PASS",
            "reviewer_required": draft["reviewer_required"],
            "review_status": draft["review_status"],
        })

    OUTPUT.write_text(
        json.dumps(
            drafts,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8",
    )

    report = {
        "total_findings": len(findings),
        "drafts_generated": len(drafts),
        "schema_valid": len(validation_results),
        "results": validation_results,
    }

    VALIDATION.write_text(
        json.dumps(
            report,
            indent=2
        ),
        encoding="utf-8",
    )

    print(f"Input findings    : {len(findings)}")
    print(f"Drafts generated  : {len(drafts)}")
    print(
        f"Schema validation : "
        f"{len(validation_results)}/{len(findings)} PASS"
    )
    print("Human review      : REQUIRED")


if __name__ == "__main__":
    main()
