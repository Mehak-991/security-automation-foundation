# Day 5 Reviewer Checklist

## Deduplication

- [ ] Duplicate key uses asset, endpoint, and issue type.
- [ ] Duplicate records are removed deterministically.
- [ ] Duplicate count is preserved for the retained record.
- [ ] Different endpoints are not treated as duplicates.
- [ ] Different issue types are not treated as duplicates.

## Severity and Priority

- [ ] CVSS is converted using transparent rules.
- [ ] Business priority uses defined asset, exploitability, and exposure inputs.
- [ ] Invalid CVSS values are rejected.
- [ ] Missing business context uses safe defaults.

## Human Review

- [ ] AI-suggested ratings require human review.
- [ ] Uncertain severity requires human review.
- [ ] Uncertain business priority requires human review.
- [ ] Automated output is not treated as final when review is required.

## Final Review

- [ ] Tests pass.
- [ ] Before/after deduplication result reviewed.
- [ ] Priority output reviewed.
- [ ] Git diff reviewed before commit.
