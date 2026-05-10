#!/usr/bin/env bash
set -euo pipefail
mode="${1:-boundary-diagnostic}"
language="${2:-agnostic}"
case "$mode" in
  boundary-diagnostic|diagnostic)
    cat <<OUT
# Freyd/AFT-style boundary diagnostic (${language})

## Lift-shaped seam
- A (public cases/contracts/workflows):
- B (internal implementation world):
- C (observable behavior world):
- P : B -> C (concrete projection in code):
- F : A -> C (required public behavior):

## Projection analysis
- What P forgets/observes/projects:
- Evidence lost by P:
- Does B combine constraints/products/equalities/pullbacks/workflows?
- Does P preserve those combinations in C?
- Bounded implementation templates for each required behavior?

## Result
- Candidate free builder / realizer / obligation artifact:
- Or obstruction:
- Exact / covering / sound / approximate comparison:

## Proof signal
project(candidate(required(case))) satisfies required(case), or obstruction reproduces failure.
OUT
    ;;
  free-builder)
    cat <<OUT
# Free builder behind projection (${language})

## Artifact
- RequiredBehavior:
- ImplementationTemplate:
- free : RequiredBehavior -> ImplementationTemplate
- project : ImplementationTemplate -> PublicBehavior

## Law
project(free(required(case))) satisfies required(case)

## Negative witness
A required behavior outside the builder's supported template set reports an obstruction.
OUT
    ;;
  no-exact-lift|obstruction)
    cat <<OUT
# Obstruction report behind projection (${language})

## Required behavior

## Projection P loses

## Internal world B cannot express

## Template set problem

## Obstruction constructors
- MissingEvidence
- MissingCapability
- InconsistentRequirement
- UnboundedTemplates

## Proof signal
The obstruction is reproducible by applying P or attempting construction for one witness case.
OUT
    ;;
  *) echo "unknown Freyd diagnostic mode: $mode" >&2; exit 2 ;;
esac
