#!/usr/bin/env bash
set -euo pipefail
carrier="${1:-Carrier}"
language="${2:-agnostic}"
cat <<OUT
# Law Table: ${carrier} (${language})

| Carrier | Operation(s) | Observation | Law | Status | Test/falsifier |
| --- | --- | --- | --- | --- | --- |
| ${carrier} | | | | true / false / conditional / unknown | |

## Prompts

- What observation makes this law meaningful?
- What stronger observation falsifies it?
- What property test would discover a counterexample?
- What architecture changes if the law is false?
OUT
