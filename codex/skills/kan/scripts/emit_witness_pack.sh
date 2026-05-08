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
  left-kan-lift|lft|lift-realization)
    cat <<'OUT'
# Left Kan lift witness

Kan data:
- A = requirements/features/tests
- B = implementation/internal choices
- C = observable/public behavior
- P = fixed projection B -> C
- F = desired behavior A -> C
- Witness a = one requirement or feature

Implementation:
1. Keep P explicit as the only public projection.
2. Synthesize or choose L(a) in B.
3. Provide eta(a): F(a) -> P(L(a)).
4. In posets: choose least b such that F(a) <= P(b).

Law test:
F(a) <= P(left_lift(a))
and no smaller implementation still satisfies that inequality.
OUT
    ;;
  right-kan-lift|rift|lift-obligation)
    cat <<'OUT'
# Right Kan lift witness

Kan data:
- A = requirements/features/tests
- B = implementation obligations/capabilities
- C = observable/public behavior
- P = fixed projection B -> C
- F = desired or accepted behavior A -> C
- Witness a = one requirement or test

Implementation:
1. Keep P explicit as the only public projection.
2. Derive R(a) in B as residual obligations or sound internal approximation.
3. Provide epsilon(a): P(R(a)) -> F(a).
4. In posets: choose greatest b such that P(b) <= F(a).

Law test:
P(right_lift(a)) <= F(a)
and no larger implementation remains sound under that inequality.
OUT
    ;;
  architecture-transformation|extension-vs-lift)
    cat <<'OUT'
# Architecture transformation witness

1. Name the boundary.
2. Decide where the unknown sits.

Extension:
  C --K--> D, known F:C->E, unknown D->E.

Lift:
  A --?--> B, known P:B->C and F:A->C, unknown A->B.

3. Pick one witness slice.
4. Write one law test.
5. Move one module through the new boundary.
6. Generalize only after the witness passes.
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
