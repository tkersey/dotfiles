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
- free syntax
- coherent observations
- transported semantics
- lifted implementation
- free builder behind projection
- obstruction report behind projection
- residual obligations
- behavioral coalgebra
- effect signature + handlers
- explicit first-order IR
- ordinary adapter, no universal framing

Then produce:
1. Track
2. Signal
3. worlds and boundary
4. construction / canonical boundary artifact
5. why this instead of nearby alternatives
6. first witness slice
7. Yoneda/Coyoneda/defunctionalization opportunities if relevant
8. Freyd/AFT projection diagnostic if lift-shaped
9. effect or coalgebra law if behavior is ongoing or multi-handler
10. exact files to inspect/change
11. tests to add first
12. smallest safe refactor
13. runtime-only leftovers
14. falsifier / overkill condition
OUT
