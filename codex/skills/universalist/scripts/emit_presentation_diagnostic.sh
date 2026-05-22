#!/usr/bin/env bash
set -euo pipefail
mode="${1:-compare}"
language="${2:-agnostic}"
case "$mode" in
  algebraic)
    cat <<OUT
# Algebraic Presentation Diagnostic (${language})

## Target artifact

Artifact:
Boundary:
Worlds:

## Generators / operations / equations

Generators:
Operations:
Equations:
Handlers/interpreters:

## Why algebraic presentation fits

- operational/command-like behavior:
- finite constructors:
- clear handlers:

## Law tests

- handler/interpreter parity:
- equations respected:
- missing constructor falsifier:
OUT
    ;;
  codensity|dense|dense-dual)
    cat <<OUT
# Codensity / Dense-Dual Presentation Diagnostic (${language})

## Target semantic artifact

Artifact:
Why direct algebraic presentation is awkward/infinitary:

## Small probe world

Objects/probes:
Morphisms/refinements:
Probe map:
Coverage/density claim:

## Dual / observation bridge

Dualizing object:
Observation result world:
Bridge/reconstruction:
Domain-specific theorem or assumption:

## Laws

Probe coherence:
Reconstruction law:
Missing-probe falsifier:
OUT
    ;;
  compare|*)
    cat <<OUT
# Presentation Strategy Comparison (${language})

## Artifact and boundary

Artifact:
Boundary:
Worlds:

## Algebraic presentation candidate

Generators:
Operations:
Equations:
Handlers:
Why it works/fails:

## Codensity / dense-dual presentation candidate

Small probe world:
Dense map / coverage claim:
Dualizing observation object:
Reconstruction operation:
Domain-specific assumption:
Why it works/fails:

## Decision

Presentation mode: algebraic / codensity / mixed / primitive
Why this mode:
Presentation law:
Presentation falsifier:
OUT
    ;;
esac
