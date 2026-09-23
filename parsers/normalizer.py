"""
Canonical finding normalizer.

Converts parsed JSON, XML, and CSV records into the common
security finding structure defined by finding.schema.json.
"""

from copy import deepcopy
from typing import Any


REQUIRED_FIELDS = {
    "title",
    "asset",
    "endpoint",
    "severity",
    "cvss",
    "cwe",
    "evidence",
    "impact",
    "remediation",
    "references",
    "status",
}


class NormalizationError(ValueError):
    """Raised when a source record cannot be normalized safely."""


def _require_field(record: dict[str, Any], field: str) -> Any:
    """Return a required field or raise a clear normalization error."""

    value = record.get(field)

    if value is None or value == "":
        raise NormalizationError(
            f"Missing required field: {field}"
        )

    return value


def _parse_cvss(value: Any) -> float:
    """Convert a CVSS value to a numeric score."""

    try:
        score = float(value)
    except (TypeError, ValueError) as exc:
        raise NormalizationError(
            f"Invalid CVSS value: {value}"
        ) from exc

    if not 0 <= score <= 10:
        raise NormalizationError(
            f"CVSS must be between 0 and 10: {score}"
        )

    return score


def _parse_references(value: Any) -> list[str]:
    """Normalize references from string or list form."""

    if isinstance(value, list):
        references = [str(item).strip() for item in value if str(item).strip()]
    else:
        references = [str(value).strip()] if str(value).strip() else []

    return references


def _traceability_id(source_format: str, source_record_id: str) -> str:
    """Convert a source record identifier into a canonical trace ID."""

    prefix = source_format.upper()

    if prefix not in {"JSON", "XML", "CSV"}:
        raise NormalizationError(
            f"Unsupported source format: {source_format}"
        )

    try:
        number = int(source_record_id.rsplit("-", 1)[1])
    except (ValueError, IndexError) as exc:
        raise NormalizationError(
            f"Invalid source record ID: {source_record_id}"
        ) from exc

    return f"TRC-{prefix}-{number:03d}"


def normalize_record(parsed_record: dict[str, Any]) -> dict[str, Any]:
    """Convert one parsed source record into a canonical finding."""

    source_format = str(parsed_record.get("source_format", "")).upper()
    source_record_id = str(parsed_record.get("source_record_id", ""))

    raw_record = parsed_record.get("raw_record")

    if not isinstance(raw_record, dict):
        raise NormalizationError(
            "Parsed record must contain a raw_record object."
        )

    title = _require_field(raw_record, "title")
    asset = _require_field(raw_record, "asset")
    endpoint = _require_field(raw_record, "endpoint")
    severity = _require_field(raw_record, "severity")
    cvss = _parse_cvss(_require_field(raw_record, "cvss"))
    cwe = _require_field(raw_record, "cwe")
    evidence = _require_field(raw_record, "evidence")
    impact = _require_field(raw_record, "impact")
    remediation = _require_field(raw_record, "remediation")
    references = _parse_references(
        _require_field(raw_record, "references")
    )
    status = _require_field(raw_record, "status")

    trace_id = _traceability_id(
        source_format,
        source_record_id,
    )

    source_snapshot = {
        "format": source_format,
        "record_id": source_record_id,
        "raw_record": deepcopy(raw_record),
    }

    return {
        "title": str(title).strip(),
        "asset": str(asset).strip(),
        "endpoint": str(endpoint).strip(),
        "severity": str(severity).strip(),
        "cvss": cvss,
        "cwe": str(cwe).strip(),
        "evidence": str(evidence).strip(),
        "impact": str(impact).strip(),
        "remediation": str(remediation).strip(),
        "references": references,
        "status": str(status).strip(),
        "traceability_ids": [trace_id],
        "sources": [source_snapshot],
    }


def _dedup_key(finding: dict[str, Any]) -> tuple[str, str, str]:
    """Create a stable key used for duplicate finding detection."""

    return (
        finding["title"].strip().lower(),
        finding["asset"].strip().lower(),
        finding["endpoint"].strip().lower(),
    )


def deduplicate_findings(
    findings: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Merge duplicate findings while preserving traceability."""

    merged: dict[tuple[str, str, str], dict[str, Any]] = {}

    for finding in findings:
        key = _dedup_key(finding)

        if key not in merged:
            merged[key] = deepcopy(finding)
            continue

        existing = merged[key]

        for trace_id in finding["traceability_ids"]:
            if trace_id not in existing["traceability_ids"]:
                existing["traceability_ids"].append(trace_id)

        existing_source_ids = {
            source["record_id"]
            for source in existing["sources"]
        }

        for source in finding["sources"]:
            if source["record_id"] not in existing_source_ids:
                existing["sources"].append(deepcopy(source))

    return list(merged.values())
