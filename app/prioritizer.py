from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class FindingKey:
    """Deterministic identity for a security finding."""

    asset: str
    endpoint: str
    issue_type: str

    def as_string(self) -> str:
        return f"{self.asset}|{self.endpoint}|{self.issue_type}"


def build_duplicate_key(finding: dict[str, Any]) -> FindingKey:
    """Build a deterministic key from the required finding fields."""

    return FindingKey(
        asset=str(finding["asset"]).strip(),
        endpoint=str(finding["endpoint"]).strip(),
        issue_type=str(finding["issue_type"]).strip(),
    )


def severity_from_cvss(cvss: float) -> str:
    """Map a CVSS score to a transparent qualitative severity."""

    score = float(cvss)

    if not 0.0 <= score <= 10.0:
        raise ValueError("CVSS score must be between 0.0 and 10.0")

    if score == 0.0:
        return "None"
    if score <= 3.9:
        return "Low"
    if score <= 6.9:
        return "Medium"
    if score <= 8.9:
        return "High"

    return "Critical"


def requires_human_review(finding: dict[str, Any]) -> bool:
    """Return True when the result should not be treated as final automatically."""

    return bool(
        finding.get("ai_suggested", False)
        or finding.get("uncertain_severity", False)
        or finding.get("uncertain_business_priority", False)
    )


def calculate_business_priority(finding: dict[str, Any]) -> int:
    """
    Calculate a transparent business-priority score.

    The score is intentionally simple and explainable:
    asset importance + exploitability + exposure.
    """

    asset_scores = {
        "critical": 2,
        "important": 1,
        "normal": 0,
    }

    exploitability_scores = {
        "confirmed": 2,
        "suspected": 1,
        "unknown": 0,
    }

    exposure_scores = {
        "internet": 2,
        "internal": 1,
        "local": 0,
    }

    asset = str(finding.get("asset_importance", "normal")).lower()
    exploitability = str(
        finding.get("exploitability", "unknown")
    ).lower()
    exposure = str(finding.get("exposure", "local")).lower()

    return (
        asset_scores.get(asset, 0)
        + exploitability_scores.get(exploitability, 0)
        + exposure_scores.get(exposure, 0)
    )


def prioritize_finding(finding: dict[str, Any]) -> dict[str, Any]:
    """Return the finding with deterministic severity and priority metadata."""

    result = dict(finding)

    cvss = result.get("cvss")
    if cvss is not None:
        result["severity_from_cvss"] = severity_from_cvss(float(cvss))

    result["business_priority_score"] = calculate_business_priority(result)
    result["human_review_required"] = requires_human_review(result)

    return result
def deduplicate_findings(findings: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    """
    Remove duplicate findings using the deterministic key:
    asset + endpoint + issue_type.

    The first occurrence is kept. Duplicate records are not silently
    discarded; their count is tracked in the retained finding.
    """

    unique_findings: dict[FindingKey, dict[str, Any]] = {}
    duplicate_count = 0

    for finding in findings:
        key = build_duplicate_key(finding)

        if key not in unique_findings:
            result = dict(finding)
            result["duplicate_count"] = 0
            unique_findings[key] = result
            continue

        unique_findings[key]["duplicate_count"] += 1
        duplicate_count += 1

    return list(unique_findings.values()), duplicate_count
