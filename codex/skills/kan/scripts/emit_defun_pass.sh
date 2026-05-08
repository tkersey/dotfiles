#!/usr/bin/env bash
set -euo pipefail
topic="${1:-boundary-ir}"
language="${2:-agnostic}"
printf '# Defunctionalization pass (%s, %s)\n\n' "$topic" "$language"
cat <<'OUT'
## Boundary being made first-order

- Construction: Lan / Ran / Delta / Lft / Rft / P_* / codensity / effect-handler
- Boundary map: K or P
- Witness slice:
- Law this pass must preserve:

## Higher-order values crossing the boundary

List every function-like value that crosses module/API/runtime boundaries:

- callback / continuation / observer / path / projection / handler / resumption / predicate / builder:
- owner module:
- call sites:
- free variables carried implicitly:

## Constructors

Replace those values with first-order cases:

```text
data BoundaryCase
  = CaseOne { payloads... }
  | CaseTwo { payloads... }
  | CustomExternal { documentedLossOfLaws... }   # only if openness is required
```

## Interpreter / apply / project function

Name exactly one central interpreter:

- applyFrame / interpretPath / runObservation / restrict / projectImplementation / satisfyObligation / handleOperation:
- module path:
- totality or partiality strategy:
- error type for impossible cases:

## Law tests

- Unit/counit/comparison witness:
- Naturality or coherence test:
- Factorization/centralization test:
- Golden regression:
- Failure case:

## Architecture migration

- Files to introduce:
- Old functions to wrap first:
- Call sites to migrate:
- Public escape hatch, if any:
- Rollback:

## Source boundaries

- Defunctionalization claim: [KAN-DANVY-NIELSEN-2001]
- CPS/control/codensity claim, if used: [KAN-HINZE-2012] or [KAN-DANVY-FILINSKI-1990]
- Kan extension/lift claim: [KAN-RIEHL-CTIC] or [KAN-NLAB-LIFT]
OUT
