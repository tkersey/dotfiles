#!/usr/bin/env bash
set -euo pipefail
topic="${1:-contract-refactor}"
language="${2:-agnostic}"
case "$topic" in
  contract-refactor|outside-in|realization)
    cat <<OUT
# Kan lift contract-first refactor (${language})

## Lift data

- A = public scenarios / contract cases / golden tests:
- B = candidate internal architecture:
- C = observable behavior:
- P : B -> C = projection from internals to public behavior:
- F : A -> C = required behavior:
- Candidate = Lft_P F / Rft_P F / P_*:
- Comparison cell = F -> P.L or P.R -> F:

## Commitment inventory

- public API behavior:
- emitted events/traces:
- persisted/report-visible state:
- policies/security/billing:
- legacy clients:

## Witness case a in A

- case:
- required observations:
- current implementation path:
- candidate internal realizer:

## Projection law test

projectImplementation(realizer(a)) == requiredBehavior(a)

or state the chosen preorder:

requiredBehavior(a) <= projectImplementation(realizer(a))
projectImplementation(residual(a)) <= requiredBehavior(a)

## No-exact-lift check

- missing data:
- missing transition:
- missing capability:
- missing observation path through P:
- required weakening or approximation:

## Refactor steps

1. Write projection/golden test.
2. Centralize P.
3. Add realizer/obligation IR if needed.
4. Implement one witness only.
5. Update obligation ledger.
6. Generalize after witness passes.
OUT
    ;;
  obligation-discovery|residual|right-lift)
    cat <<OUT
# Kan lift obligation discovery (${language})

## Inputs

- A = tests / policies / reports / endpoint cases:
- C = observable behavior lattice or relation:
- F : A -> C = required behavior:
- B = internal obligations / capabilities / resources:
- P : B -> C = projection:
- Direction = Rft_P F if comparison is P.R -> F:

## Obligation ledger

| Case | Observation | Required F(a) | Current P can produce | Missing B artifact | Repair | Test |
|---|---|---|---|---|---|---|

## Obligation kinds

- data:
- transition:
- capability:
- temporal/idempotency/order:
- observation/projection:
- coherence across observations:

## Soundness law

project(obligation(a)) <= required(a)

## No-exact-lift report

For every missing observation, state:
- why P cannot produce it from current B;
- whether to enrich B, change P, weaken F, add a dependency, or accept approximation.
OUT
    ;;
  no-exact-lift|obstruction)
    cat <<OUT
# No-exact-lift report (${language})

## Claimed lift

- A:
- B:
- C:
- P : B -> C:
- F : A -> C:
- Witness a:

## Required observation

- observation:
- required value/behavior:
- comparison relation:

## Obstruction

Current P cannot produce the required observation because:

- missing data:
- missing state transition:
- missing capability:
- missing temporal guarantee:
- missing projection path:
- incoherent observations:

## Repair options

1. Enrich B:
2. Change P:
3. Weaken F:
4. Add external dependency:
5. Accept approximate lift:

## Tests

- failing witness test:
- repair acceptance test:
- regression guard:
OUT
    ;;
  view-update|reverse-migration)
    cat <<OUT
# View-update / reverse-migration lift (${language})

## Lift data

- B = source/internal states or database instances:
- C = public views / target observations:
- P : B -> C = view/query/projection:
- A = desired view-update cases:
- F : A -> C = desired view after update:

## Analysis

- Is there a source update b' such that P(b') == F(a)?
- If not, what source information is missing?
- Which source updates are ambiguous?
- Which invariants must be preserved?

## Tests

P(applySourceUpdate(b, lift(a))) == F(a)

and source invariants still hold.
OUT
    ;;
  effect-handler|trace-realization)
    cat <<OUT
# Effect-handler / trace-realization lift (${language})

## Lift data

- A = desired effect/trace scenarios:
- B = effectful programs, handler strategies, runtime plans:
- C = observable traces:
- P : B -> C = interpreter/handler trace semantics:
- F : A -> C = required trace behavior:

## Realization

- candidate program/handler:
- projection path:
- observations:
- residual obligations:

## Law test

trace(P(candidate(a))) compares to F(a)

State exact equality, prefix refinement, containment, or allowed nondeterminism.
OUT
    ;;
  *) echo "Unknown lift playbook topic: $topic" >&2; exit 2 ;;
esac
printf '\n# Language hint: %s\n' "$language"
