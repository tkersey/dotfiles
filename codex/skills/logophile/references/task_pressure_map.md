# Task Pressure Map

Infer pressures from the task first. Use these defaults only when the task underspecifies them.

For formal computer-science operators, preserve the technical distinction. Do not use a strong term such as `linearizable`, `complete`, `optimal`, or `constant-time` unless the task can support its proof burden.

## Bug fix / regression / review response

Dominant pressures:
- unsound diagnosis
- hidden invariant break
- oversized fix
- missing verification

Default stack candidates:
- `unsound`
- `mechanistic`
- `counterexample-guided`
- `accretive`
- `traceable`

Artifacts:
- Soundness Ledger
- Minimal Counterexample
- Counterexample Refinement Ledger
- Chosen Cut
- proof receipt

## Feature implementation / planned code

Dominant pressures:
- architecture drift
- scope creep
- unnecessary complexity
- weak verification
- special cases replacing a principal solution

Default stack candidates:
- `canonical`
- `principal`
- `parametric`
- `accretive`
- `invariant-preserving`
- `traceable`

Artifacts:
- contract / invariant row
- Principal Solution + Instantiation Map
- implementation seam
- verification receipt

## Plan-to-PR / execution workflow

Dominant pressures:
- analysis without movement
- stale plan graph
- missing proof before ship
- incomplete task closure
- loops that do not reduce the remaining gap

Default stack candidates:
- `actuating`
- `contractive`
- `fixed-point`
- `proof-carrying`
- `traceable`

Artifacts:
- Actuation Receipt
- Contraction Measure
- task graph / completion receipts
- Certificate-Bearing Handoff
- closure gate

## Code review / adversarial audit

Dominant pressures:
- local blindness
- untested assumptions
- regression risk
- misuse hazards
- equivalent-looking states that are not behaviorally equivalent

Default stack candidates:
- `adversarial`
- `counterexample-guided`
- `exhaustive`
- `hazard-seeking`
- `traceable`

Artifacts:
- candidate inventory
- strongest countercase
- Counterexample Refinement Ledger
- change agenda

## Review adjudication / should we act?

Dominant pressures:
- over-acceptance
- reviewer authority bias
- local-validity trap
- additive mutation from comments
- criteria chosen after seeing the preferred answer

Default stack candidates:
- `discriminative`
- `rebuttal-first`
- `criterial`
- `invariant-seeking`
- `ablative`
- `evidence-weighted`

Artifacts:
- resolve-selection map
- no-change countercase
- Criteria Matrix
- governing invariant candidate
- ablation activation receipt

## Soundness / invariant review

Dominant pressures:
- unwitnessed guarantees
- illegal inhabitants
- partial eliminators
- broken preservation/progress
- incoherent abstractions
- soundness/completeness confusion

Default stack candidates:
- `unsound`
- `unwitnessed`
- `ill-typed`
- `total`
- `decidable`
- `preservation-aware`
- `progress-aware`

Artifacts:
- Soundness Ledger
- totality table
- Decision Procedure
- witness receipt
- completeness gap inventory when relevant

## Abstraction teardown / technical debt / deletion

Dominant pressures:
- addition bias
- duplicate truth surfaces
- vestigial scaffolding
- accidental-rhyme merges
- over-preservation
- clients depending on representation accidents

Default stack candidates:
- `ablative`
- `winnowing`
- `quotienting`
- `representation-independent`
- `normalizing`
- `refinement-preserving`

Artifacts:
- Ablation Ledger
- Reduction Certificate
- quotient relation
- client-observation audit
- recomposition proof

## Simplification with strict behavior preservation

Dominant pressures:
- behavior drift
- bad DRY merges
- hidden side effects
- proof weakness
- unclear equality notion

Default stack candidates:
- `extensional`
- `bisimulative`
- `isomorphic`
- `clone-classified`
- `traceable`

Artifacts:
- Observation Contract
- Bisimulation Relation or Isomorphism Card
- duplication map
- LOC / surface delta

Choose the preservation relation explicitly:
- `isomorphic` for invertible structural correspondence
- `bisimulative` for mutually matching transitions
- `observationally-equivalent` for equality under selected observations
- `refinement-preserving` when invalid, obsolete, or unrequired behavior may disappear

## Rewrite systems / canonicalization

Dominant pressures:
- rewrite order changes the result
- overlapping rules diverge
- loops do not terminate
- multiple normal forms survive
- agent or migration paths conflict

Default stack candidates:
- `confluent`
- `terminating`
- `critical-pair-aware`
- `congruence-preserving`
- `normalizing`

Artifacts:
- Confluence Matrix
- Critical-Pair Ledger
- termination measure
- congruence checks
- canonical normal form

## Fixed-point / iterative improvement

Dominant pressures:
- repeated passes that appear productive but do not converge
- no measurable distance to closure
- stale or reopened findings
- loop termination confused with fixed-point stability

Default stack candidates:
- `contractive`
- `monotone`
- `fixed-point`
- `saturating`
- `proof-carrying`

Artifacts:
- Contraction Measure
- Information-Order Map
- Fixed-Point Gate
- saturation stop rule
- current proof receipts

## Counterexample-guided refinement

Dominant pressures:
- each failure creates another local patch
- abstraction too coarse or too broad
- wound-specific tests accumulate
- the model does not explain the counterexample family

Default stack candidates:
- `counterexample-guided`
- `refinement-driven`
- `shrinking`
- `invariant-seeking`
- `principal`

Artifacts:
- Minimal Counterexample
- Counterexample Refinement Ledger
- refinement chain
- governing law / invariant
- principal model candidate

## Protocol / state-machine equivalence

Dominant pressures:
- final outputs match while intermediate behavior diverges
- ordering, liveness, or error transitions differ
- infinite/reactive behavior is judged only by finite examples
- partial transition coverage

Default stack candidates:
- `bisimulative`
- `coinductive`
- `totalizing`
- `progress-aware`
- `confluent`

Artifacts:
- Bisimulation Relation
- coinductive invariant
- transition coverage table
- liveness/progress checks
- critical-pair or convergence checks

## Program analysis / whole-input reasoning

Dominant pressures:
- examples miss reachable bad paths
- concrete execution is too large to enumerate
- path conditions are hidden
- static claims lack sound abstraction

Default stack candidates:
- `abstract-interpreting`
- `symbolic`
- `type-directed`
- `taint-aware`
- `sound`

Artifacts:
- abstract domain / transfer functions
- path-condition ledger
- type obligations
- source-to-sink map
- soundness claim and limitations

## Verification without a direct oracle

Dominant pressures:
- exact expected output unavailable
- tests encode guessed answers
- one implementation is trusted as truth
- failures are too large to understand

Default stack candidates:
- `oracle-aware`
- `metamorphic`
- `differential`
- `property-based`
- `shrinking`

Artifacts:
- Oracle Map
- Metamorphic Relation Suite
- Differential Result Matrix
- generators / properties / shrinkers
- Minimal Counterexample

## Test quality / hardening

Dominant pressures:
- line coverage without defect sensitivity
- narrow handpicked examples
- unreachable state regions
- no failure containment testing

Default stack candidates:
- `mutation-resistant`
- `coverage-guided`
- `fault-injecting`
- `replayable`
- `model-checking`

Artifacts:
- mutation score and surviving-mutant ledger
- coverage frontier
- fault matrix
- Replay Receipt
- model-checker counterexample trace

## Concurrency / concurrent-object correctness

Dominant pressures:
- race-dependent outcomes
- operations appear out of order
- transaction correctness confused with object correctness
- atomicity or real-time order undefined

Default stack candidates:
- `linearizable`
- `serializable`
- `atomic`
- `commutative`
- `idempotent`

Artifacts:
- concurrent history
- linearization points
- serialization graph
- atomicity boundary
- commutativity/idempotence tests

Use the distinction:
- `linearizable` for operation histories that must respect real time
- `serializable` for transaction histories equivalent to a serial order

## Distributed consistency / replication

Dominant pressures:
- stale reads
- conflicting replicas
- partition behavior undefined
- “eventual consistency” used without convergence
- authority claimed without agreement

Default stack candidates:
- `causally-consistent`
- `eventually-consistent`
- `quorum-aware`
- `consensus-backed`
- `partition-aware`
- `deduplicating`

Artifacts:
- happens-before graph
- convergence and conflict contract
- quorum matrix
- consensus authority map
- partition behavior table
- deduplication proof

## Recovery / interrupted workflows

Dominant pressures:
- partial writes
- resumed work from dirty state
- retries duplicate effects
- recovery requires perfect manual reset
- stale receipts influence continuation

Default stack candidates:
- `self-stabilizing`
- `transactional`
- `idempotent`
- `rebaselining`
- `replayable`

Artifacts:
- recovery invariant
- convergence proof
- transaction/rollback boundary
- Baseline Receipt
- Replay Receipt

## Streaming / queues / overload

Dominant pressures:
- unbounded queues
- producer outruns consumer
- retries hide overload
- batch semantics change ordering or failure behavior

Default stack candidates:
- `backpressure-aware`
- `streaming`
- `batching`
- `bounded`
- `fault-contained`

Artifacts:
- demand/capacity contract
- memory/queue bound
- chunk or batch semantics
- failure-containment map

## Algorithm / search selection

Dominant pressures:
- search may be interrupted
- no incumbent best-so-far answer
- heuristics lack guarantees
- branches are explored after they cannot win
- “optimal” is claimed without objective or bound

Default stack candidates:
- `anytime`
- `admissible`
- `branch-and-bound`
- `best-first`
- `pruning`
- `approximation-aware`

Artifacts:
- Incumbent + Remaining-Gap Receipt
- heuristic proof
- frontier ordering
- bounds / pruned branches
- approximation ratio or quality envelope

## Complexity / tractability analysis

Dominant pressures:
- total input size hides the governing parameter
- preprocessing can collapse the hard core
- one expensive step is mistaken for poor sequence cost
- output size dominates runtime

Default stack candidates:
- `parameterized`
- `kernelizing`
- `amortized`
- `output-sensitive`
- `worst-case-aware`
- `asymptotic`

Artifacts:
- parameter map
- kernel instance and equivalence proof
- potential/accounting argument
- complexity bound
- measured crossover

## Performance / dataflow optimization

Dominant pressures:
- full recomputation
- unnecessary materialization
- poor locality
- critical path ignored
- optimization changes semantics

Default stack candidates:
- `incremental`
- `demand-driven`
- `locality-aware`
- `fusion-oriented`
- `work-efficient`
- `span-efficient`
- `zero-copy`

Artifacts:
- invalidation graph
- demand map
- locality / working-set evidence
- fused pipeline
- work/span analysis
- ownership/lifetime proof

## Security / authority design

Dominant pressures:
- ambient authority
- partial policy mediation
- privilege concentration
- unintended information flow
- hidden side channels
- untrusted code escape

Default stack candidates:
- `least-authority`
- `capability-secure`
- `complete-mediation`
- `privilege-separated`
- `noninterfering`
- `sandboxed`

Artifacts:
- authority/capability matrix
- mediation coverage map
- privilege boundary map
- Information-Flow Matrix
- sandbox policy and escape tests

## Cryptographic / low-level security

Dominant pressures:
- secret-dependent timing or memory behavior
- unsafe memory boundary
- parser/tool surface larger than necessary
- untracked untrusted influence

Default stack candidates:
- `constant-time`
- `side-channel-aware`
- `memory-safe`
- `taint-aware`
- `attack-surface-minimizing`
- `fail-closed`

Artifacts:
- timing/branch audit
- side-channel inventory
- unsafe-code / memory-safety audit
- source-to-sink flow map
- attack-surface delta

## API / module abstraction

Dominant pressures:
- clients depend on hidden representation
- implementations satisfy signatures but violate laws
- effects are ambient
- special cases prevent general reuse
- extensions alter old behavior

Default stack candidates:
- `representation-independent`
- `lawful`
- `effect-explicit`
- `parametric`
- `principal`
- `conservative-extending`

Artifacts:
- client-observation audit
- Law Suite
- Effect Signature and Handler Map
- Parametricity Matrix
- Principal Solution
- conservative-extension certificate

## Data / schema decomposition

Dominant pressures:
- decomposition loses information
- constraints require reconstructing the whole
- references break during lifecycle changes
- migrations silently invent defaults
- lineage disappears

Default stack candidates:
- `lossless`
- `dependency-preserving`
- `referential-integrity-preserving`
- `schema-evolution-aware`
- `lineage-preserving`

Artifacts:
- round-trip/losslessness proof
- dependency-preservation matrix
- reference lifecycle audit
- schema evolution matrix
- lineage graph

## Event / ledger architecture

Dominant pressures:
- destructive history rewrite
- derived state mistaken for authority
- replay cannot reproduce state
- supersession is implicit

Default stack candidates:
- `append-only`
- `event-sourced`
- `replayable`
- `monotone`
- `reconciling`

Artifacts:
- append/supersession contract
- event schema and reducer
- replay proof
- information-order map
- reconciliation ledger

## Knowledge extraction / session archaeology

Dominant pressures:
- memory/provenance drift
- noisy hits
- shallow summaries
- unsupported causality

Default stack candidates:
- `forensic`
- `cartographic`
- `provenance-preserving`
- `triangulating`
- `saturating`

Artifacts:
- Provenance Map
- source stratification
- contradiction ledger
- saturation stop rule

## Learning from the past / precedent recovery

Dominant pressures:
- memory treated as authority
- false analogy
- stale or superseded lessons
- precedent with no action delta

Default stack candidates:
- `precedential`
- `provenance-preserving`
- `distinguishing`
- `supersession-aware`
- `actuating`

Artifacts:
- Precedent Ledger
- analogy / distinguishing-facts table
- freshness and supersession chain
- explicit action delta

## Setting precedent / durable rule creation

Dominant pressures:
- one-off decisions silently becoming policy
- unbounded scope
- missing exceptions
- no supersession path

Default stack candidates:
- `nomothetic`
- `constitutive`
- `criterial`
- `traceable`

Artifacts:
- Nomothetic Receipt
- rule, scope, non-governing cases, authority, and supersession condition
- persona when requested: `Nomothete`

## Systems thinking / intervention design

Dominant pressures:
- local optimization
- missed feedback loops
- second-order effects
- wrong control point

Default stack candidates:
- `cybernetic`
- `cartographic`
- `leverage-seeking`
- `actuating`

Artifacts:
- Cybernetic Map
- control-point receipt
- proof of movement

## Simulation / counterfactual world modeling

Dominant pressures:
- toy simulation mistaken for reality
- hidden state or transition rules
- unsupported counterfactuals
- fidelity boundary omitted

Default stack candidates:
- `emulative`
- `counterfactual`
- `dynamical`
- `observational`
- `fidelity-bounded`

Artifacts:
- Emulation Receipt
- Counterfactual Ledger
- Dynamics Map
- Observation Contract
- Fidelity Boundary

## Evaluation / grading / judging

Dominant pressures:
- unstated criteria
- preference disguised as defect
- evidence-free scoring
- no final disposition

Default stack candidates:
- `adjudicative`
- `criterial`
- `evidence-weighted`
- `calibrated`
- `dispositive`

Artifacts:
- Adjudication Ledger
- Criteria Matrix
- Evidence Weighting table
- Dispositive Factor row
- persona when requested: `Arbiter`

## Accounting / reconciliation

Dominant pressures:
- unexplained residuals
- unowned obligations
- state or resources appearing/disappearing without cause
- independent surfaces disagreeing

Default stack candidates:
- `reconciling`
- `conservation-aware`
- `traceable`
- `owner-aware`

Artifacts:
- Reconciliation Ledger
- Conservation Ledger
- residual disposition
- owner map

## Reset / stale state / workflow restart

Dominant pressures:
- stale proof
- outdated branch/head/session memory
- invalidated assumptions
- inherited route errors

Default stack candidates:
- `rebaselining`
- `stale-proof`
- `reconciling`
- `canonicalizing`

Artifacts:
- Baseline Receipt
- stale artifact list
- current authority map

## Hidden behavior / callbacks / defunctionalization

Dominant pressures:
- opaque higher-order control flow
- scattered handlers
- missing totality
- weak inspectability

Default stack candidates:
- `reifying`
- `closed-world`
- `totalizing`
- `inspectable`
- `algebraic`

Artifacts:
- behavior algebra
- constructors / payloads
- total interpreter
- preservation proof

## Research memo / market scan

Dominant pressures:
- weak sourcing
- overclaiming
- shallow synthesis
- bloated prose

Default stack candidates:
- `source-disciplined`
- `calibrated`
- `adversarial`
- `synthetic`

Artifacts:
- source ledger
- confidence map
- counterclaim table

## Planning / strategy

Dominant pressures:
- ill-posed goals
- hidden assumptions
- missing tradeoffs
- false certainty
- search that never produces a valid incumbent

Default stack candidates:
- `ill-posed`
- `calibrated`
- `parsimonious`
- `tractabilizing`
- `anytime`
- `traceable`

Artifacts:
- governing question
- option table
- incumbent + remaining gap
- dominant move

## Naming / policy wording / contracts

Dominant pressures:
- semantic drift
- obligation drift
- vague scope
- overloaded terminology
- weak doctrine grammar
- mode/persona confusion
- formal term used without its actual guarantee

Default stack candidates:
- `precise`
- `scoped`
- `obligation-preserving`
- `distinctive`
- `operator-aligned`

Notes:
- `precise`, `scoped`, `obligation-preserving`, and `operator-aligned` are task-local descriptive labels.
- Use them only if they produce an actual gain in the doctrine block.
- Prefer mode adjectives/gerunds and reserve persona nouns for explicit persona requests.
- Preserve formal distinctions such as `confluent` vs `deterministic`, `principal` vs `optimal`, and `linearizable` vs `serializable`.
- Replace generic defaults with sharper domain terms whenever the task supports them.
