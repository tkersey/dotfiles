#!/usr/bin/env bash
set -euo pipefail
kind="${1:-design-memo}"
language="${2:-agnostic}"
case "$kind" in
  lift-realization|left-lift|lft)
    cat <<OUT
# Kan left-lift realization stub (${language})

## Problem frame

What desired observable behavior must be realized behind a fixed boundary?

## Kan lift data

- A (requirements/spec/features/tests):
- B (implementation/internal/resource category):
- C (observable/public/semantic category):
- P : B -> C (fixed projection/boundary):
- F : A -> C (desired observable behavior):
- Candidate: Lft_P F
- Unit/comparison: eta : F -> P . Lft_P F

## Why this is a lift, not an extension

- Unknown is before/behind P:
- P is fixed because:
- A plain adapter is not enough because:

## Witness object a in A

- a:
- desired F(a):
- candidate implementation Lft_P F(a):
- projected behavior P(Lft_P F(a)):

## Implementation shape

- boundary/projection module P:
- synthesized/derived module:
- central construction function:
- invalid/partial cases:

## Law tests

- realization: F(a) relates to P(Lft_P F(a)) via eta
- naturality across one h : a -> a':
- minimality/factorization approximation:
- regression/golden witness:

## Risks

- P is not actually fixed:
- order/2-cell direction is wrong:
- synthesized artifact bypasses P:
- over-generation/over-engineering:

## Source boundaries

- mathematical claims:
- programming claims:
- architecture inferences:
OUT
    ;;
  lift-obligation|right-lift|rift)
    cat <<OUT
# Kan right-lift obligation stub (${language})

## Problem frame

What residual requirements, weakest obligations, or sound internal constraints must be derived behind a fixed boundary?

## Kan lift data

- A (requirements/spec/features/tests):
- B (implementation obligations/capabilities/internal category):
- C (observable/public/semantic category):
- P : B -> C (fixed projection/boundary):
- F : A -> C (desired/accepted observable behavior):
- Candidate: Rft_P F
- Counit/comparison: epsilon : P . Rft_P F -> F

## Why this is a lift, not an extension

- Unknown is before/behind P:
- P is fixed because:
- A plain checklist is not enough because:

## Witness object a in A

- a:
- desired/accepted F(a):
- candidate residual Rft_P F(a):
- projected behavior P(Rft_P F(a)):

## Implementation shape

- boundary/projection module P:
- residual/obligation module:
- central soundness check:
- invalid/partial cases:

## Law tests

- soundness: P(Rft_P F(a)) relates to F(a) via epsilon
- naturality across one h : a -> a':
- maximality/factorization approximation:
- regression/golden witness:

## Risks

- P is not actually fixed:
- order/2-cell direction is wrong:
- obligation checks bypass Rft:
- under-constrained implementation:

## Source boundaries

- mathematical claims:
- programming claims:
- architecture inferences:
OUT
    ;;
  architecture-transformation|kan-lift|design-memo|*)
    cat <<OUT
# Kan ${kind} stub (${language})

## Problem frame

What extension, lift, compatibility, optimization, migration, synthesis, or obligation problem is being solved?

## Composition axis

Choose one:

- Extension/precomposition: unknown is after K.
- Lift/postcomposition: unknown is before P.
- Restriction/checking: K* or P_* only.

## Extension data, if using Lan/Ran/Delta

- C:
- D:
- K : C -> D:
- F : C -> E:
- E:
- Candidate: Lan_K F / Ran_K F / K* (Delta)
- Unit/counit analogue:

## Lift data, if using Lft/Rft/P_*

- A:
- B:
- C:
- P : B -> C:
- F : A -> C:
- Candidate: Lft_P F / Rft_P F / P_*
- Unit/counit comparison:

## Direction choice

- Why this composition axis:
- Why this direction:
- Main failure mode prevented:
- Why a plain interface/adapter is not enough:

## Witness slice

- witness object:
- source/requirement value:
- target/implementation value:
- boundary map:
- expected comparison:

## Implementation shape

- module/interface:
- adapter/projection/interpreter:
- generated/synthesized/default behavior:
- normalization/coherence/residual strategy:

## Law tests

- unit/counit or comparison naturality:
- factorization/centralization:
- golden/regression witness:

## Risks

- false categorical model:
- quotient/coherence/residual issue:
- performance/complexity issue:
- onboarding issue:

## Source boundaries

- mathematical claims:
- programming claims:
- architecture inferences:
OUT
    ;;
esac
