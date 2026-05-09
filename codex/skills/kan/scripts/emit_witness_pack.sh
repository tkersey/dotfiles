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
  yoneda|yoneda-observation|observation-boundary|ran-observer)
    cat <<'OUT'
# Yoneda observation witness

Boundary data:
- Construction = Ran / Rft / P_* / codensity / facade
- Boundary map = K or P
- Observed value = model / behavior / facade / public output
- Witness observation = one query / selector / policy / test oracle

Implementation:
1. List sanctioned observations.
2. Represent observation-heavy access through observe/runObservation.
3. Hide raw representation behind the observer boundary.
4. If needed, defunctionalize observers into Observation constructors.
5. Tie the observation runner back to the selected Kan law.

Artifacts:
- Observation case type
- runObservation(value, observation)
- coherence validator for overlapping observations

Law tests:
- observe(lift(value), identityObservation) recovers value, if identity is in scope.
- observing composed maps equals composing observations.
- old projections through Ran/Rft remain coherent.
OUT
    ;;
  coyoneda|coyoneda-generation|generation-boundary|lan-generator)
    cat <<'OUT'
# Coyoneda generation witness

Boundary data:
- Construction = Lan / Lft / generated artifact / migration
- Boundary map = K or P
- Raw payload = one source artifact / event / command / AST node / realizer
- Deferred map/path = one target transformation or projection path

Implementation:
1. Keep raw source payload explicit.
2. Package it with a deferred map/path into the target.
3. Lower only through one interpreter/lowering function.
4. If needed, defunctionalize maps into Path or ProjectionPath constructors.
5. Tie lowering back to the selected Kan law.

Artifacts:
- Generated or Deferred case type
- Path / ProjectionPath case type
- lower / interpretPath / projectImplementation

Law tests:
- lower(identityPath, payload) agrees with original payload/behavior.
- two deferred maps fuse to their composition.
- source provenance survives until lowering.
- Lan/Lft unit or realization law still holds.
OUT
    ;;
  yoneda-coyoneda-lift|yc-lift)
    cat <<'OUT'
# Yoneda/Coyoneda Kan-lift witness

Lift data:
- A = requirements/spec cases
- B = implementation/design choices
- C = observable behavior
- P : B -> C = fixed public projection
- F : A -> C = required public behavior
- Witness a = one contract/test/feature

Yoneda side:
- PublicObservation cases define what can be observed in C.
- runObservation reads a required or projected behavior.

Coyoneda side:
- CandidateRealizer carries raw internal payload.
- ProjectionPath carries deferred path through P.
- projectImplementation lowers the realizer/path pair to observable behavior.

Law test:
for each observation obs:
  runObservation(projectImplementation(realizer(a), path), obs)
  == runObservation(F(a), obs)

Residual:
if no ProjectionPath exists, emit an explicit Obligation instead of silently passing.
OUT
    ;;
  defunctionalization|defun-ran|defun-lan|defun-lift|defun-effects)
    cat <<'OUT'
# Defunctionalization witness

Boundary data:
- Construction = Lan / Ran / Delta / Lft / Rft / codensity / effect-handler
- Boundary map = K or P
- Witness slice = one endpoint / AST node / observation / continuation frame / requirement

Implementation:
1. Identify callbacks/functions crossing the boundary.
2. Create one constructor per function shape.
3. Store each function's free variables as constructor payloads.
4. Replace function application with one interpreter/apply/project function.
5. Test that the interpreter preserves the selected Kan law.

Examples:
- Lan: PathToTarget + interpretPath
- Ran: Observation + runObservation
- Codensity: Frame + applyFrame
- Lft: ImplementationPlan + projectImplementation
- Rft: Obligation + satisfyObligation

Law test:
apply(defunctionalizedCase, input) == originalFunction(input)
and the selected unit/counit/comparison law still holds.
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
  lift-contract-refactor|contract-refactor|outside-in-refactor)
    cat <<'OUT'
# Kan lift contract-first refactor witness

Lift data:
- A = public contract/golden-test cases
- B = internal architecture/design candidates
- C = observable public behavior
- P = fixed projection from internals to public behavior
- F = required behavior for each case
- Witness a = one endpoint/workflow/report/policy case

Implementation:
1. Inventory external commitments for a.
2. Implement or centralize P.
3. Encode F(a) as observations/fixtures.
4. Choose candidate L(a) in B.
5. Project candidate through P and compare to F(a).
6. If equality/coverage fails, emit obligations rather than broad refactoring.

Law test:
for each observation obs:
  observe(P(L(a)), obs) == observe(F(a), obs)

or use a stated preorder/refinement.
OUT
    ;;
  lift-obligation-discovery|obligation-discovery|no-exact-lift)
    cat <<'OUT'
# Kan lift obligation-discovery witness

Lift data:
- A = requirements/tests/policies/reports
- B = internal obligations/capabilities/resources
- C = observable behavior
- P = projection from obligations/capabilities to observations
- F = required behavior
- Witness a = one public commitment

Implementation:
1. Enumerate observations required by F(a).
2. For each observation, ask whether current P can produce it from B.
3. Record missing data, transitions, capabilities, temporal guarantees, projection paths, and coherence requirements.
4. Classify exact, covering, sound, approximate, or no-exact-lift.
5. Add one failing or passing witness test per obligation.

No-exact-lift report:
- required observation:
- why P cannot produce it:
- repair by enriching B / changing P / weakening F / adding dependency / accepting approximation:
OUT
    ;;
  *) echo "Unknown topic: $topic" >&2; exit 2 ;;
esac
printf '\n# Language hint: %s\n' "$language"
