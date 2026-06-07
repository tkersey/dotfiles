#!/usr/bin/env bash
set -euo pipefail
cat <<OUT
# Kan mechanics for Boundary Normal Form

For each uncertified boundary, classify mechanics:

| Boundary | Axis | Candidate mechanics | Law | Falsifier | Status |
| --- | --- | --- | --- | --- | --- |
| | extension | Lan/Ran/Delta | | | |
| | lift | Lft/Rft/Freyd | | | |
| | representation | Yoneda/Coyoneda | | | |
| | control-flow | defunctionalized IR/codensity | | | |

Next step:
1. choose one boundary;
2. emit Composition Certificate elaboration;
3. implement artifact + interpreter/projection;
4. add law + falsifier;
5. mark status.
OUT
