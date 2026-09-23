# Security Automation Foundation

## Project Overview

This project is a controlled security automation foundation for authorized
local/lab security testing.

The project started with basic configuration, approved-target validation,
Run ID generation, and structured logging. It was then extended with a safe
Nmap scanner adapter and now includes parser and normalization components for
processing scanner findings from multiple data formats.

The main goal is to keep the workflow controlled, testable, traceable, and
auditable while avoiding unrestricted command execution.

## Current Capabilities

The project currently provides:

- approved-target validation
- YAML-based project configuration
- scanner allow-list configuration
- Run ID generation
- structured JSON audit logging
- controlled Nmap scanner execution
- fixed scanner command construction
- execution timeout protection
- Nmap version capture
- controlled evidence output
- JSON, XML, and CSV parsing
- canonical security finding normalization
- JSON Schema validation
- malformed-input handling
- missing-field validation
- duplicate finding handling
- traceability IDs
- automated unit tests
- local/lab execution scope documentation

## Day 1 - Foundation

Day 1 established the basic execution boundary.

The foundation component:

1. loads the YAML configuration
2. loads the approved-targets file
3. generates a Run ID
4. validates the supplied target
5. records the validation result in structured JSON logging

The foundation check is validation-only and does not perform scanning or
connect to targets.

### Approved Targets

The current approved targets are:

- `127.0.0.1`
- `localhost`

A target that is not present in `approved_targets.txt` is rejected.

## Day 2 - Scanner Adapter and Safe Execution

Day 2 added a controlled Nmap scanner adapter.

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
- writes structured execution events to `evidence/run.log`

### Controlled Command Format

The current command format is:

```text
nmap -sT -n -p 1-1000 <approved-target>
```

The scanner options are controlled by the adapter and configuration rather than
being supplied as arbitrary command-line arguments.

### Day 2 Safety Controls

Scanner execution is restricted to explicitly approved targets.

An unapproved target is rejected before the scanner subprocess is started.

Additional controls include:

- fixed scanner executable
- controlled scanner arguments
- execution timeout
- controlled evidence directory
- structured audit logging
- local/lab execution scope

Detailed safety controls are documented in:

`docs/scanner_adapter_safety.md`

## Day 3 - Output Parsers and Canonical Normalization

Day 3 extends the workflow after scanner execution.

The Day 3 pipeline is:

```text
JSON / XML / CSV
       |
       v
     Parser
       |
       v
Raw Source Records
       |
       v
 Canonical Normalizer
       |
       v
Deduplication
       |
       v
Traceability
       |
       v
JSON Schema Validation
       |
       v
Normalized Findings
```

### Supported Input Formats

The parser layer currently supports:

- JSON
- XML
- CSV

The Day 3 fixtures contain:

```text
JSON → 2 records
XML  → 2 records
CSV  → 1 record
-----------------
Total → 5 records
```

### Canonical Finding Structure

Each normalized finding uses a common structure containing:

- title
- asset
- endpoint
- severity
- CVSS
- CWE
- evidence
- impact
- remediation
- references
- status
- traceability IDs
- source record information

### Traceability

Each source record receives a traceability identifier.

Current example format:

```text
TRC-JSON-001
TRC-JSON-002
TRC-XML-001
TRC-XML-002
TRC-CSV-001
```

The source record is preserved with the normalized finding so that the
normalized result can be traced back to its original input.

### Duplicate Handling

Duplicate findings are detected using the finding title, asset, and endpoint.

When duplicate findings are merged, the normalizer preserves the source
traceability IDs and source records.

### Validation

The normalized findings are validated against:

`schemas/finding.schema.json`

The current five fixture findings are all schema-valid:

```text
Validated findings: 5
Valid findings: 5
Schema validation: PASS
```

## Error Handling

The parser and normalizer explicitly handle invalid input.

Current tests cover:

- malformed JSON
- malformed XML
- missing required fields
- invalid CVSS values

Invalid input is rejected with a clear parsing or normalization error rather
than being silently accepted.

## Evidence and Reports

Day 3 generated normalized output and validation reports under:

```text
reports/day3/
```

The directory contains the scripts and generated validation artifacts used to
demonstrate the parser and normalization workflow.

Important files include:

- `export_normalized.py`
- `validate_normalized.py`
- `generate_validation_report.py`
- `normalized_findings.json`
- `validation_report.json`

The scanner execution evidence from Day 2 is stored under:

```text
evidence/runs/
```

Structured execution and audit events are stored in:

```text
evidence/run.log
```

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

Current scanner settings include:

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
|   |-- .gitkeep
|   |-- base_adapter.py
|   `-- nmap_adapter.py
|
|-- parsers/
|   |-- .gitkeep
|   |-- output_parsers.py
|   `-- normalizer.py
|
|-- schemas/
|   `-- finding.schema.json
|
|-- evidence/
|   |-- run.log
|   `-- runs/
|       `-- <generated scan evidence>.json
|
|-- reports/
|   |-- .gitkeep
|   `-- day3/
|       |-- export_normalized.py
|       |-- generate_validation_report.py
|       |-- normalized_findings.json
|       `-- validate_normalized.py
|
|-- docs/
|   `-- scanner_adapter_safety.md
|
`-- tests/
    |-- fixtures/
    |   |-- nmap_localhost_sample.txt
    |   `-- day3/
    |       |-- malformed.json
    |       |-- malformed.xml
    |       |-- sample_findings.csv
    |       |-- sample_findings.json
    |       `-- sample_findings.xml
    |-- test_day3_duplicates.py
    |-- test_day3_errors.py
    |-- test_day3_parsers.py
    |-- test_foundation_check.py
    `-- test_nmap_adapter.py
```

## File and Folder Purpose

| Path | Purpose |
|---|---|
| `app/foundation_check.py` | Validates project configuration and approved targets |
| `app/audit_logger.py` | Writes structured JSON audit events |
| `config/config.example.yaml` | Main project configuration example |
| `config/scanner_allowlist.yaml` | Controlled Nmap scanner configuration |
| `adapters/base_adapter.py` | Common scanner adapter interface and result model |
| `adapters/nmap_adapter.py` | Controlled Nmap scanner implementation |
| `parsers/output_parsers.py` | JSON, XML, and CSV parser implementations |
| `parsers/normalizer.py` | Canonical finding normalization and deduplication |
| `schemas/finding.schema.json` | Canonical security finding JSON Schema |
| `approved_targets.txt` | Explicitly approved targets |
| `evidence/run.log` | Structured execution audit log |
| `evidence/runs/` | Generated scanner evidence |
| `reports/day3/export_normalized.py` | Exports normalized findings |
| `reports/day3/validate_normalized.py` | Validates findings against the schema |
| `reports/day3/generate_validation_report.py` | Generates the Day 3 validation report |
| `docs/scanner_adapter_safety.md` | Scanner safety controls and limitations |
| `tests/test_foundation_check.py` | Day 1 foundation tests |
| `tests/test_nmap_adapter.py` | Day 2 scanner adapter tests |
| `tests/test_day3_parsers.py` | Successful parser tests |
| `tests/test_day3_errors.py` | Malformed and invalid-input tests |
| `tests/test_day3_duplicates.py` | Duplicate handling tests |
| `tests/fixtures/` | Repeatable test fixtures |

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

### Day 3 Tests

Day 3 tests cover:

- JSON parsing
- XML parsing
- CSV parsing
- preservation of raw source records
- malformed JSON rejection
- malformed XML rejection
- missing required field rejection
- invalid CVSS rejection
- duplicate finding handling
- traceability preservation

### Current Test Result

The complete project test suite currently passes:

```text
18 passed
```

## Validation Summary

### Day 1

- foundation configuration validation completed
- approved-target validation completed
- Run ID generation completed
- structured logging completed
- automated tests passed

### Day 2

- scanner allow-list completed
- Nmap adapter implemented
- approved target execution verified
- unapproved target rejection verified
- timeout handling implemented
- Nmap version capture implemented
- controlled evidence output implemented
- audit logging integrated
- safety documentation completed
- automated tests passed

### Day 3

- JSON parser implemented
- XML parser implemented
- CSV parser implemented
- five source records processed
- five canonical findings generated
- JSON Schema validation completed
- five findings validated successfully
- traceability IDs preserved
- malformed-input handling implemented
- missing-field validation implemented
- invalid CVSS handling implemented
- duplicate handling implemented
- validation report generated
- automated test suite passed

## Current Status

The repository currently contains the foundation, scanner adapter, parser,
normalizer, validation, and testing components completed across Days 1–3.

Current complete test result:

```text
18 passed
```

## Scope and Limitations

This project is intended for authorized local/lab security automation.

The current implementation is deliberately limited and does not provide
unrestricted network scanning or arbitrary command execution.

Scanner execution is bounded by an approved-target allow-list, controlled
command construction, timeout protection, and controlled evidence paths.
Parser and normalization components are designed to reject malformed or
incomplete data rather than silently accepting it.
