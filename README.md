# Security Automation Foundation

## Project Overview

This project is the starting foundation for a controlled security automation workflow.

The main idea is simple: before adding scanners, parsers, AI-assisted processing, or report generation, the workflow should first have clear project boundaries, approved inputs, configuration, logging, and repeatable validation.

The current version is intentionally small and focuses on the basic building blocks that can be tested easily.

## What This Foundation Covers

This project currently provides:

- a clean repository structure
- an approved-targets list
- example YAML configuration
- configuration validation
- approved-input validation
- unique Run IDs
- structured JSON logging
- automated tests
- local/lab-only execution rules

## Project Structure

```text
security_automation_foundation/
|
|-- README.md
|-- approved_targets.txt
|-- .gitignore
|
|-- app/
|   `-- foundation_check.py
|
|-- config/
|   `-- config.example.yaml
|
|-- adapters/
|   `-- .gitkeep
|
|-- parsers/
|   `-- .gitkeep
|
|-- evidence/
|   `-- run.log
|
|-- reports/
|   `-- .gitkeep
|
`-- tests/
    `-- test_foundation_check.py
