# Precision Lexicon

Use these as guarded phrase replacements. A replacement is valid only when it preserves meaning, obligation, uncertainty, agency, and copy-paste safety.

For formal computer-science terms, preserve the proof burden. A sharper term is invalid when the surrounding task cannot support its actual guarantee.

For explanatory depth and productive non-closure, see [depth_deliberation_doctrine.md](depth_deliberation_doctrine.md) and [depth_deliberation_probe_cases.md](depth_deliberation_probe_cases.md).

## Generic -> sharper defaults

- `improve` -> `tighten`, `harden`, `simplify`, `stabilize`, `clarify`, `validate`, `defuse`, `accelerate`, `actuate`, `normalize`, `converge`, or `incrementalize` when the local gain is clear.
- `handle` -> `reject`, `normalize`, `parse`, `route`, `validate`, `recover`, `surface`, `fail-closed`, `totalize`, `reconcile`, `deduplicate`, or `mediate` when the behavior is known.
- `deal with` -> name the action: `triage`, `isolate`, `resolve`, `defer`, `route`, `instrument`, `prove`, `document`, `rebaseline`, `decommission`, `serialize`, or `stabilize`.
- `make better` -> name the axis: `more deterministic`, `more confluent`, `more traceable`, `less coupled`, `more canonical`, `lower blast radius`, `more witness-backed`, `less surface-bearing`, `more incremental`, or `more fault-contained`.
- `things` / `stuff` -> name the object: `comments`, `invariants`, `handlers`, `paths`, `checks`, `risks`, `artifacts`, `surfaces`, `obligations`, `receipts`, `transitions`, `replicas`, `capabilities`, or `oracles`.
- `issue` -> `defect`, `risk`, `regression`, `invariant break`, `foot-gun`, `mismatch`, `gap`, `unreconciled residual`, `soundness gap`, `critical pair`, `race`, or `oracle gap` when the class is known.
- `problem` -> `failure mode`, `constraint conflict`, `soundness gap`, `scope mismatch`, `evidence gap`, `routing gap`, `unwitnessed guarantee`, `state-space mismatch`, `tractability bottleneck`, or `consistency violation` when known.
- `review feedback` -> `review claim`, `review finding`, `review suggestion`, `review disposition`, `counterexample`, or `warrant` depending on context.
- `solve` -> `tractabilize`, `actuate`, `remediate`, `adjudicate`, `construct`, `prove`, `search`, `synthesize`, or `decide` when the task shape is known.
- `reset` -> `rebaseline`, `epoch`, `reinitialize`, or `renormalize` depending whether authority, generation, runtime state, or canonical form is changing.
- `decompose` -> `factorize`, `orthogonalize`, `partition`, or `kernelize` depending whether the task exposes factors, independent axes, distributed regions, or a smaller equivalent instance.
- `reduce` / `remove what is unnecessary` -> `winnow`, `quotient`, `ablate`, `prune`, `deforest`, or `normalize` depending whether the task retains live obligations, collapses indistinguishable distinctions, removes unearned surface, eliminates search branches, removes intermediates, or reaches canonical form.
- `account for` -> `reconcile`, `attribute`, `conserve`, or `amortize` depending whether the task balances surfaces, assigns causes/owners, proves nothing appeared/disappeared without a transition, or distributes cost across a sequence.
- `dig deeper` -> `be excavatory` when the task should descend through causal, representational, historical, ownership, or invariant layers until the route changes.
- `ruminate harder` -> `be aporetic` when a genuine contradiction or underdetermination must remain open long enough to expose the missing distinction or decisive evidence.

## Coding and review language

- `works` -> `passes the targeted check`, `preserves the contract`, `closes the gate`, `satisfies the invariant`, `converges to the canonical result`, or `moves the system state`.
- `safe` -> `fail-closed`, `bounded`, `reversible`, `invariant-preserving`, `permission-checked`, `witness-backed`, `memory-safe`, `noninterfering`, or `no broader blast radius`.
- `test it` -> `verify the changed path`, `reproduce the failure`, `exercise the invariant`, `run the closure gate`, `prove movement`, `check the metamorphic relation`, or `differentially compare implementations`.
- `fix this` -> `remediate the material finding`, `close the invariant break`, `refine the model from the counterexample`, `apply the narrowest sufficient change`, or `actuate the selected lever`.
- `review this` -> `adjudicate the claim`, `stress the changeset`, `audit invariants`, `verify readiness`, `test the strongest countercase`, or `check conformance to the declared consistency model`.
- `simplify` -> `factor`, `winnow`, `quotient`, `ablate`, `prune`, `deforest`, `normalize`, or `reduce surface` when that is the real operation.
- `delete code` -> `ablate`, `decommission`, `collapse`, `privatize`, `canonicalize`, or `remove a vestigial surface` depending on proof and contract.
- `same behavior` -> `isomorphic`, `bisimulative`, `observationally equivalent`, or `refinement-preserving` only after naming the intended relation.
- `general solution` -> `principal solution` when special cases should be instantiations of one most-general construction.
- `keep improving` -> `contract toward the fixed point`, `saturate until the model stops changing`, or `run as an anytime procedure` depending on the stop and interruption contract.
- `make consistent` -> `make confluent`, `serializable`, `linearizable`, `causally consistent`, or `eventually convergent` only after naming the surface and guarantee.
- `make retries safe` -> `make the operation idempotent and deduplicating`.
- `recover automatically` -> `make the workflow self-stabilizing` only when convergence from reachable dirty states is actually required.
- `carry evidence` -> `make the handoff proof-carrying` when the certificate must travel with the result.

## Verification and testing language

- `test without knowing the exact answer` -> `define an Oracle Map and metamorphic relations`.
- `compare two versions` -> `run differential verification` when disagreement should be treated as a finding.
- `find the smallest failing case` -> `shrink to a minimal counterexample`.
- `test broadly` -> `use property-based or coverage-guided generation` when input families or state regions matter.
- `make tests meaningful` -> `make the suite mutation-resistant` when defect sensitivity is the criterion.
- `explore all states` -> `model-check the bounded state space` when a finite model and properties exist.
- `reproduce it` -> `capture a replayable trace` when state and ordering must be restored.
- `test recovery` -> `inject faults and verify containment and convergence`.

## Concurrency and distributed language

- `atomic operation` -> `linearizable operation` only when real-time order is part of the claim; otherwise `atomic at the declared observation boundary`.
- `transactions are correct` -> `serializable`, `snapshot-isolated`, or another named isolation level after checking the actual history guarantee.
- `events stay in order` -> `causally consistent` when cause-before-effect is the intended relation.
- `replicas eventually agree` -> `eventually consistent with a named convergence condition and conflict policy`.
- `use a quorum` -> `quorum-aware` with explicit read/write overlap and failure thresholds.
- `one authoritative value` -> `consensus-backed` when distributed agreement is required.
- `handle partitions` -> `partition-aware` with availability, consistency, and degradation behavior named.
- `avoid duplicate effects` -> `deduplicate repeated delivery under an explicit key`.
- `control overload` -> `apply backpressure and bound queue growth`.
- `isolate failure` -> `fault-contain the subsystem`.

## Algorithms and optimization language

- `best solution` -> `optimal` only when objective, constraints, horizon, and proof/search bound are explicit; otherwise use `dominant`, `best-known`, or `principal`.
- `most general solution` -> `principal`.
- `good heuristic` -> `admissible`, `consistent`, or empirically effective depending on the actual guarantee.
- `search efficiently` -> `best-first`, `branch-and-bound`, `prune`, or `kernelize` depending on frontier, bounds, elimination, or preprocessing.
- `can stop anytime` -> `anytime` only when a valid incumbent exists at every interruption point.
- `complexity depends on one factor` -> `parameterized by <factor>`.
- `average cost is low` -> `amortized` when the sequence argument exists.
- `runtime depends on result size` -> `output-sensitive`.
- `works well online` -> `competitive` when compared against an offline optimum.
- `close enough` -> `approximation-aware` with a ratio or quality envelope.
- `uses randomness` -> `randomized with seedability and failure bounds`.
- `make reproducible` -> `derandomize` or expose the seed, depending on intent.

## Performance and dataflow language

- `update efficiently` -> `incrementalize from the invalidation graph`.
- `compute only what is needed` -> `make demand-driven`.
- `keep related work together` -> `make locality-aware`.
- `optimize memory behavior` -> `make cache-conscious`.
- `avoid copies` -> `make zero-copy with ownership and lifetime proof`.
- `handle large inputs` -> `stream under an explicit memory bound`.
- `reduce overhead` -> `batch while preserving ordering and failure semantics`.
- `combine passes` -> `fuse adjacent traversals and remove intermediate materialization`.
- `parallelize efficiently` -> `optimize both work and span`.
- `scale better` -> `improve asymptotic behavior and validate the crossover`.
- `limit resource use` -> `bound time, memory, retries, queues, fanout, or state explicitly`.

## Security and authority language

- `avoid accidental capture` -> `make the transformation hygienic`.
- `isolate dependencies` -> `make the process hermetic`.
- `limit permissions` -> `apply least authority`.
- `make authority explicit` -> `use capabilities`.
- `check every access` -> `apply complete mediation`.
- `separate risky code` -> `privilege-separate it`.
- `prevent information leaks` -> `establish noninterference` when the influence relation can be stated.
- `avoid timing leaks` -> `make the operation constant-time` only with timing/control-flow evidence.
- `consider side channels` -> `perform a side-channel audit`.
- `make low-level code safe` -> `establish a memory-safety boundary`.
- `reduce security exposure` -> `minimize attack surface`.
- `run untrusted code safely` -> `sandbox it with explicit resource and capability limits`.
- `track untrusted input` -> `perform taint-aware source-to-sink analysis`.

## Data and schema language

- `preserve all information` -> `prove the transformation lossless`.
- `keep constraints checkable` -> `preserve dependencies after decomposition`.
- `keep references valid` -> `preserve referential integrity`.
- `evolve the schema safely` -> `use a schema-evolution matrix`.
- `keep history` -> `append with explicit supersession`.
- `derive state from events` -> `event-source the state`.
- `show where data came from` -> `preserve lineage`.

## Precedent and policy language

- `learn from the past` -> `recover and adjudicate precedent` when prior cases should change the route.
- `use previous experience` -> `apply binding or persuasive precedent after checking distinguishing facts and supersession`.
- `set a precedent` -> `establish a nomothetic rule` when the decision should govern future cases.
- `precedent setter` -> `Nomothete` when the user explicitly asks for a persona; use `nomothetic` for the operating mode.
- `creates the rule` -> `constitutes the governing rule` when the decision changes structure rather than merely applying policy.

## Simulation and modeling language

- `simulate` -> `emulate`, `counterfactually project`, `model dynamically`, or `use a surrogate` depending on fidelity and purpose.
- `model what happens` -> `build a dynamical model with state, transitions, delays, and observations` when history or ordering matters.
- `what if` -> `counterfactual intervention` when changed and held-constant assumptions should be explicit.
- `realistic simulation` -> `fidelity-bounded emulation` when validated and unsupported regions must be named.
- `digital stand-in` -> `surrogate` when the model substitutes for an expensive, unavailable, or dangerous real system.

## Evaluation and judgment language

- `evaluate` -> `adjudicate`, `score`, `validate`, `compare`, or `rank` depending whether a disposition, metric, proof, alternative comparison, or ordering is required.
- `judge` -> `issue a criteria-backed ruling` when explicit standards and dispositions matter.
- `grader` / `judge persona` -> `Arbiter` when the user explicitly asks for a persona; use `adjudicative` for the operating mode.
- `what matters most` -> `identify the dispositive factor` when one fact, rule, or test determines the outcome.
- `be objective` -> `declare criteria, weight evidence and counterevidence, and calibrate confidence`.

## Doctrine / mode language

- `be rigorous` -> `reject unwitnessed claims and preserve named invariants`.
- `be careful` -> `label uncertainty, preserve obligations, and check the failure surface`.
- `think deeply` -> `derive the governing invariant and test the strongest countercase`.
- `dig deeper` -> `be excavatory: descend until another layer no longer changes the model, owner, route, or proof burden`.
- `ruminate harder` -> `be aporetic: preserve the genuine unresolved difficulty until the missing distinction, evidence, or decision condition is explicit`.
- `take action` -> `actuate the lever and prove the system moved`.
- `start over` -> `rebaseline to the current authoritative state and invalidate stale receipts`.
- `systems thinking` -> `map cybernetic feedback loops, control points, signals, delays, and second-order effects`.
- `extract knowledge` -> `build a forensic provenance map and triangulate contradictions`.
- `learn from prior work` -> `build a Precedent Ledger and apply only current, non-superseded precedent with an action delta`.
- `make a simulator` -> `build a fidelity-bounded emulation with an Observation Contract`.
- `grade it` -> `adjudicate it against declared criteria and issue a disposition`.
- `make the routes agree` -> `make the system confluent and resolve critical pairs`.
- `make every pass count` -> `make the loop contractive under a named distance metric`.
- `avoid special cases` -> `seek a principal, parametric solution`.
- `reason beyond examples` -> `use symbolic or abstract interpretation with an explicit soundness boundary`.
- `use better words` -> `choose doctrine words that change procedure, not tone`.

## Guardrails

Do not replace if:

- the sharper word overstates certainty;
- the original intentionally stays broad;
- the domain has a canonical term;
- the substitution changes agency or obligation;
- the phrase is code, an identifier, a flag, a path, a schema field, or machine-consumed syntax;
- the new word would activate a workflow or proof obligation the task does not support;
- the formal term would imply a guarantee that has not been checked;
- `excavatory` would reward depth theater rather than a changed explanatory model;
- `aporetic` would reward indefinite indecision rather than sharpening a real difficulty;
- a lighter adjacent term is more honest.
