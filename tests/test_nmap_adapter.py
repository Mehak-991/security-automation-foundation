import json
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from adapters.nmap_adapter import NmapAdapter


def test_build_command_for_approved_target():
    adapter = NmapAdapter()

    command = adapter.build_command("127.0.0.1")

    assert command == [
        "nmap",
        "-sT",
        "-n",
        "-p",
        "1-1000",
        "127.0.0.1",
    ]


def test_unapproved_target_is_rejected_before_execution():
    adapter = NmapAdapter()

    with patch("adapters.nmap_adapter.subprocess.run") as mock_run:
        with pytest.raises(ValueError, match="Target is not approved"):
            adapter.scan("192.0.2.10", "RUN-TEST-REJECTED")

        mock_run.assert_not_called()


def test_successful_scan_creates_evidence_file():
    adapter = NmapAdapter()
    run_id = "RUN-TEST-SUCCESS"

    fake_result = type(
        "FakeResult",
        (),
        {
            "returncode": 0,
            "stdout": "Nmap test output",
            "stderr": "",
        },
    )()

    with patch.object(
        adapter,
        "_get_tool_version",
        return_value="Nmap version 7.99",
    ):
        with patch(
            "adapters.nmap_adapter.subprocess.run",
            return_value=fake_result,
        ):
            result = adapter.scan("127.0.0.1", run_id)

    assert result.return_code == 0
    assert result.timed_out is False
    assert result.tool_version == "Nmap version 7.99"

    evidence_path = Path(result.output_file)
    assert evidence_path.exists()

    with evidence_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    assert data["run_id"] == run_id
    assert data["target"] == "127.0.0.1"
    assert data["return_code"] == 0

    evidence_path.unlink()


def test_timeout_is_recorded():
    adapter = NmapAdapter()
    run_id = "RUN-TEST-TIMEOUT"

    timeout_error = subprocess.TimeoutExpired(
        cmd=["nmap"],
        timeout=30,
        output="partial output",
        stderr="timeout",
    )

    with patch.object(
        adapter,
        "_get_tool_version",
        return_value="Nmap version 7.99",
    ):
        with patch(
            "adapters.nmap_adapter.subprocess.run",
            side_effect=timeout_error,
        ):
            result = adapter.scan("127.0.0.1", run_id)

    assert result.return_code == -1
    assert result.timed_out is True
    assert result.tool_version == "Nmap version 7.99"

    evidence_path = Path(result.output_file)
    assert evidence_path.exists()

    evidence_path.unlink()


def test_output_uses_controlled_evidence_directory():
    adapter = NmapAdapter()

    output_path = adapter.output_directory.resolve()
    project_root = Path.cwd().resolve()

    assert output_path.is_relative_to(project_root)
    assert output_path.name == "runs"
