"""
Simple evidence capture utilities for the security automation workflow.
"""

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def sha256_file(file_path: Path) -> str:
    """Return the SHA-256 hash of a file."""

    digest = hashlib.sha256()

    with file_path.open("rb") as file:
        for chunk in iter(lambda: file.read(8192), b""):
            digest.update(chunk)

    return digest.hexdigest()


def redact_secrets(text: str) -> str:
    """Redact common token and password-like values."""

    patterns = [
        (
            r"(?i)(bearer\s+)[A-Za-z0-9._~+/=-]+",
            r"\1[REDACTED]",
        ),
        (
            r"(?i)(api[_-]?key\s*[:=]\s*)\S+",
            r"\1[REDACTED]",
        ),
        (
            r"(?i)(password\s*[:=]\s*)\S+",
            r"\1[REDACTED]",
        ),
    ]

    redacted = text

    for pattern, replacement in patterns:
        redacted = re.sub(pattern, replacement, redacted)

    return redacted


def write_redacted_copy(
    source_file: Path,
    destination_file: Path,
) -> None:
    """Create a redacted copy of a text evidence file."""

    content = source_file.read_text(encoding="utf-8")
    redacted = redact_secrets(content)

    destination_file.parent.mkdir(parents=True, exist_ok=True)
    destination_file.write_text(
        redacted,
        encoding="utf-8",
    )


def create_manifest(
    run_id: str,
    target: str,
    command: list[str],
    tool_version: str,
    scope: str,
    operator: str,
    evidence_file: Path,
    manifest_file: Path,
) -> None:
    """Create a manifest containing evidence metadata and file hash."""

    relative_evidence = str(
        evidence_file.resolve().relative_to(PROJECT_ROOT.resolve())
    )

    manifest = {
        "run_id": run_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "target": target,
        "command": command,
        "tool_version": tool_version,
        "scope": scope,
        "operator": operator,
        "evidence_file": relative_evidence,
        "sha256": sha256_file(evidence_file),
    }

    manifest_file.parent.mkdir(parents=True, exist_ok=True)

    with manifest_file.open("w", encoding="utf-8") as file:
        json.dump(manifest, file, indent=2)
