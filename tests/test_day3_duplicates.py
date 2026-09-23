from parsers.normalizer import deduplicate_findings


def test_duplicate_findings_are_merged_and_traceability_is_preserved():
    finding_json = {
        "title": "Missing Security Header",
        "asset": "127.0.0.1",
        "endpoint": "/",
        "severity": "Medium",
        "cvss": 5.3,
        "cwe": "CWE-693",
        "evidence": "Header missing in synthetic response.",
        "impact": "Missing security controls may increase browser-side exposure.",
        "remediation": "Configure the required security header.",
        "references": [
            "https://cwe.mitre.org/data/definitions/693.html"
        ],
        "status": "Open",
        "traceability_ids": ["TRC-JSON-003"],
        "sources": [
            {
                "format": "JSON",
                "record_id": "JSON-003",
                "raw_record": {
                    "title": "Missing Security Header"
                }
            }
        ],
    }

    finding_xml = {
        "title": "Missing Security Header",
        "asset": "127.0.0.1",
        "endpoint": "/",
        "severity": "Medium",
        "cvss": 5.3,
        "cwe": "CWE-693",
        "evidence": "Same synthetic finding from XML source.",
        "impact": "Same synthetic impact.",
        "remediation": "Configure the required security header.",
        "references": [
            "https://cwe.mitre.org/data/definitions/693.html"
        ],
        "status": "Open",
        "traceability_ids": ["TRC-XML-003"],
        "sources": [
            {
                "format": "XML",
                "record_id": "XML-003",
                "raw_record": {
                    "title": "Missing Security Header"
                }
            }
        ],
    }

    result = deduplicate_findings(
        [finding_json, finding_xml]
    )

    assert len(result) == 1

    merged = result[0]

    assert "TRC-JSON-003" in merged["traceability_ids"]
    assert "TRC-XML-003" in merged["traceability_ids"]

    assert len(merged["sources"]) == 2
