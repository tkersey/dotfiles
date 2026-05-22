#!/usr/bin/env bash
set -euo pipefail
mode="${1:-report}"
language="${2:-agnostic}"
cat <<OUT
# Codensity Presentation Report (${language})

## Target behavior / monad / effect

Name:
Category/world:
Why it is semantic/large/infinitary/observational:

## Algebraic presentation attempt

Generators:
Operations:
Equations:
Why insufficient or not useful:

## Small probe world

Objects/probes:
Morphisms/refinements:
Probe map:
Why small/simple:
Coverage/density claim:

## Duality / observation bridge

Dualizing object / observation object:
Dual world or observation world:
Adjunction/equivalence/bridge:
Commuting square / compatibility law:

## Reconstruction

Right Kan / codensity formula or architecture analogue:
What is reconstructed:
Generic categorical part:
Domain-specific theorem or assumption:

## Law tests

Probe coherence:
Density/coverage:
Reconstruction:
Composition/monad coherence:
Negative witness:
OUT
