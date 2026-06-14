#!/usr/bin/env bash
set -euo pipefail
focus="${1:-syntax}"
language="${2:-agnostic}"
case "$focus" in
  syntax|syntax-semantics|agentic|tool|plan)
    cat <<OUT
# Category Pivot: syntax/semantics (${language})

## Current world

- Current representation: executable behavior / prose / callback / prompt / tool call / service method
- Hard operation: inspect / authorize / replay / diff / prove / totalize / serialize
- Why hard here:

## Easy world

- Syntax artifact: Plan / ToolOperation / PolicyRule / ContextSchema / Workflow / PatchIntent
- Constructors:
- Formation rules:
- Invalid forms:

## Semantic world

- Effects / traces / public behavior / policy outcome / memory consequence:
- Observations:
- Invariants:

## Interpreter

- handler / runner / compiler / renderer / projector:
- owner module:
- bypass policy:

## Laws

- Soundness: accepted syntax denotes valid observed semantics.
- Adequacy: required semantic distinctions are representable or observable.
- Preservation: syntax transformations preserve declared observations.
- Falsifier:
OUT
    ;;
  abstract-domain|poset|lattice)
    cat <<OUT
# Category Pivot: abstract domain / poset (${language})

## Current world
- Concrete states/behaviors:
- Hard operation: exhaustive analysis / least capability / greatest safe envelope / policy obligation

## Easy world
- Abstract domain / poset / lattice:
- Order meaning:
- Join / meet / residual operations:

## Transfer
- abstraction alpha:
- concretization/observation gamma:
- loss / approximation:

## Law
- soundness: concrete behavior is contained in abstraction/concretization.
- falsifier:
OUT
    ;;
  coalgebra|trace|protocol)
    cat <<OUT
# Category Pivot: coalgebra / trace semantics (${language})

## Current world
- Branchy mutable state or protocol behavior:

## Easy world
- State type:
- Input/action type:
- Observation type:
- transition/step function:
- observe function:

## Law
- trace law:
- invalid transition falsifier:
OUT
    ;;
  schema|context|categorical-data)
    cat <<OUT
# Category Pivot: schema-shaped context (${language})

## Current world
- Raw sources / chunks / tool outputs / documents / logs:

## Easy world
- Context schema:
- Observables:
- Mapping:
- Constraints:
- Provenance:
- Freshness:

## Law
- context satisfies schema and preserves observables after rendering.
- falsifier:
OUT
    ;;
  presheaf|site|sheafification)
    cat <<OUT
# Category Pivot: usage site / presheaf (${language})

## Current world
- Scattered local uses of an abstraction:

## Easy world
- Usage site:
- Local sections:
- Overlaps:
- Restriction maps:

## Law
- compatible local meanings glue to one global meaning.
- falsifier:
OUT
    ;;
  resource|capability)
    cat <<OUT
# Category Pivot: resource/capability world (${language})

## Current world
- Permissions/resources encoded as booleans, strings, or scattered checks:

## Easy world
- Resources:
- Composition/separation:
- Capabilities:
- Ownership/transfer rules:

## Law
- operations consume/produce only declared resources.
- falsifier:
OUT
    ;;
  *)
    echo "Unknown category pivot focus: $focus" >&2
    exit 2
    ;;
esac
