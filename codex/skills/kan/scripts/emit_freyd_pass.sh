#!/usr/bin/env bash
set -euo pipefail
topic="${1:-boundary-diagnostic}"
language="${2:-agnostic}"
case "$topic" in
  boundary-diagnostic|freyd-aft|freyd-lift-boundary)
    cat <<'OUT'
# Freyd/AFT lift-boundary diagnostic

## Lift data

- A = public scenarios / requirements / contract cases:
- B = internal implementation architecture:
- C = observable behavior:
- P : B -> C = projection / view / runtime observer:
- F : A -> C = required behavior:

## Projection P

- concrete module/function/test harness:
- what P observes:
- what P forgets:
- bypasses around P to remove:

## Constraint structure in B

- products / composition:
- pullbacks / shared-interface joins:
- equalizers / agreement checks:
- intersections / policy meets:
- validation or evidence objects:

## Preservation tests for P

- constraint preserved by projection:
- test fixture:
- expected projected equality/refinement:

## Solution-set-like templates

List the bounded implementation strategies that should cover accepted realizations.

- template 1:
- template 2:
- template 3:

## Candidate free builder

- Free : C -> B:
- implementation artifact:
- L = Free . F:
- exactness classification: exact / embedding / covering / sound / approximate / no-exact-lift

## Projection law

P(Free(F(a))) satisfies F(a) for witness a.

## Obstruction report

- vague P:
- missing constraints in B:
- P loses required observation:
- no bounded implementation template:
- repair options:
OUT
    ;;
  free-builder)
    cat <<'OUT'
# Free-builder scaffold

Given a lift-shaped problem with P : B -> C and F : A -> C:

1. Define observable behavior C as a first-order contract/behavior type.
2. Define implementation architecture B as implementation plans, workflow skeletons, effect programs, or modules.
3. Define project : B -> C.
4. Define Free : C -> B.
5. Define L(a) = Free(F(a)).
6. Test project(L(a)) equals/covers/satisfies F(a).
7. Record when Free creates extra generated behavior and classify the unit/comparison.

Minimal law:

project(free(required_behavior)) ~= required_behavior

where ~= is exact equality, embedding, covering, soundness, or an explicitly documented approximation.
OUT
    ;;
  solution-set|templates)
    cat <<'OUT'
# Solution-set-like implementation templates

For each observable requirement, list a small menu of implementation templates.

## Requirement class

- observable requirement:
- relevant observations:

## Templates

| Template | Covers | Required data | Required transitions | Risks |
|---|---|---|---|---|
| | | | | |

## Factor-through claim

Every accepted implementation of this requirement should factor through one of these templates, at least as an engineering policy.

## Tests

- one fixture per template;
- one fixture proving unsupported requirements produce no-exact-lift;
- one fixture proving projection through the template satisfies the observable requirement.
OUT
    ;;
  no-exact-lift|obstruction)
    cat <<'OUT'
# No-exact-lift obstruction report

## Required observation

- case a:
- F(a) requires:

## Current boundary

- B currently stores/derives:
- P currently observes:

## Obstruction

Why P cannot produce the required observation from current B.

## Repair options

1. Enrich B with missing data/state/capability.
2. Change P to observe the missing behavior.
3. Add an external dependency that can supply the observation.
4. Weaken F or document approximation.
5. Reject the refactor as unsupported.

## Regression test

Add a failing test that captures the obstruction before applying a repair.
OUT
    ;;
  *) echo "Unknown Freyd/AFT topic: $topic" >&2; exit 2 ;;
esac
printf '\n# Language hint: %s\n' "$language"
