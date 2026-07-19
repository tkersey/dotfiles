#!/usr/bin/env bash
set -euo pipefail

mode="${1:-space}"
language="${2:-agnostic}"

case "$mode" in
  space|comonad-space|spatiality)
    focus="whole spatial world: points, coalgebras, halos, basis, and continuity"
    ;;
  density|density-comonad|basis|subbasis)
    focus="patch vocabulary, density comonad, basis strength, and canonical reconstruction"
    ;;
  halo|halos|labelled-halo|germ)
    focus="effective and labelled halos, germs, restriction, local/global identity, and resource bounds"
    ;;
  continuous|continuous-map|continuous-comonad-map|locality-preserving)
    focus="point map, coalgebra/context transport, halo direction, cartesian/locality compatibility, and falsifiers"
    ;;
  compare)
    focus="compare plain dependency/context models with comonadic spatiality and reject unnecessary escalation"
    ;;
  *)
    echo "Unknown comonadic spatiality mode: $mode" >&2
    echo "Use: space | density | halo | continuous | compare" >&2
    exit 2
    ;;
esac

cat <<OUT
# Comonadic Spatiality Report (${mode}, ${language})

Focus: ${focus}

## Scope

- system / seam:
- why locality changes correctness:
- simpler graph/context/type model considered:
- reason for escalation or preservation:

## Spatial world

- world:
- points:
- transformations:
- global observations:
- local observations:
- equality/coherence notion:

## Patch vocabulary

- patch category / vocabulary B:
- subbasis functor P:
- local points:
- global points:
- local-to-global map:
- identifications and provenance:

## Density / basis

- candidate C = Lan_P P or practical approximation:
- effective construction:
- subbasis-only or basis:
- decomposition into basic patches:
- canonical reconstruction:
- density witness / approximation:
- coverage that is not a basis:

## Comonad / coalgebra data

- context former C:
- counit / center extraction:
- comultiplication / nested local views:
- situated object / coalgebra h : E -> C(E):
- distinction from behavioral coalgebra:

## Halo / germ

- representative point:
- halo representation:
- finite / formal / bounded / indexed:
- labels: target, kind, owner, capability, effect, provenance, trust, time, cost
- restriction operation:
- germ representation:
- computation and invalidation budget:

## Boundary / continuity

- boundary:
- point map:
- source and target spatial worlds:
- coalgebra/context transport:
- halo-map direction:
- ordinary comonad map / continuous map / both / neither:
- continuity law:
- restriction or inverse-image law:

## Universalist integration

- Track / certificate:
- Exact Context germ:
- Possibility Sheafification relation:
- presentation mode: density-comonadic spatial / mixed / primitive
- canonical artifact:
- interpreter / query / projection / lowering:

## Law witnesses

- center / counit:
- neighborhood coherence / coassociativity:
- coalgebra centeredness:
- restriction / germ:
- basis density / reconstruction:
- continuity / halo preservation:
- labelled-halo preservation:
- local/global identity and provenance:
- resource law:

## Falsifiers / obstructions

- point preserved but locality lost:
- local/global identity collapsed:
- example coverage mistaken for basis density:
- unbounded or non-effective halo:
- invalid germ after transport:
- lost label / provenance / capability:
- stale spatial index:
- research assumption not justified:

## Witness seam

- files/modules:
- smallest implementation:
- verification:
- compatibility:
- stop point:

## Status

planned / implemented / verified / approximated / obstructed / primitive exception
OUT