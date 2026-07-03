# Doctrine Word Bank

Use these as defaults, not mandates. Pick words for procedural gain, not prestige.

A good doctrine word activates an operator and leaves an artifact. A weak doctrine word only improves tone.

## Action / execution operators

- `actuating`: find the control point, actuate the lever, and prove state movement.
  - Cash-out: Actuation Receipt.
  - Use when: the task is understood enough to move, but the agent risks staying in analysis.
- `lever-seeking`: identify the smallest intervention that changes the outcome.
  - Cash-out: control-point map or levered intervention row.
- `dominance-tested`: choose the route that beats alternatives, not merely one that works.
  - Cash-out: dominance row with rejected alternatives.
- `constructive`: produce an actual witness, plan, patch, proof, artifact, or experiment.
  - Cash-out: constructed object and proof signal.
- `decisive`: collapse plausible options into one chosen route when evidence is sufficient.
  - Cash-out: selected route plus countercase disposition.

## Problem-shaping operators

- `tractabilizing`: reshape the problem into a solvable form before solving it.
  - Cash-out: Tractability Receipt.
- `factorizing`: decompose the whole into factors with contracts and recomposition.
  - Cash-out: Factorization Map.
- `winnowing`: factor the whole, retain only live obligations, and remove what no longer earns retention.
  - Cash-out: Winnowing Ledger or Reduction Certificate.
- `quotienting`: collapse distinctions with no semantic consequence into equivalence classes.
  - Cash-out: quotient relation, congruence witnesses, retained distinction witnesses.
- `normalizing`: recompose survivors into canonical normal form.
  - Cash-out: normal-form gate.
- `refinement-preserving`: preserve required behavior while invalid, obsolete, or unrequired behavior may disappear.
  - Cash-out: preservation relation in a Reduction Certificate.

## Reduction / deletion operators

- `ablative`: remove accumulated surface while preserving the live contract.
  - Cash-out: Ablation Activation Receipt and Ablation Ledger or evidence-backed `not-required`.
- `dominated`: another route covers the obligation with lower complexity or stronger proof.
  - Cash-out: dominance row with replacement path.
- `subsumed`: the local abstraction no longer owns a distinct obligation.
  - Cash-out: subsumption row with new owner.
- `vestigial`: the former obligation is retired, moved, or obsolete.
  - Cash-out: obligation-history row.
- `uninhabited`: a branch or state has no legal runtime inhabitant under current constructors and invariants.
  - Cash-out: state-space row and deletion/assertion decision.
- `deforesting`: remove pass-through wrappers, adapters, mappers, and intermediate structures that own no policy or invariant.
  - Cash-out: pass-through chain collapse candidate.
- `conservative`: preserve public behavior and compatibility unless retirement is explicit.
  - Cash-out: keep/delete/decommission proof.
- `isomorphic`: strict preservation relation; behavior or structure is preserved up to mapping.
  - Cash-out: Isomorphism Card.
  - Warning: not a reduction operator by itself.

## Reset / stale-state control

- `rebaselining`: bind to the current authoritative state and invalidate stale assumptions or receipts.
  - Cash-out: Baseline Receipt.
- `epoching`: create a new state generation and migrate, preserve, retire, or invalidate pre-epoch assumptions.
  - Cash-out: Epoch Boundary.
- `renormalizing`: restore canonical normal form after drift.
  - Cash-out: normal-form restoration receipt.
- `reconciling`: account for every material input, output, obligation, transition, and residual.
  - Cash-out: Reconciliation Ledger.

## Systems / knowledge extraction

- `forensic`: extract truth from traces, artifacts, contradictions, and provenance.
  - Cash-out: Provenance Map.
- `cartographic`: map knowledge surfaces, authority gradients, blind spots, and high-yield query paths.
  - Cash-out: System Map.
- `cybernetic`: model feedback loops, control points, signals, delays, adaptation, and second-order effects.
  - Cash-out: Cybernetic Map.
- `provenance-preserving`: keep source, freshness, and confidence attached to material claims.
  - Cash-out: evidence/source ledger.
- `stratified`: rank evidence by authority, freshness, and closeness to event.
  - Cash-out: source stratification table.
- `triangulating`: cross-check claims across independent surfaces.
  - Cash-out: triangulation ledger.
- `abductive`: infer the best explanatory model, then test disconfirming evidence.
  - Cash-out: hypothesis ledger with falsifiers.
- `saturating`: keep searching until marginal evidence no longer changes the route or model.
  - Cash-out: saturation stop rule.

## Hidden behavior / type-theoretic architecture

- `reifying`: make hidden behavior explicit as data.
  - Cash-out: behavior algebra: constructors, payloads, total interpreter, preservation proof.
- `totalizing`: make the interpreter, handler, or eliminator total over legal constructors.
  - Cash-out: totality table.
- `algebraic`: represent behavior as carriers, operations, observations, and laws.
  - Cash-out: law catalog or behavior algebra.
- `closed-world`: the behavior space is finite/enumerable enough to make cases explicit.
  - Cash-out: closed case inventory.
- `inspectable`: behavior can be logged, replayed, serialized, diffed, cached, routed, or tested.
  - Cash-out: inspection/replay proof.

## Failure-mode words

- `unsound`: reject unsupported inferences; surface missing premises and invalid guarantees.
- `unwitnessed`: a guarantee lacks a concrete witness: invariant, check, construction, type restriction, or test.
- `ill-typed`: the representation admits states, transitions, or values that do not fit the claimed domain.
- `illegal inhabitant`: an impossible state is representable.
- `partial`: an eliminator, handler, or case split only works for part of the intended domain.
- `non-total`: a required path can fail to produce a legal continuation.
- `incoherent`: layers disagree about what an abstraction, state, or protocol means.
- `non-compositional`: behavior works locally but fails when combined with adjacent paths.
- `ill-founded`: retries, recursion, dependency chains, or state transitions lack a terminating/progress-preserving structure.
- `vacuous`: reject empty, tautological, or content-free claims.
- `spurious`: challenge accidental patterns and misleading correlations.
- `pathological`: hunt edge cases and weird failure surfaces.
- `ill-posed`: question whether the task is specified tightly enough.
- `confounded`: look for mixed causes or ambiguous attribution.
- `hazard-seeking`: hunt misuse traps and foot-guns.
- `fail-closed`: prefer safe refusal over silent permissive failure.

## Reasoning-mode words

- `mechanistic`: explain causal chains, not symptoms.
- `falsifiable`: frame claims as testable and disprovable.
- `canonical`: prefer standard forms and primary paths.
- `compositional`: break the task into parts with explicit interfaces.
- `parsimonious`: minimize assumptions and moving parts.
- `adversarial`: try to break the first plausible answer.
- `source-disciplined`: prefer primary and authoritative evidence.
- `calibrated`: match confidence to evidence.
- `synthetic`: compress many signals into a concise comparative frame.
- `coherent`: ensure definitions, behavior, and layers agree globally.

## Type-theoretic / soundness words

- `witness-bearing`: every guarantee has a visible witness.
- `preservation-aware`: transformations preserve the promised invariant.
- `progress-aware`: valid states can keep moving without getting stuck.
- `refinement-first`: lower-level representations preserve higher-level contracts.
- `total`: handlers and eliminators cover the intended domain.
- `inhabitance-aware`: ask what states are newly possible and whether they should be.
- `constructor/eliminator-aware`: check both what creates a state and what consumes it.
- `well-founded`: recursion, retries, and state transitions have a terminating or progress-preserving shape.

## Scope / execution words

- `accretive`: prefer reviewable change that increases capability without broadening invalid states.
- `surgical`: minimize blast radius and irrelevant edits.
- `orthogonal`: keep concerns separated.
- `reversible`: leave a low-cost path to back out or isolate.
- `idempotent`: make repeated application safe.
- `deterministic`: control hidden state, time, and randomness.
- `hermetic`: reduce ambient dependencies and hidden context.
- `surface-area-minimizing`: keep interfaces and complexity small.
- `contract-first`: define success and invariants before editing.
- `seam-conscious`: choose the smallest stable boundary that can carry the fix.

## Verification / reporting words

- `traceable`: tie claims to evidence, diffs, tests, or sources.
- `exhaustive`: cover all material branches, not just the happy path.
- `invariant-preserving`: preserve named truths across change.
- `auditable`: make the review path legible to others.
- `reproducible`: make the result checkable by rerunning.
- `fixed-point`: stop only when a fresh pass finds no material change.
- `saturating`: keep iterating while new material findings still appear.
- `tail-proof`: put the proof and next action where the CLI user will see it.

## Weak words unless made operational

- `smart`
- `deep`
- `insightful`
- `nuanced`
- `thoughtful`
- `sophisticated`
- `elegant`
- `rigorous`

Only keep these if the surrounding doctrine block turns them into explicit checks, artifacts, or constraints.
