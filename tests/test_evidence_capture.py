import json
from pathlib import Path

import app.evidence_manager as evidence_manager
from app.evidence_manager import (
    create_manifest,
    redact_secrets,
    sha256_file,
)


def test_sha256_is_consistent(tmp_path):
    evidence_file = tmp_path / "evidence.txt"

    evidence_file.write_text(
        "sample evidence",
        encoding="utf-8",
    )

    first_hash = sha256_file(evidence_file)
    second_hash = sha256_file(evidence_file)

    assert first_hash == second_hash
    assert len(first_hash) == 64


def test_secret_redaction():
    sample = (
        "Authorization: Bearer TEST_TOKEN "
        "password=demo_password "
        "api_key=DEMO_API_KEY"
    )

    redacted = redact_secrets(sample)

    assert "TEST_TOKEN" not in redacted
    assert "demo_password" not in redacted
    assert "DEMO_API_KEY" not in redacted

    assert redacted.count("[REDACTED]") == 3


def test_manifest_contains_required_metadata(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(
        evidence_manager,
        "PROJECT_ROOT",
        tmp_path,
    )

    evidence_file = tmp_path / "evidence.json"
    manifest_file = tmp_path / "manifest.json"

    evidence_file.write_text(
        '{"sample": "evidence"}',
        encoding="utf-8",
    )

    create_manifest(
        run_id="RUN-DAY4-001",
        target="127.0.0.1",
        command=[
            "nmap",
            "-sT",
            "-n",
            "-p",
            "1-1000",
            "127.0.0.1",
        ],
        tool_version="Nmap version 7.99",
        scope="local-lab",
        operator="intern-lab",
        evidence_file=evidence_file,
        manifest_file=manifest_file,
    )

    assert manifest_file.exists()

    with manifest_file.open(
        "r",
        encoding="utf-8",
    ) as file:
        manifest = json.load(file)

    required_fields = {
        "run_id",
        "timestamp",
        "target",
        "command",
        "tool_version",
        "scope",
        "operator",
        "evidence_file",
        "sha256",
    }

    assert required_fields.issubset(
        manifest.keys()
    )

    assert manifest["run_id"] == "RUN-DAY4-001"
    assert manifest["target"] == "127.0.0.1"
    assert manifest["scope"] == "local-lab"


def test_manifest_hash_matches_evidence(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(
        evidence_manager,
        "PROJECT_ROOT",
        tmp_path,
    )

    evidence_file = tmp_path / "evidence.txt"
    manifest_file = tmp_path / "manifest.json"

    evidence_file.write_text(
        "reproducible evidence",
        encoding="utf-8",
    )

    create_manifest(
        run_id="RUN-DAY4-002",
        target="127.0.0.1",
        command=[
            "nmap",
            "-sT",
            "127.0.0.1",
        ],
        tool_version="Nmap version 7.99",
        scope="local-lab",
        operator="intern-lab",
        evidence_file=evidence_file,
        manifest_file=manifest_file,
    )

    with manifest_file.open(
        "r",
        encoding="utf-8",
    ) as file:
        manifest = json.load(file)

    assert manifest["sha256"] == sha256_file(
        evidence_file
    )


def test_reference_fixture_matches_saved_evidence():
    source = Path(
        "evidence/runs/"
        "RUN-20260922-104820_127_0_0_1.json"
    )

    fixture = Path(
        "tests/fixtures/day4/"
        "reference_evidence.json"
    )

    assert source.exists()
    assert fixture.exists()

    assert sha256_file(source) == sha256_file(
        fixture
    )
