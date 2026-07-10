# Doctrine Word Bank

Use these as defaults, not mandates. Pick words for procedural gain, not prestige.

A good doctrine word activates an operator and leaves an observable behavioral consequence. A weak doctrine word only improves tone.

For the expanded computer-science catalog and formal distinctions, see [computer_science_doctrine.md](computer_science_doctrine.md).

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
- `orthogonalizing`: separate entangled concerns into independently testable axes without losing their coupling map.
  - Cash-out: factor/coupling matrix.
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

## Rewrite systems / convergence operators

- `confluent`: permit many paths but require them to join at one canonical result.
  - Cash-out: Confluence Matrix or Critical-Pair Ledger.
- `terminating`: require rewrites, retries, recursion, or workflow chains to reach a stopping state.
  - Cash-out: termination measure or ranking function.
- `critical-pair-aware`: find overlapping rules whose independent application may diverge.
  - Cash-out: Critical-Pair Ledger.
- `contractive`: require every iteration to reduce a named distance to closure.
  - Cash-out: Contraction Measure.
- `monotone`: preserve an explicit information, authority, or state order.
  - Cash-out: Information-Order Map.
- `inflationary`: preserve the prior state while moving upward in the declared order.
  - Cash-out: inflationary transition proof.
- `congruence-preserving`: preserve equivalence under every permitted context.
  - Cash-out: context/congruence checks.
- `conservative-extending`: add expressive power without changing existing valid meaning.
  - Cash-out: conservative-extension certificate.
- `commutative`: make independent operation order irrelevant.
  - Cash-out: commutativity matrix.
- `associative`: make grouping irrelevant.
  - Cash-out: associativity law tests.
- `distributive`: expose valid interaction and decomposition between operations.
  - Cash-out: distributive-law tests.

## Semantics / abstraction operators

- `principal`: seek the most general solution satisfying the constraints.
  - Cash-out: Principal Solution and Instantiation Map.
- `parametric`: require uniform behavior across admissible representations.
  - Cash-out: Parametricity Matrix.
- `extensional`: judge equality by selected observations rather than internal construction.
  - Cash-out: Observation Contract.
- `representation-independent`: prevent clients from depending on hidden representation choices.
  - Cash-out: client-observation audit.
- `bisimulative`: require mutually matching observable transitions.
  - Cash-out: Bisimulation Relation.
- `coinductive`: reason about ongoing or infinite behavior through observations.
  - Cash-out: coinductive invariant.
- `inductive`: construct or prove from constructors and structurally smaller cases.
  - Cash-out: constructor coverage and induction hypothesis.
- `lawful`: require an abstraction to satisfy its claimed laws.
  - Cash-out: Law Suite.
- `decidable`: define a terminating decision procedure for every admissible input.
  - Cash-out: Decision Procedure.
- `complete`: cover every semantically valid case.
  - Cash-out: completeness argument or missing-case inventory.
- `effect-explicit`: expose effects in the type, protocol, or interpreter.
  - Cash-out: Effect Signature and Handler Map.
- `referentially-transparent`: make substitution by value behavior-preserving.
  - Cash-out: side-effect/capture audit.

## Program-analysis / refinement operators

- `abstract-interpreting`: reason soundly over a tractable over-approximation of concrete execution.
  - Cash-out: abstract domain and sound transfer functions.
- `symbolic`: reason over variables and path constraints instead of only concrete examples.
  - Cash-out: path-condition ledger.
- `counterexample-guided`: let failures refine the abstraction or invariant rather than create wound-specific patches.
  - Cash-out: Counterexample Refinement Ledger.
- `refinement-driven`: add distinctions only when forced by accepted observations or failed proof.
  - Cash-out: refinement chain.
- `proof-carrying`: make validation evidence travel with the result across boundaries.
  - Cash-out: Certificate-Bearing Handoff.
- `type-directed`: let type and inhabitation obligations drive construction and search.
  - Cash-out: type-obligation map.
- `taint-aware`: track untrusted influence from sources to sinks.
  - Cash-out: source-to-sink flow map.

## Verification / oracle operators

- `shrinking`: reduce a failure to the smallest counterexample that still exhibits it.
  - Cash-out: Minimal Counterexample.
- `metamorphic`: test invariant relations when no exact expected output exists.
  - Cash-out: Metamorphic Relation Suite.
- `differential`: compare independent implementations or versions and investigate disagreement.
  - Cash-out: Differential Result Matrix.
- `property-based`: generate broad input families from invariants.
  - Cash-out: generators, properties, and shrinkers.
- `oracle-aware`: name what makes a result checkable and where no direct oracle exists.
  - Cash-out: Oracle Map.
- `coverage-guided`: steer generation toward unexplored control-flow, state, or semantic regions.
  - Cash-out: coverage frontier.
- `mutation-resistant`: require tests to detect plausible injected defects.
  - Cash-out: mutation score and surviving-mutant ledger.
- `model-checking`: explore a bounded state space against safety or temporal properties.
  - Cash-out: model, properties, and counterexample trace.
- `replayable`: capture enough state and ordering to reproduce behavior.
  - Cash-out: Replay Receipt.
- `fault-injecting`: deliberately test failure containment and recovery.
  - Cash-out: fault matrix.

## Concurrency / distributed operators

- `linearizable`: make each operation appear atomic while respecting real-time order.
  - Cash-out: concurrent history and linearization points.
- `serializable`: make concurrent transactions equivalent to some serial execution.
  - Cash-out: serialization graph.
- `causally-consistent`: preserve cause-before-effect ordering.
  - Cash-out: happens-before graph.
- `eventually-consistent`: permit bounded divergence only with a convergence and visibility contract.
  - Cash-out: convergence condition and conflict policy.
- `quorum-aware`: reason about overlap, stale reads, and failure thresholds.
  - Cash-out: quorum matrix.
- `consensus-backed`: require an agreement protocol before claiming one authoritative order or value.
  - Cash-out: consensus authority map.
- `self-stabilizing`: converge back to a valid state from reachable dirty or partial states.
  - Cash-out: recovery variant and convergence proof.
- `fault-contained`: bound failure propagation to explicit regions.
  - Cash-out: fault-containment map.
- `partition-aware`: name behavior under communication partitions.
  - Cash-out: partition behavior table.
- `backpressure-aware`: make upstream production respond to downstream capacity.
  - Cash-out: demand/capacity contract.
- `transactional`: bind a multi-step mutation under an explicit atomicity/isolation/durability contract.
  - Cash-out: transaction boundary.
- `atomic`: make an operation indivisible at the relevant observation boundary.
  - Cash-out: atomicity proof.
- `deduplicating`: make repeated delivery converge on one logical effect.
  - Cash-out: deduplication key and retry proof.

## Algorithm / search operators

- `anytime`: maintain a valid incumbent at every interruption point and improve it with more budget.
  - Cash-out: Incumbent + Remaining-Gap Receipt.
- `admissible`: use a heuristic that does not overestimate remaining cost.
  - Cash-out: admissibility argument.
- `consistent-heuristic`: require heuristic values to obey transition consistency.
  - Cash-out: heuristic consistency checks.
- `branch-and-bound`: prune branches whose best possible result cannot beat the incumbent.
  - Cash-out: incumbent, bounds, and pruned-branch ledger.
- `best-first`: expand the most promising frontier item under an explicit score.
  - Cash-out: frontier ordering.
- `pruning`: remove search branches proven unable to affect the answer.
  - Cash-out: pruning rule and completeness impact.
- `kernelizing`: reduce a hard problem to a smaller equivalent instance.
  - Cash-out: kernel instance and equivalence proof.
- `parameterized`: expose the structural parameter that governs difficulty.
  - Cash-out: parameter map and complexity claim.
- `output-sensitive`: measure work relative to input plus produced output.
  - Cash-out: output-sensitive complexity bound.
- `amortized`: evaluate cost over an operation sequence.
  - Cash-out: potential or accounting argument.
- `competitive`: compare an online strategy with the best offline strategy.
  - Cash-out: competitive ratio.
- `worst-case-aware`: test catastrophic inputs or adversarial schedules.
  - Cash-out: worst-case bound or adversarial test.
- `approximation-aware`: state the quality bound when exact optimization is infeasible.
  - Cash-out: approximation ratio or quality envelope.
- `randomized`: state probability, seedability, and failure bounds.
  - Cash-out: probabilistic guarantee.
- `derandomizing`: replace randomness with deterministic structure when proof or repeatability requires it.
  - Cash-out: deterministic substitute and comparison.

## Performance / dataflow operators

- `incremental`: recompute only the dependency closure invalidated by change.
  - Cash-out: invalidation graph.
- `demand-driven`: compute or retrieve only what downstream observations require.
  - Cash-out: demand map.
- `locality-aware`: keep data and computation near reuse, ownership, or failure boundaries.
  - Cash-out: locality map.
- `cache-conscious`: account for working-set and cache behavior.
  - Cash-out: cache evidence.
- `zero-copy`: avoid unnecessary materialization while preserving ownership/lifetime safety.
  - Cash-out: copy count and lifetime proof.
- `streaming`: process bounded chunks without requiring the full input in memory.
  - Cash-out: memory bound and chunk contract.
- `batching`: amortize fixed costs while preserving ordering and failure semantics.
  - Cash-out: batch contract.
- `fusion-oriented`: combine adjacent passes and remove intermediate structures.
  - Cash-out: fused pipeline and preservation proof.
- `work-efficient`: keep total parallel work near the best sequential work.
  - Cash-out: work analysis.
- `span-efficient`: minimize the critical path.
  - Cash-out: span/critical-path analysis.
- `asymptotic`: choose by scaling behavior, then validate constants against the workload.
  - Cash-out: complexity model and measured crossover.
- `bounded`: enforce explicit limits on time, memory, retries, queues, fanout, or state.
  - Cash-out: resource budget.

## Security / authority operators

- `hygienic`: prevent unintended capture of names, context, authority, state, or assumptions.
  - Cash-out: Capture Audit.
- `end-to-end`: put the guarantee at the endpoint capable of verifying it.
  - Cash-out: endpoint verification map.
- `least-authority`: give each component only the capabilities required.
  - Cash-out: authority/capability matrix.
- `capability-secure`: represent authority as explicit unforgeable capabilities.
  - Cash-out: capability graph.
- `complete-mediation`: check authority on every access path.
  - Cash-out: mediation coverage map.
- `privilege-separated`: split high-risk authority from ordinary computation.
  - Cash-out: privilege boundary map.
- `noninterfering`: prevent forbidden inputs or principals from influencing protected observations.
  - Cash-out: Information-Flow Matrix.
- `constant-time`: prevent secrets from influencing timing or comparable resource behavior.
  - Cash-out: timing/branch audit.
- `side-channel-aware`: inventory information leakage through timing, memory, logs, caches, errors, or resources.
  - Cash-out: side-channel inventory.
- `memory-safe`: prevent invalid memory access and ownership violations.
  - Cash-out: memory-safety boundary.
- `attack-surface-minimizing`: reduce exposed operations, parsers, privileges, protocols, and dependencies.
  - Cash-out: attack-surface delta.
- `sandboxed`: confine untrusted execution with explicit resource and capability limits.
  - Cash-out: sandbox policy and escape tests.

## Data / schema operators

- `lossless`: preserve all information required by the live contract.
  - Cash-out: round-trip or losslessness proof.
- `dependency-preserving`: preserve constraints needed for local validation after decomposition.
  - Cash-out: dependency-preservation matrix.
- `referential-integrity-preserving`: maintain valid references across lifecycle transitions.
  - Cash-out: reference lifecycle audit.
- `schema-evolution-aware`: make versioning, defaults, unknown fields, and migration ownership explicit.
  - Cash-out: schema evolution matrix.
- `append-only`: express history through additions and supersession rather than destructive rewrite.
  - Cash-out: append/supersession contract.
- `event-sourced`: treat events as authority and state as replayable projection.
  - Cash-out: event schema, reducer, and replay proof.
- `lineage-preserving`: keep the derivation path from source to result.
  - Cash-out: lineage graph.

## Reset / stale-state control

- `rebaselining`: bind to the current authoritative state and invalidate stale assumptions or receipts.
  - Cash-out: Baseline Receipt.
- `epoching`: create a new state generation and migrate, preserve, retire, or invalidate pre-epoch assumptions.
  - Cash-out: Epoch Boundary.
- `renormalizing`: restore canonical normal form after drift.
  - Cash-out: normal-form restoration receipt.
- `reconciling`: account for every material input, output, obligation, transition, and residual.
  - Cash-out: Reconciliation Ledger.
- `conservation-aware`: permit no material state, resource, obligation, or authority to appear or disappear without a witnessed transition.
  - Cash-out: Conservation Ledger.

## Precedent / norm-setting operators

- `precedential`: recover a prior case, extract its rule, distinguish the current facts, and apply only what still governs.
  - Cash-out: Precedent Ledger with provenance, analogy, distinctions, freshness, supersession, and action delta.
- `distinguishing`: identify facts that prevent a superficially similar precedent from controlling.
  - Cash-out: distinguishing-facts row.
- `supersession-aware`: reject a prior rule when newer evidence or policy has replaced it.
  - Cash-out: supersession chain.
- `nomothetic`: deliberately establish a scoped rule that future cases may inherit.
  - Cash-out: Nomothetic Receipt.
- `constitutive`: create or change the governing structure rather than merely applying it.
  - Cash-out: Constitutive Receipt.

## Simulation / world-modeling operators

- `emulative`: build an executable surrogate that preserves behavior relevant to the decision.
  - Cash-out: Emulation Receipt.
- `counterfactual`: vary one intervention while naming held-constant assumptions.
  - Cash-out: Counterfactual Ledger.
- `dynamical`: model state, transitions, time, delays, feedback, and attractors.
  - Cash-out: Dynamics Map.
- `observational`: define measurements by which model and reality are compared.
  - Cash-out: Observation Contract.
- `fidelity-bounded`: state where the surrogate is validated, approximate, unknown, or unsupported.
  - Cash-out: Fidelity Boundary.
- `surrogative`: provide a lower-cost or safer stand-in for a real system.
  - Cash-out: Surrogate Contract.
- `agentic`: model actors as goal-seeking entities with policies, information, incentives, and adaptation.
  - Cash-out: actor/policy map.
- `world-modeling`: represent environment, actors, state, actions, observations, constraints, and transition rules.
  - Cash-out: World Model.

## Evaluation / judgment operators

- `adjudicative`: judge claims, artifacts, or options against explicit criteria and issue a disposition.
  - Cash-out: Adjudication Ledger.
- `criterial`: declare the standard before scoring, comparing, or ruling.
  - Cash-out: Criteria Matrix.
- `evidence-weighted`: weight evidence and counterevidence rather than authority, fluency, or preference.
  - Cash-out: Evidence Weighting table.
- `dispositive`: identify the fact, rule, or test that determines the outcome.
  - Cash-out: Dispositive Factor row.
- `calibrated`: match confidence, severity, and finality to evidence.
  - Cash-out: confidence/disposition ledger.

## Systems / knowledge extraction

- `forensic`: extract truth from traces, artifacts, contradictions, and provenance.
  - Cash-out: Provenance Map.
- `cartographic`: map knowledge surfaces, authority gradients, blind spots, and high-yield query paths.
  - Cash-out: System Map.
- `cybernetic`: model feedback loops, control points, signals, delays, adaptation, and second-order effects.
  - Cash-out: Cybernetic Map.
- `provenance-preserving`: keep source, freshness, and confidence attached to claims.
  - Cash-out: evidence/source ledger.
- `stratified`: rank evidence by authority, freshness, and closeness to event.
  - Cash-out: source stratification table.
- `triangulating`: cross-check claims across independent surfaces.
  - Cash-out: triangulation ledger.
- `abductive`: infer the best explanatory model, then test disconfirming evidence.
  - Cash-out: hypothesis ledger with falsifiers.
- `saturating`: search until marginal evidence no longer changes the route or model.
  - Cash-out: saturation stop rule.

## Hidden behavior / type-theoretic architecture

- `reifying`: make hidden behavior explicit as data.
  - Cash-out: behavior algebra with constructors, payloads, total interpreter, and preservation proof.
- `totalizing`: make the interpreter, handler, or eliminator total over legal constructors.
  - Cash-out: totality table.
- `algebraic`: represent behavior as carriers, operations, observations, and laws.
  - Cash-out: law catalog or behavior algebra.
- `closed-world`: make an enumerable behavior space explicit.
  - Cash-out: closed case inventory.
- `inspectable`: make behavior loggable, replayable, serializable, diffable, cacheable, routable, or testable.
  - Cash-out: inspection/replay proof.

## Failure-mode words

- `unsound`: reject unsupported inferences; surface missing premises and invalid guarantees.
- `unwitnessed`: a guarantee lacks a concrete witness.
- `ill-typed`: the representation admits values or transitions outside the claimed domain.
- `illegal inhabitant`: an impossible state is representable.
- `partial`: a handler or case split covers only part of the intended domain.
- `non-total`: a required path can fail to produce a legal continuation.
- `incoherent`: layers disagree about an abstraction, state, or protocol.
- `non-compositional`: behavior works locally but fails under composition.
- `ill-founded`: recursion, retries, or dependency chains lack a terminating/progress-preserving shape.
- `vacuous`: reject empty, tautological, or content-free claims.
- `spurious`: challenge accidental patterns and misleading correlations.
- `pathological`: hunt edge cases and strange failure surfaces.
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
- `tail-proof`: put proof and next action where the CLI user will see them.

## Persona nouns

Use persona nouns only when the user explicitly asks for a role/persona. Keep the operating mode separate from the persona.

- `nomothete`: a precedent-setter or lawgiver; pair with `NOMOTHETIC` mode.
- `arbiter`: a criteria-backed judge; pair with `ADJUDICATIVE` mode.
- `emulator`: a builder/operator of an executable surrogate; pair with `EMULATIVE` mode.

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
