# Actuating v5.1.0 Patch Notes

## Intent

Make `$actuating` a true mutation authority rather than an implementation aesthetic.

## Added

- APMA-v1 pre-mutation authority receipt.
- `tools/actuation_authority_gate.py`.
- `references/pre-mutation-interlock.md`.
- Self-invalidating GCR diagnosis.
- Regression tests for authorization, resource coverage, APMA checking, and stale-sequence GCR diagnosis.

## Hard rule

```text
No APMA-v1 mutation-authorized receipt => no actuation-labeled patch.
```

## Expected audit effect

Future true/control `$actuating` rows should have:

```text
mutations_without_gcr = 0
graph_bypass_rows = 0
projection_inversion_rows = 0
```
