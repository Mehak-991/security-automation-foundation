import pytest

from app.prioritizer import (
    build_duplicate_key,
    calculate_business_priority,
    requires_human_review,
    severity_from_cvss,
)


def test_duplicate_key_is_deterministic():
    finding = {
        "asset": "127.0.0.1",
        "endpoint": "/login",
        "issue_type": "weak-authentication",
    }

    first = build_duplicate_key(finding)
    second = build_duplicate_key(dict(finding))

    assert first == second
    assert first.as_string() == "127.0.0.1|/login|weak-authentication"


@pytest.mark.parametrize(
    ("cvss", "expected"),
    [
        (0.0, "None"),
        (3.9, "Low"),
        (4.0, "Medium"),
        (6.9, "Medium"),
        (7.0, "High"),
        (8.9, "High"),
        (9.0, "Critical"),
        (10.0, "Critical"),
    ],
)
def test_cvss_severity_rules(cvss, expected):
    assert severity_from_cvss(cvss) == expected


def test_invalid_cvss_is_rejected():
    with pytest.raises(ValueError):
        severity_from_cvss(10.1)


def test_business_priority_is_deterministic():
    finding = {
        "asset_importance": "critical",
        "exploitability": "confirmed",
        "exposure": "internet",
    }

    assert calculate_business_priority(finding) == 6


def test_ai_suggested_result_requires_review():
    finding = {
        "ai_suggested": True,
    }

    assert requires_human_review(finding) is True


def test_uncertain_result_requires_review():
    finding = {
        "uncertain_severity": True,
    }

    assert requires_human_review(finding) is True


def test_clear_result_does_not_require_review():
    finding = {
        "ai_suggested": False,
        "uncertain_severity": False,
        "uncertain_business_priority": False,
    }

    assert requires_human_review(finding) is False
from app.prioritizer import deduplicate_findings


def test_duplicate_findings_are_removed():
    findings = [
        {
            "asset": "127.0.0.1",
            "endpoint": "/login",
            "issue_type": "weak-authentication",
        },
        {
            "asset": "127.0.0.1",
            "endpoint": "/login",
            "issue_type": "weak-authentication",
        },
        {
            "asset": "127.0.0.1",
            "endpoint": "/search",
            "issue_type": "xss",
        },
    ]

    unique, duplicate_count = deduplicate_findings(findings)

    assert len(unique) == 2
    assert duplicate_count == 1


def test_different_endpoint_is_not_duplicate():
    findings = [
        {
            "asset": "127.0.0.1",
            "endpoint": "/login",
            "issue_type": "xss",
        },
        {
            "asset": "127.0.0.1",
            "endpoint": "/search",
            "issue_type": "xss",
        },
    ]

    unique, duplicate_count = deduplicate_findings(findings)

    assert len(unique) == 2
    assert duplicate_count == 0


def test_different_issue_type_is_not_duplicate():
    findings = [
        {
            "asset": "127.0.0.1",
            "endpoint": "/login",
            "issue_type": "xss",
        },
        {
            "asset": "127.0.0.1",
            "endpoint": "/login",
            "issue_type": "weak-authentication",
        },
    ]

    unique, duplicate_count = deduplicate_findings(findings)

    assert len(unique) == 2
    assert duplicate_count == 0


def test_duplicate_count_is_preserved():
    findings = [
        {
            "asset": "127.0.0.1",
            "endpoint": "/login",
            "issue_type": "xss",
        },
        {
            "asset": "127.0.0.1",
            "endpoint": "/login",
            "issue_type": "xss",
        },
        {
            "asset": "127.0.0.1",
            "endpoint": "/login",
            "issue_type": "xss",
        },
    ]

    unique, duplicate_count = deduplicate_findings(findings)

    assert len(unique) == 1
    assert duplicate_count == 2
    assert unique[0]["duplicate_count"] == 2
def test_cvss_lower_boundary():
    assert severity_from_cvss(0.0) == "None"


def test_cvss_upper_boundary():
    assert severity_from_cvss(10.0) == "Critical"


def test_negative_cvss_is_rejected():
    with pytest.raises(ValueError):
        severity_from_cvss(-0.1)


def test_missing_business_context_uses_safe_defaults():
    finding = {}

    assert calculate_business_priority(finding) == 0


def test_uncertain_business_priority_requires_review():
    finding = {
        "uncertain_business_priority": True,
    }

    assert requires_human_review(finding) is True
