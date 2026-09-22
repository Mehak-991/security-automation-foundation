# Security Automation Foundation

## Project Overview

This project is the foundation for a controlled security automation workflow.

The project was started with basic input validation, configuration, Run IDs,
and structured logging. It now extends that foundation with a controlled
Nmap scanner adapter for authorized local/lab use.

The main goal is to keep scanner execution bounded, testable, auditable, and
separate from unrestricted command execution.

## Current Capabilities

The project currently provides:

- a clean repository structure
- an approved-targets list
- YAML-based project configuration
- scanner allow-list configuration
- configuration validation
- approved-input validation
- Run ID generation
- structured JSON audit logging
- a controlled Nmap scanner adapter
- fixed scanner command construction
- execution timeout protection
- Nmap tool version capture
- stdout and stderr capture
- controlled evidence output paths
- automated unit tests
- local/lab-only execution rules
- documented scanner safety controls
- a sample Nmap output fixture for repeatable testing

## Day 1 - Foundation

Day 1 established the basic execution boundary for the project.

The foundation check:

1. loads the YAML configuration
2. loads the approved-targets file
3. generates a Run ID
4. validates the supplied target
5. records the validation result in structured JSON logging

The foundation check is validation-only and does not perform scanning or
connect to the target.

### Current Approved Targets

The current approved targets are:

- `127.0.0.1`
- `localhost`

A target that is not present in `approved_targets.txt` is rejected.

## Day 2 - Scanner Adapter and Safe Execution

Day 2 extends the foundation with a controlled Nmap scanner adapter.

The adapter:

- validates the target against `approved_targets.txt`
- reads scanner settings from `config/scanner_allowlist.yaml`
- constructs the Nmap command internally
- does not accept arbitrary scanner arguments
- applies a 30-second execution timeout
- captures the installed Nmap version
- captures stdout and stderr
- records the process return code
- records timeout status
- writes scanner evidence under `evidence/runs/`
- writes structured scanner execution events to `evidence/run.log`

### Controlled Command Format

The current command format is:

```text
nmap -sT -n -p 1-1000 <approved-target>
```

The scanner options are controlled by the adapter and configuration rather than
being supplied as arbitrary command-line arguments.

## Safety Controls

Scanner execution is restricted to explicitly approved targets.

For example:

```text
127.0.0.1
```

is currently approved and can proceed to scanner execution.

An unapproved target such as:

```text
192.0.2.10
```

is rejected before the scanner subprocess is started.

The automated test suite also verifies that the scanner subprocess is not
called when an unapproved target is supplied.

Additional controls include:

- fixed scanner executable
- controlled scanner arguments
- execution timeout
- controlled evidence directory
- structured audit logging
- local/lab execution scope

Detailed safety controls are documented in:

`docs/scanner_adapter_safety.md`

## Evidence and Logging

Successful scanner executions create JSON evidence files under:

```text
evidence/runs/
```

Each scanner execution record includes information such as:

- timestamp
- Run ID
- target
- command
- return code
- timeout status
- Nmap version
- stdout
- stderr

Structured scanner execution events are written to:

```text
evidence/run.log
```

Generated runtime evidence and log files are treated as execution artifacts
and are excluded from source control where appropriate.

## Configuration

### Foundation Configuration

The main project configuration is:

`config/config.example.yaml`

It defines:

- project name
- environment
- approved-targets file
- approved-input enforcement
- structured logging
- Run ID generation
- local-only execution
- human review requirement

### Scanner Configuration

The scanner configuration is:

`config/scanner_allowlist.yaml`

The current scanner configuration defines:

```yaml
scanner:
  name: nmap
  executable: nmap
  scan_type: "-sT"
  dns_resolution: "-n"
  ports: "1-1000"
  timeout_seconds: 30
  output_directory: "evidence/runs"
```

## Project Structure

```text
security_automation_foundation/
|
|-- README.md
|-- approved_targets.txt
|-- .gitignore
|
|-- app/
|   |-- audit_logger.py
|   `-- foundation_check.py
|
|-- config/
|   |-- config.example.yaml
|   `-- scanner_allowlist.yaml
|
|-- adapters/
|   |-- base_adapter.py
|   `-- nmap_adapter.py
|
|-- parsers/
|   `-- .gitkeep
|
|-- evidence/
|   |-- run.log
|   `-- runs/
|       `-- <generated scan evidence>.json
|
|-- reports/
|   `-- .gitkeep
|
|-- docs/
|   `-- scanner_adapter_safety.md
|
`-- tests/
    |-- fixtures/
    |   `-- nmap_localhost_sample.txt
    |-- test_foundation_check.py
    `-- test_nmap_adapter.py
```

## File and Folder Purpose

| Path | Purpose |
|---|---|
| `README.md` | Project overview, setup information, structure, and validation summary |
| `approved_targets.txt` | List of explicitly approved targets |
| `app/foundation_check.py` | Validates project configuration and approved input |
| `app/audit_logger.py` | Writes structured JSON audit events |
| `config/config.example.yaml` | Example project configuration |
| `config/scanner_allowlist.yaml` | Controlled Nmap scanner configuration |
| `adapters/base_adapter.py` | Common scanner adapter interface and result model |
| `adapters/nmap_adapter.py` | Controlled Nmap scanner implementation |
| `parsers/` | Reserved for future scanner output parsers |
| `evidence/run.log` | Structured execution audit log |
| `evidence/runs/` | Generated scanner evidence files |
| `reports/` | Reserved for future report generation |
| `docs/scanner_adapter_safety.md` | Scanner execution safety controls and limitations |
| `tests/test_foundation_check.py` | Day 1 automated tests |
| `tests/test_nmap_adapter.py` | Day 2 scanner adapter tests |
| `tests/fixtures/` | Sample input/output data for repeatable testing |

## Testing

The project uses `pytest` for automated testing.

### Day 1 Tests

Day 1 tests cover:

- approved target file handling
- Run ID format
- approved target acceptance
- unapproved target rejection

### Day 2 Tests

Day 2 tests cover:

- controlled Nmap command construction
- unapproved target rejection before execution
- successful scan result handling
- timeout handling
- controlled evidence directory validation

A sample Nmap output fixture is also included:

`tests/fixtures/nmap_localhost_sample.txt`

The complete project test suite currently passes:

```text
9 passed
```

## Validation Evidence

### Day 1 Validation

The foundation component was tested with:

- approved target: `127.0.0.1`
- unapproved target: `192.0.2.10`

The approved target was accepted and the unapproved target was rejected.

### Day 2 Validation

A real Nmap execution was performed against the approved local target:

```text
127.0.0.1
```

The controlled command was:

```text
nmap -sT -n -p 1-1000 127.0.0.1
```

The execution completed successfully with:

- return code: `0`
- timeout: `False`
- Nmap version: `7.99`

The scan result was saved as JSON evidence under:

```text
evidence/runs/
```

The scanner execution was also recorded in:

```text
evidence/run.log
```

The unapproved-target test confirmed that:

```text
192.0.2.10
```

was rejected before scanner execution, and no evidence file was created for
that rejected run.

## Scope and Limitations

This project is intended for authorized local/lab security automation.

The current implementation is deliberately limited and does not provide
unrestricted network scanning or arbitrary command execution.

The scanner adapter uses fixed command construction, an explicit
target allow-list, a fixed timeout, and controlled evidence paths. These
controls are intended to keep the current workflow bounded and auditable.

## Current Status

### Day 1

- Foundation repository structure completed
- Configuration validation completed
- Approved-target validation completed
- Run ID generation completed
- Structured logging completed
- Automated tests passing

### Day 2

- Scanner allow-list configuration completed
- Scanner adapter interface completed
- Nmap adapter implemented
- Approved-target enforcement completed
- Safe command construction completed
- Timeout protection implemented
- Nmap version capture implemented
- Controlled evidence output implemented
- Structured audit logging integrated
- Safety documentation completed
- Unit tests completed

Current complete test result:

```text
9 passed
```
