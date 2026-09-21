"""
Small project foundation check for the security automation workflow.

The script validates the configuration, checks whether a supplied target
is approved, creates a run ID, and writes a structured JSON log.

This is a validation-only component. It does not scan or connect to targets.
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_config(config_path: Path) -> dict:
    with config_path.open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    if not isinstance(config, dict):
        raise ValueError("Configuration must contain a YAML object.")

    required_sections = [
        "project",
        "input",
        "logging",
        "execution",
        "review",
    ]

    missing = [
        section for section in required_sections
        if section not in config
    ]

    if missing:
        raise ValueError(
            f"Missing configuration sections: {', '.join(missing)}"
        )

    return config


def load_approved_targets(target_file: Path) -> set[str]:
    with target_file.open("r", encoding="utf-8") as file:
        return {
            line.strip()
            for line in file
            if line.strip() and not line.strip().startswith("#")
        }


def create_run_id() -> str:
    timestamp = datetime.now(timezone.utc)
    return timestamp.strftime("RUN-%Y%m%d-%H%M%S")


def write_log(log_file: Path, run_id: str, event: str, status: str, message: str) -> None:
    log_file.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "run_id": run_id,
        "event": event,
        "status": status,
        "message": message,
    }

    with log_file.open("a", encoding="utf-8") as file:
        file.write(json.dumps(entry) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate an approved security automation target."
    )
    parser.add_argument(
        "--target",
        required=True,
        help="Target value to validate against the approved-targets file.",
    )
    parser.add_argument(
        "--config",
        default="config/config.example.yaml",
        help="Path to the YAML configuration file.",
    )

    args = parser.parse_args()

    config_path = PROJECT_ROOT / args.config
    config = load_config(config_path)

    target_file = PROJECT_ROOT / config["input"]["approved_targets_file"]
    log_file = PROJECT_ROOT / config["logging"]["log_file"]

    run_id = create_run_id()

    approved_targets = load_approved_targets(target_file)

    if config["input"]["allow_only_approved"] and args.target not in approved_targets:
        message = f"Target rejected: {args.target}"
        write_log(log_file, run_id, "target_validation", "REJECTED", message)

        print(f"Run ID: {run_id}")
        print("Validation: REJECTED")
        print(message)
        return 1

    message = f"Target approved: {args.target}"
    write_log(log_file, run_id, "target_validation", "APPROVED", message)

    print(f"Run ID: {run_id}")
    print("Validation: APPROVED")
    print(message)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
