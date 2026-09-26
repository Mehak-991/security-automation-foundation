import json
from pathlib import Path

from app.prompt_guard import detect_prompt_injection


BASE_DIR = Path(__file__).resolve().parents[2]

FIXTURE = (
    BASE_DIR
    / "tests"
    / "fixtures"
    / "day6"
    / "prompt_injection_cases.json"
)

OUTPUT = (
    BASE_DIR
    / "reports"
    / "day6"
    / "injection_test_report.json"
)


def main():
    cases = json.loads(
        FIXTURE.read_text(encoding="utf-8")
    )

    results = []

    for case in cases:
        detected, reason = detect_prompt_injection(
            case["text"]
        )

        results.append({
            "id": case["id"],
            "detected": detected,
            "expected": True,
            "result": "PASS" if detected else "FAIL",
            "reason": reason,
        })

    passed = sum(
        1
        for item in results
        if item["result"] == "PASS"
    )

    report = {
        "total_cases": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "results": results,
    }

    OUTPUT.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8",
    )

    print(
        f"Prompt-injection cases : {len(results)}"
    )
    print(
        f"Passed                 : {passed}"
    )
    print(
        f"Failed                 : {len(results) - passed}"
    )


if __name__ == "__main__":
    main()
