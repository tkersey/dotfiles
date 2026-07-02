#!/usr/bin/env bash
set -euo pipefail
domain="${1:-domain}"
language="${2:-agnostic}"
cat <<OUT
# Track A0 — Domain Algebra Discovery: ${domain} (${language})

## Governing rule

Algebra before architecture.

## Deliverables

1. Domain:
2. Carriers:
3. Operations / constructors / eliminators:
4. Observations / equality criteria:
5. Laws:
6. Non-laws / counterexamples:
7. Interpreters / effect boundaries:
8. Property tests / falsifiers:
9. Architecture implications:
10. Escalation candidates:

## Escalation decision

- Stay local if law tests solve the problem.
- Track D/E if laws fail across boundaries.
- Track F if semantic consumption needs certified context.
- Track G if local uses fail to glue.
- Track H if the current representation is the wrong category/world.
- Track I if the whole effective substrate is in scope.
OUT
