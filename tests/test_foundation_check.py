import re
import subprocess
import sys
from pathlib import Path

from app.foundation_check import load_approved_targets, create_run_id


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_approved_targets_file_contains_local_targets():
    target_file = PROJECT_ROOT / "approved_targets.txt"

    targets = load_approved_targets(target_file)

    assert "127.0.0.1" in targets
    assert "localhost" in targets


def test_run_id_has_expected_format():
    run_id = create_run_id()

    assert re.fullmatch(r"RUN-\d{8}-\d{6}", run_id)


def test_approved_target_is_accepted():
    result = subprocess.run(
        [
            sys.executable,
            "app/foundation_check.py",
            "--target",
            "127.0.0.1",
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Validation: APPROVED" in result.stdout
    assert "Target approved: 127.0.0.1" in result.stdout


def test_unapproved_target_is_rejected():
    result = subprocess.run(
        [
            sys.executable,
            "app/foundation_check.py",
            "--target",
            "192.0.2.10",
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "Validation: REJECTED" in result.stdout
    assert "Target rejected: 192.0.2.10" in result.stdout
