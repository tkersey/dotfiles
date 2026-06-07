#!/usr/bin/env bash
set -euo pipefail
scope="${1:-repo}"
language="${2:-agnostic}"
cat <<OUT
# Abstraction Normal Form Plan (${scope}, ${language})

## Audit scope

- repo/module:
- architecture-level abstractions to inspect:

## Candidate signals

- stringly typed protocols:
- nullable/optional field state machines:
- duplicated status/state encodings:
- callback registries:
- DTO meaning drift:
- missing global artifact implied by tests:
- raw context masquerading as certified context:

## Ranking table

| Abstraction | Site | Sheaf failure | Risk | First witness |
|---|---|---|---|---|
| | | | | |

## First sheafification

- abstraction:
- canonical repair:
- law:
- falsifier:
- stop point:

## Verification

- commands:
- bypass search:
- migration compatibility:
OUT
