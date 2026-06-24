# `$review-compression-compiler` 7.0 Patch Notes

The compiler now consumes sealed batches rather than an open stream of findings.

It emits:

```text
CEB-v2
MBK-v1
RC-v1
RAP-v1 plan
minimum-realization constraints
PHI-v1 baseline
```

Witness multiplicity is compressed before code exists.
