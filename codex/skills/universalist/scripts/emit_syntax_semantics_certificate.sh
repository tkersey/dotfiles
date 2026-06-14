#!/usr/bin/env bash
set -euo pipefail
artifact="${1:-ToolOperation}"
language="${2:-agnostic}"
cat <<OUT
# Syntax / Semantics Certificate: ${artifact} (${language})

## Artifact

- Name: ${artifact}
- Boundary owned:

## Syntax world

- Constructors:
- Formation rules:
- Invalid forms:
- Totality requirements:

## Semantic world

- Effects / denotations:
- Observations:
- Invariants:
- Equivalence notion:

## Interpreter / handler / compiler / renderer

- Function/module:
- Owner:
- Bypass policy:

## Laws

### Soundness

accepted syntax denotes valid observed semantics

### Adequacy

required semantic distinctions are representable or observable

### Preservation

syntax transformation preserves declared observations

## Falsifier

- Accepted syntax with invalid semantics:
- Needed semantic behavior not expressible in syntax:

## Status

planned / implemented / verified / obstructed
OUT
