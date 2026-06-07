#!/usr/bin/env bash
set -euo pipefail
kind="${1:-design}"
language="${2:-agnostic}"
cat <<OUT
# Kan ${kind} stub (${language})

## Handoff / world-boundary data
- Signal:
- Seam:
- Worlds:
- Boundary kind:
- Known side:
- Unknown location:
- Witness slice:
- Proof signal:

## Extension-axis data, if applicable
- C:
- D:
- E:
- K : C -> D:
- F : C -> E:
- Candidate: Lan / Ran / Delta
- Unit/counit:

## Lift-axis data, if applicable
- A:
- B:
- C0:
- P : B -> C0:
- F : A -> C0:
- Candidate: Lft / Rft / P_*
- Comparison cell:

## Representation pass
- Yoneda observations:
- Coyoneda generated payloads/paths:
- Defunctionalized cases:

## Law and falsifier
- Positive law:
- Negative witness:
OUT
