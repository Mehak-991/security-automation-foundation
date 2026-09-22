"""
Structured audit logging for the security automation workflow.
"""

import json
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
AUDIT_LOG = PROJECT_ROOT / "evidence" / "run.log"


def write_audit_log(
    run_id: str,
    event: str,
    status: str,
    target: str,
    command: list[str] | None = None,
    return_code: int | None = None,
    timed_out: bool | None = None,
    tool_version: str | None = None,
    output_file: str | None = None,
    message: str | None = None,
) -> None:
    """Write one structured JSON audit entry."""

    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "run_id": run_id,
        "event": event,
        "status": status,
        "target": target,
        "command": command,
        "return_code": return_code,
        "timed_out": timed_out,
        "tool_version": tool_version,
        "output_file": output_file,
        "message": message,
    }

    with AUDIT_LOG.open("a", encoding="utf-8") as file:
        file.write(json.dumps(entry) + "\n")
