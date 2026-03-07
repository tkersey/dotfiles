# Shadow Mode

Use shadow mode after the static replay suite is green.

## Goal
- Compare live `$tk` behavior on fresh work against the replay-distilled expectations without blocking normal work.

## Suggested process
1. Tag 5-10 fresh `$tk` sessions by mode: advice, implementation, strict-output worker.
2. For each session, score:
   - seam choice
   - abstraction level
   - blast radius
   - proof posture
   - output-contract compliance
3. Mark drift as one of:
   - doctrine drift
   - wrapper contamination
   - proof overclaim
   - prose-only drift
4. Add a new replay case only when the drift recurs or exposes a missing contract.

## Pass bar
- No critical output-contract violations.
- At least 5/5 sampled sessions preserve the intended seam/shape decision.
- No faux-proof claims.

Reference artifacts for this repo can live beside this file as:
- `shadow-suite-YYYY-MM-DD.yaml`
- `shadow-pass-YYYY-MM-DD.md`
