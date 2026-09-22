"""
Controlled Nmap adapter for the local/lab security automation workflow.

The adapter only executes Nmap against targets present in the approved
targets file and uses scanner options defined in scanner_allowlist.yaml.
"""

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import yaml

from adapters.base_adapter import ScanResult, ScannerAdapter
from app.audit_logger import write_audit_log


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class NmapAdapter(ScannerAdapter):
    """Execute a controlled Nmap scan against an approved target."""

    def __init__(self, config_path: str = "config/scanner_allowlist.yaml"):
        self.config_path = PROJECT_ROOT / config_path
        self.config = self._load_config()

        scanner = self.config["scanner"]

        self.executable = scanner["executable"]
        self.scan_type = scanner["scan_type"]
        self.dns_resolution = scanner["dns_resolution"]
        self.ports = scanner["ports"]
        self.timeout = int(scanner["timeout_seconds"])

        self.output_directory = (
            PROJECT_ROOT / scanner["output_directory"]
        )
        self.approved_targets_file = PROJECT_ROOT / "approved_targets.txt"

    def _load_config(self) -> dict:
        """Load and validate scanner configuration."""

        with self.config_path.open("r", encoding="utf-8") as file:
            config = yaml.safe_load(file)

        if not isinstance(config, dict) or "scanner" not in config:
            raise ValueError("Invalid scanner configuration.")

        required = {
            "name",
            "executable",
            "scan_type",
            "dns_resolution",
            "ports",
            "timeout_seconds",
            "output_directory",
        }

        missing = required - set(config["scanner"])

        if missing:
            raise ValueError(
                f"Missing scanner configuration fields: {', '.join(sorted(missing))}"
            )

        return config

    def _load_approved_targets(self) -> set[str]:
        """Load targets that are permitted for scanner execution."""

        with self.approved_targets_file.open(
            "r", encoding="utf-8"
        ) as file:
            return {
                line.strip()
                for line in file
                if line.strip() and not line.strip().startswith("#")
            }

    def _check_target(self, target: str) -> None:
        """Reject targets that are not explicitly approved."""

        approved_targets = self._load_approved_targets()

        if target not in approved_targets:
            raise ValueError(f"Target is not approved: {target}")

    def build_command(self, target: str) -> list[str]:
        """Build the fixed Nmap command."""

        self._check_target(target)

        return [
            self.executable,
            self.scan_type,
            self.dns_resolution,
            "-p",
            self.ports,
            target,
        ]

    def _get_tool_version(self) -> str:
        """Capture the installed Nmap version."""

        result = subprocess.run(
            [self.executable, "--version"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )

        first_line = result.stdout.strip().splitlines()

        if first_line:
            return first_line[0]

        return "Unknown"

    def scan(self, target: str, run_id: str) -> ScanResult:
        """Run Nmap safely against an approved target."""

        try:
            command = self.build_command(target)
        except ValueError as exc:
            write_audit_log(
                run_id=run_id,
                event="scanner_execution",
                status="REJECTED",
                target=target,
                message=str(exc),
            )
            raise

        self.output_directory.mkdir(parents=True, exist_ok=True)

        output_file = (
            self.output_directory
            / f"{run_id}_{target.replace('.', '_')}.json"
        )

        tool_version = self._get_tool_version()

        write_audit_log(
            run_id=run_id,
            event="scanner_execution",
            status="STARTED",
            target=target,
            command=command,
            tool_version=tool_version,
            output_file=str(output_file.relative_to(PROJECT_ROOT)),
            message="Approved target accepted; Nmap execution started.",
        )

        timed_out = False

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                check=False,
            )

            return_code = result.returncode
            stdout = result.stdout
            stderr = result.stderr

        except subprocess.TimeoutExpired as exc:
            return_code = -1
            stdout = exc.stdout or ""
            stderr = exc.stderr or ""
            timed_out = True

        scan_result = ScanResult(
            run_id=run_id,
            target=target,
            command=command,
            return_code=return_code,
            stdout=stdout,
            stderr=stderr,
            timed_out=timed_out,
            tool_version=tool_version,
            output_file=str(output_file.relative_to(PROJECT_ROOT)),
        )

        with output_file.open("w", encoding="utf-8") as file:
            json.dump(
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "run_id": scan_result.run_id,
                    "target": scan_result.target,
                    "command": scan_result.command,
                    "return_code": scan_result.return_code,
                    "timed_out": scan_result.timed_out,
                    "tool_version": scan_result.tool_version,
                    "stdout": scan_result.stdout,
                    "stderr": scan_result.stderr,
                },
                file,
                indent=2,
            )

        final_status = "TIMEOUT" if timed_out else (
            "COMPLETED" if return_code == 0 else "FAILED"
        )

        write_audit_log(
            run_id=run_id,
            event="scanner_execution",
            status=final_status,
            target=target,
            command=command,
            return_code=return_code,
            timed_out=timed_out,
            tool_version=tool_version,
            output_file=str(output_file.relative_to(PROJECT_ROOT)),
            message="Nmap execution completed.",
        )

        return scan_result
