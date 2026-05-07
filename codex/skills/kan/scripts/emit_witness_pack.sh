#!/usr/bin/env bash
set -euo pipefail
topic="${1:-pointwise-lan}"
language="${2:-agnostic}"
case "$topic" in
  pointwise-lan|coend-lan|lan)
    cat <<'OUT'
# Pointwise Lan witness

Kan data:
- C = core/source category
- D = target/extended category
- K = inclusion/schema map/embedding
- F = old semantics or source instance
- Witness d = one target object

Implementation:
1. Enumerate K ↓ d: all pairs (c, u: Kc -> d).
2. Create tagged values (c, u, x in F c).
3. Quotient by source morphisms f where u' . Kf = u.
4. Unit eta(c,x) = class(c, id_Kc, x).

Law test:
lan_map(Kf, eta(c,x)) == eta(c', Ff(x))
OUT
    ;;
  pointwise-ran|end-ran|ran)
    cat <<'OUT'
# Pointwise Ran witness

Kan data:
- C = observations/source category
- D = target/new category
- K = observation embedding/projection
- F = old observable behavior
- Witness d = one target object

Implementation:
1. Enumerate d ↓ K: all pairs (c, u: d -> Kc).
2. Build product of F(c) over observations.
3. Keep coherent families satisfying Ff(x_(c,u)) = x_(c',u').
4. Counit epsilon(c,family) = family at (c, id_Kc).

Law test:
Ff(epsilon(c,family)) == epsilon(c', ran_map(Kf,family))
OUT
    ;;
  codensity)
    cat <<'OUT'
# Codensity witness

Shape:
Codensity m a = forall b. (a -> m b) -> m b

Implementation:
1. Lift old monadic/free program.
2. Reassociate binds through continuation form.
3. Lower with pure/return.
4. Compare semantics with direct program.
5. Benchmark representative workload.

Failure tests:
- error ordering unchanged
- resource finalization unchanged
- logs/observable effects unchanged if those are part of semantics
OUT
    ;;
  data-migration)
    cat <<'OUT'
# Data migration witness

Schema mapping K : S -> T
Instance I : S -> Set

Choose:
- Delta_K for restriction/backward compatibility
- Sigma_K = Lan_K for pushforward/generative migration
- Pi_K = Ran_K for coherent/conservative migration

Tests:
- old report over I equals old report over Delta_K(migrated)
- quotient/merge cases documented
- provenance preserved
OUT
    ;;
  *) echo "Unknown topic: $topic" >&2; exit 2 ;;
esac
printf '\n# Language hint: %s\n' "$language"
