# Evidence Redacti
on Checklist

Before sharing or storing evidence, check the following:

- Remove or redact Bearer tokens.
- Remove or redact API keys.
- Remove or redact password values.
- Do not include unnecessary secrets in logs or screenshots.
- Keep synthetic test values separate from real credentials.
- Verify that the final evidence contains only information needed for review.

## Current Project Check

The evidence manager supports redaction for common:

- Bearer token patterns
- API key patterns
- password-like values

Redaction is a supporting control and is not guaranteed to detect every
possible secret format.

## Validation

Synthetic token, API key, and password examples were tested and replaced
with `[REDACTED]`.
