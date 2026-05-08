#!/usr/bin/env bash
set -euo pipefail
topic="${1:-boundary-representation}"
language="${2:-agnostic}"
case "$topic" in
  yoneda|observation|observation-boundary|ran-observer)
    cat <<OUT
# Yoneda observation pass (${language})

Use when a boundary is observation-heavy: Ran facades, read models, public contract projections, policies, test oracles, or capability consumers.

## Boundary data

- Construction: Ran / Rft / P_* / codensity / facade
- Boundary map: K or P
- Observed thing:
- Existing observers/callbacks:
- Witness observation:

## Yoneda-shaped representation

- Sanctioned observations:
- Hidden representation that must not leak:
- observe/runObservation function:
- Coherence/naturality law:

## Defunctionalization option

- Observation constructors:
- Payloads/free variables:
- runObservation implementation:
- Invalid observation cases:

## Law tests

- observation round trip or identity observation:
- map/observation fusion:
- representation independence:
- selected Ran/Rft/P_* law:

## Failure modes

- raw representation still leaks:
- observations duplicated outside the runner:
- observer inspects forbidden internals:
OUT
    ;;
  coyoneda|generation|generation-boundary|lan-generator)
    cat <<OUT
# Coyoneda generation pass (${language})

Use when a boundary is generation-heavy: Lan extensions, plugin nodes, schema migrations, generated clients, event envelopes, workflow steps, or candidate realizers.

## Boundary data

- Construction: Lan / Lft / generated artifact / migration
- Boundary map: K or P
- Raw source payload:
- Deferred transformation/path:
- Witness generated target:

## Coyoneda-shaped representation

- Payload type:
- Deferred map/path type:
- lower/interpretPath function:
- Provenance to preserve:

## Defunctionalization option

- Path/GeneratedCase constructors:
- Payloads/free variables:
- lower/interpretPath implementation:
- Invalid path cases:

## Law tests

- identity lowering:
- map/path fusion:
- provenance preservation:
- selected Lan/Lft law:

## Failure modes

- payload interpreted too early:
- path/map scattered across modules:
- no provenance or fusion benefit:
OUT
    ;;
  lift|kan-lift|both)
    cat <<OUT
# Yoneda/Coyoneda lift pass (${language})

Use when solving behind a fixed projection P : B -> C.

## Lift data

- A (requirements/spec cases):
- B (implementation/design choices):
- C (observable behavior):
- P : B -> C:
- F : A -> C:
- Candidate: Lft_P F / Rft_P F / P_*
- Witness a:

## Yoneda side: public observations

- Observation cases:
- runObservation function:
- Required observation results F(a):
- Coherence/naturality law:

## Coyoneda side: candidate realizers

- CandidateRealizer cases:
- ProjectionPath cases:
- projectImplementation function:
- Residual obligations when projection is missing:

## Law tests

- for every observation obs: runObservation(P(realizer(a)), obs) == runObservation(F(a), obs)
- missing projection path emits an explicit obligation
- no public behavior bypasses P

## Defunctionalization outputs

- PublicObservation IR:
- CandidateRealizer IR:
- ProjectionPath IR:
- Boundary interpreter/projector:
OUT
    ;;
  boundary-representation|*)
    cat <<OUT
# Yoneda/Coyoneda boundary-representation pass (${language})

## Decide local representation

- Observation-heavy? Use Yoneda.
- Generation-heavy? Use Coyoneda.
- Lift boundary? Use Yoneda for public observations and Coyoneda for candidate realizers.

## Questions

1. What is the selected Kan construction: Lan / Ran / Delta / Lft / Rft / P_*?
2. What crosses the boundary: observations, generated payloads, projection paths, callbacks, handlers, or realizers?
3. Should it remain higher-order, or become first-order IR?
4. What single interpreter/apply/project/lower function owns the semantics?
5. What law test ties it back to the selected Kan construction?

## Deliverables

- Observation or Generated/Path case type.
- Interpreter/projector/lowering function.
- Identity/round-trip or fusion test.
- Unit/counit/realization law test.
- Failure case for invalid observation/path/projection.
OUT
    ;;
esac
