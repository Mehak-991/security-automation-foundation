# Evidence Capture and Storage

## Purpose

This module stores security evidence with useful metadata, integrity checks,
and basic redaction support.

## Evidence Handling

- Evidence is stored under controlled project directories.
- Each run can have a manifest containing run metadata.
- SHA-256 is used to verify evidence integrity.
- Common Bearer tokens, API keys, and password-like values can be redacted.
- A reference fixture is maintained for reproducibility testing.

## Manifest Metadata

The manifest records:

- Run ID
- timestamp
- target
- command
- tool version
- scope
- operator
- evidence file
- SHA-256 hash

## Validation

Current checks include:

- hash consistency
- secret redaction
- manifest metadata
- evidence hash matching
- reference fixture reproducibility

The current complete test suite passes with 23 tests.
