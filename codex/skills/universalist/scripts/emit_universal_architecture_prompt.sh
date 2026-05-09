#!/usr/bin/env bash
set -euo pipefail
cat <<'OUT'
Use $universalist.

I want to change this architecture:

Current:
<modules/APIs/data flow>

Desired:
<target behavior or architecture>

Classify the core seam as one of:
- product / coproduct / refined type / pullback / exponential / free construction
- coherent observations
- transported semantics
- lifted implementation
- residual obligation
- explicit IR / defunctionalization
- ordinary adapter, no universal architecture needed

Then produce:
1. Track
2. Signal
3. Construction
4. Why this instead of nearby alternatives
5. Seam / files
6. Boundary and compatibility plan
7. Before -> After
8. Verification
9. Runtime-only leftovers
10. Canonical boundary artifact, if Track D
11. Law / witness test
12. De-escalation check
13. Next seam, if any
OUT
