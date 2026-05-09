#!/usr/bin/env bash
set -euo pipefail
cat <<'OUT'
# Universal Artifact Matrix

| Pressure | Canonical artifact | First seam | Proof signal |
|---|---|---|---|
| Many consumers interpret commands differently | Free syntax / AST | one command/rule | interpreter parity |
| New internals must satisfy old views | Coherent observations | one endpoint/query | old view parity + overlap coherence |
| Source semantics must move to target surface | Transported semantics | one generated/plugin case | old behavior through embedding |
| Public behavior known before internals | Lifted implementation | one contract case | projection(realizer) == required |
| Public behavior known before internals but P is vague/lossy | Free builder / projection diagnostic | one projection function | project(free(required)) passes or obstruction named |
| Public policy implies internal checks | Residual obligation | one policy clause | missing obligation fails |
| Generated payloads lose provenance | Deferred generation artifact | one generated item | lowering preserves provenance |
| Query/projection sprawl | Observation vocabulary | one projection family | representation-independent observation |
| Callback boundary hides semantics | Explicit IR | one callback family | apply(encoded) == callback fixture |
OUT
