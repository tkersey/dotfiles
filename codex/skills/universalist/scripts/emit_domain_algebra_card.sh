#!/usr/bin/env bash
set -euo pipefail
domain="${1:-domain}"
language="${2:-agnostic}"
cat <<OUT
# Domain Algebra Card: ${domain} (${language})

## Domain

## Carriers

| Carrier | Meaning | Invalid states to block |
| --- | --- | --- |
| | | |

## Operations / constructors / eliminators

| Operation | Signature | Pure/effectful | Owner |
| --- | --- | --- | --- |
| | | | |

## Observations / equality criteria

| Observation | What it sees | What it ignores |
| --- | --- | --- |
| | | |

## Laws

| Law | Observation boundary | Test |
| --- | --- | --- |
| | | |

## Non-laws / counterexamples

| Tempting law | Counterexample | Architecture consequence |
| --- | --- | --- |
| | | |

## Interpreters / effect boundaries

## Property tests / falsifiers

## Architecture implications

## Escalation candidates

- Track B:
- Track D/E:
- Track F:
- Track G:
- Track H:
- Track I:
OUT
