#!/usr/bin/env bash
set -euo pipefail
kind="${1:-design-memo}"
language="${2:-agnostic}"
cat <<OUT
# Kan ${kind} stub (${language})

## Problem frame

What extension, compatibility, optimization, or migration problem is being solved?

## Kan data

- C:
- D:
- K : C -> D:
- F : C -> E:
- E:
- Candidate: Lan_K F / Ran_K F / K* (Delta)
- Unit/counit analogue:

## Direction choice

- Why Lan/Ran/Delta:
- Main failure mode prevented:
- Why a plain interface is not enough:

## Witness object d in D

- d:
- If Lan: objects of K ↓ d:
- If Ran: objects of d ↓ K:

## Implementation shape

- module/interface:
- adapter/interpreter:
- generated/default behavior:
- normalization or coherence strategy:

## Law tests

- unit/counit naturality:
- factorization/centralization:
- golden/regression witness:

## Risks

- false categorical model:
- quotient/coherence issue:
- performance/complexity issue:
- onboarding issue:

## Source boundaries

- mathematical claims:
- programming claims:
- architecture inferences:
OUT
