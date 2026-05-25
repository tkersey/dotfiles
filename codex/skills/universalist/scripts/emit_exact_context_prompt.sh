#!/usr/bin/env bash
set -euo pipefail
mode="${1:-audit}"
cat <<OUT
Use \$universalist Track F — Exact Context / semantic consumption boundary.

Mode: ${mode}

Goal:
I want the semantic consumer to receive exactly the right prepared context, not raw retrieved data.

Produce:
1. semantic consumer and task type;
2. task-specific context schema T_q;
3. required observables Obs_q;
4. candidate source worlds and I_candidate;
5. source-to-context mapping M_q;
6. constraint closure/chase steps;
7. provenance, missingness, contradiction, and freshness requirements;
8. observational-core/minimization plan;
9. rendering plan and rendering law;
10. Context Certificate;
11. first witness task;
12. falsifiers for missing, stale, unsupported, contradictory, and irrelevant context.

Do not treat retrieval results as context. Treat retrieval as candidate source-instance generation.
OUT
