"""
Create an evidence manifest for a saved scanner run.
"""

import json
from pathlib import Path

from app.evidence_manager import create_manifest


PROJECT_ROOT = Path(__file__).resolve().parents[1]

EVIDENCE_FILE = (
    PROJECT_ROOT
    / "evidence"
    / "runs"
    / "RUN-20260922-104820_127_0_0_1.json"
)

MANIFEST_FILE = (
    PROJECT_ROOT
    / "evidence"
    / "manifests"
    / "RUN-20260922-104820_manifest.json"
)


def main() -> None:
    """Read saved evidence and create its manifest."""

    with EVIDENCE_FILE.open("r", encoding="utf-8") as file:
        evidence = json.load(file)

    create_manifest(
        run_id=evidence["run_id"],
        target=evidence["target"],
        command=evidence["command"],
        tool_version=evidence["tool_version"],
        scope="local-lab",
        operator="intern-lab",
        evidence_file=EVIDENCE_FILE,
        manifest_file=MANIFEST_FILE,
    )

    print("Manifest created:", MANIFEST_FILE)
    print("Evidence file:", EVIDENCE_FILE)
    print("Manifest creation: PASS")


if __name__ == "__main__":
    main()
