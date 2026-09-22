"""
Base interface for scanner adapters.

Adapters are responsible for constructing and executing
approved scanner commands in a controlled environment.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ScanResult:
    """Standard result returned by a scanner adapter."""

    run_id: str
    target: str
    command: list[str]
    return_code: int
    stdout: str
    stderr: str
    timed_out: bool
    tool_version: str | None = None
    output_file: str | None = None


class ScannerAdapter(ABC):
    """Abstract interface for approved scanner adapters."""

    @abstractmethod
    def build_command(self, target: str) -> list[str]:
        """Build a controlled scanner command for the target."""
        raise NotImplementedError

    @abstractmethod
    def scan(self, target: str, run_id: str) -> ScanResult:
        """Execute the scanner against an approved target."""
        raise NotImplementedError
