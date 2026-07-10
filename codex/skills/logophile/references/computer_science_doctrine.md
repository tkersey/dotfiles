# Computer Science Doctrine

Use this reference when a computer-science term can function as an agent doctrine operator.

The goal is not technical-sounding prose. Each word must induce a distinct procedure, constraint, proof obligation, search posture, or stopping rule.

For every candidate, identify:

```text
trigger -> operator -> artifact -> proof burden -> lighter fallback
```

Do not claim a formal guarantee merely because the word is evocative.

## Rewrite systems and convergence

| Word | Activated behavior | Cash-out | Critical distinction |
|---|---|---|---|
| `confluent` | permit multiple paths but require them to join at one canonical result | Confluence Matrix | unlike `deterministic`, many paths may be valid |
| `terminating` | require rewrites, retries, recursion, or loops to stop | ranking function / termination measure | stopping does not prove the right fixed point |
| `critical-pair-aware` | inspect overlapping rules whose independent application may diverge | Critical-Pair Ledger | local rule validity does not imply global confluence |
| `contractive` | require every pass to shrink a named distance to closure | Contraction Measure | stronger than generic progress |
| `monotone` | preserve an explicit information, authority, or state order | Information-Order Map | formal order law, not merely “improving” |
| `inflationary` | preserve prior state while moving upward in the order | inflationary transition proof | can over-accumulate when supersession is required |
| `congruence-preserving` | preserve equivalence under every permitted context | congruence checks | quotienting is unsafe without congruence |
| `conservative-extending` | add expressive power without changing existing valid meaning | conservative-extension certificate | extension is not ordinary backward compatibility |
| `commutative` | make independent operation order irrelevant | commutativity matrix | does not imply idempotence |
| `associative` | make grouping irrelevant | law tests | enables batching/folding, not arbitrary reordering |
| `distributive` | expose lawful interaction between two operations | distributive-law tests | useful for decomposition and incrementalization |

## Semantics, abstraction, and equivalence

| Word | Activated behavior | Cash-out | Critical distinction |
|---|---|---|---|
| `principal` | find the most general solution satisfying the constraints | Principal Solution + Instantiation Map | unlike `optimal`, no objective function is required |
| `parametric` | behave uniformly across admissible representations | Parametricity Matrix | rejects hidden type cases and example overfitting |
| `extensional` | judge equality by declared observations | Observation Contract | ignores internal construction unless observable |
| `representation-independent` | prevent clients from depending on hidden representation | client-observation audit | module boundary guarantee |
| `bisimulative` | match observable transitions in both directions | Bisimulation Relation | behavioral and stepwise, not structural isomorphism |
| `coinductive` | reason about ongoing/infinite behavior through observations | coinductive invariant | appropriate for streams, servers, protocols |
| `inductive` | build/prove from constructors and smaller cases | constructor coverage | appropriate for finite recursive construction |
| `lawful` | require an abstraction to satisfy its claimed laws | Law Suite | signatures alone are insufficient |
| `decidable` | provide a terminating judgment procedure for every valid input | Decision Procedure | totality does not itself imply termination |
| `complete` | include or derive every semantically valid case | completeness argument | pair with soundness |
| `effect-explicit` | expose effects in types, protocols, or interpreters | Effect Signature + Handler Map | rejects ambient hidden effects |
| `referentially-transparent` | permit substitution by value without behavior change | side-effect/capture audit | useful for caching and equational reasoning |

## Program analysis and refinement

| Word | Activated behavior | Cash-out | Critical distinction |
|---|---|---|---|
| `abstract-interpreting` | reason soundly over a tractable over-approximation | abstract domain + transfer functions | over-approximation trades precision for soundness |
| `symbolic` | reason over variables and path constraints | Path-Condition Ledger | not merely broad concrete testing |
| `counterexample-guided` | refine the model from failures instead of patching instances | Counterexample Refinement Ledger | canonical CEGAR posture |
| `refinement-driven` | add distinctions only when forced by observations/proof | refinement chain | fights speculative state growth |
| `proof-carrying` | make evidence travel with the result | Certificate-Bearing Handoff | stronger boundary rule than traceability |
| `type-directed` | let type and inhabitation obligations steer construction | type-obligation map | useful for synthesis and refactoring |
| `taint-aware` | track untrusted influence from sources to sinks | source-to-sink map | information-flow discipline |

## Verification and test-oracle design

| Word | Activated behavior | Cash-out | Critical distinction |
|---|---|---|---|
| `shrinking` | minimize a failing input, state, trace, or diff | Minimal Counterexample | removes noise while preserving failure |
| `metamorphic` | test invariant relations when no exact oracle exists | Metamorphic Relation Suite | relation-based, not guessed golden output |
| `differential` | compare independent implementations/versions | Differential Matrix | disagreement is evidence, not automatic blame |
| `property-based` | generate input families from invariants | generators + properties + shrinkers | broader than example tests |
| `oracle-aware` | name exact, partial, relational, statistical, or absent oracles | Oracle Map | prevents invented certainty |
| `coverage-guided` | steer generation toward unexplored regions | coverage frontier | coverage is guidance, not correctness |
| `mutation-resistant` | require tests to kill plausible injected defects | mutation score / surviving-mutant ledger | measures defect sensitivity |
| `model-checking` | explore bounded state space against properties | counterexample trace | requires explicit model and properties |
| `replayable` | capture enough state/order to reproduce behavior | Replay Receipt | different from merely traceable |
| `fault-injecting` | deliberately test containment and recovery | fault matrix | proves failure behavior, not happy path |

## Concurrency and distributed systems

| Word | Activated behavior | Cash-out | Critical distinction |
|---|---|---|---|
| `linearizable` | make operations appear atomic and respect real-time order | concurrent history + linearization points | stronger/different than transaction serializability |
| `serializable` | make concurrent transactions equivalent to some serial order | serialization graph | need not respect operation real-time order |
| `causally-consistent` | preserve cause-before-effect ordering | happens-before graph | unrelated events may remain unordered |
| `eventually-consistent` | permit temporary divergence under a real convergence contract | convergence/conflict contract | “eventual” without a condition is empty |
| `quorum-aware` | reason about read/write overlap and failure thresholds | quorum matrix | avoids hand-wavy replica claims |
| `consensus-backed` | require agreement protocol before claiming one authoritative order | consensus authority map | authority is not consensus |
| `self-stabilizing` | converge from reachable dirty/partial states to a valid state | Recovery Certificate | does not require perfect reset |
| `fault-contained` | bound failure propagation to explicit regions | containment map | isolation must be demonstrated |
| `partition-aware` | name availability/consistency behavior under communication loss | partition table | makes degraded modes explicit |
| `backpressure-aware` | make production respond to downstream capacity | demand/capacity contract | queues are not backpressure |
| `transactional` | bind multi-step mutation under an explicit consistency/rollback contract | transaction boundary | name the actual isolation/durability level |
| `atomic` | make an operation indivisible at the declared observation boundary | atomicity proof | scope of observation matters |
| `deduplicating` | make repeated delivery converge on one logical effect | dedupe key + retry proof | often paired with idempotence |

## Algorithms, search, and optimization

| Word | Activated behavior | Cash-out | Critical distinction |
|---|---|---|---|
| `anytime` | maintain a valid best-so-far answer at every interruption point | Incumbent + Remaining-Gap Receipt | unlike exhaustive search, useful before completion |
| `admissible` | use a heuristic that never overestimates remaining cost | admissibility argument | required for some optimal-search guarantees |
| `consistent-heuristic` | make heuristic estimates respect transition costs | consistency checks | prevents reopened states in A* |
| `branch-and-bound` | prune branches unable to beat the incumbent | bound/pruning ledger | needs a valid bound |
| `best-first` | expand the most promising frontier under an explicit score | frontier ordering | score must be named |
| `pruning` | remove branches proven unable to affect the answer | pruning rule + completeness impact | unsupported pruning can lose solutions |
| `kernelizing` | reduce a hard problem to a smaller equivalent instance | kernel + equivalence proof | parameterized preprocessing |
| `parameterized` | expose the structural parameter governing difficulty | parameter map | input size alone may mislead |
| `output-sensitive` | measure work relative to input plus output size | complexity bound | useful for enumeration/query tasks |
| `amortized` | distribute cost across an operation sequence | potential/accounting proof | not an average-case claim |
| `competitive` | compare online strategy with offline optimum | competitive ratio | online-algorithm notion |
| `worst-case-aware` | test catastrophic inputs or adversarial schedules | worst-case bound/test | complements average behavior |
| `approximation-aware` | state quality bounds when exact optimum is infeasible | approximation ratio/envelope | “good enough” must be bounded |
| `randomized` | state probability, seedability, and failure bounds | probabilistic guarantee | randomness is a contract |
| `derandomizing` | replace probabilistic choice with deterministic structure | substitute + comparison | useful for repeatability/proof |

## Performance and dataflow

| Word | Activated behavior | Cash-out |
|---|---|---|
| `incremental` | recompute only invalidated dependency closure | invalidation graph |
| `demand-driven` | compute/retrieve only what downstream observations require | demand map |
| `locality-aware` | place data/computation near reuse, ownership, or failure boundaries | locality map |
| `cache-conscious` | account for working-set and cache behavior | cache evidence |
| `zero-copy` | avoid materialization while preserving ownership/lifetimes | copy count + lifetime proof |
| `streaming` | process bounded chunks without full materialization | memory/chunk contract |
| `batching` | amortize fixed costs while preserving ordering/failure semantics | batch contract |
| `fusion-oriented` | combine adjacent passes and remove intermediates | fused pipeline |
| `work-efficient` | keep parallel work near best sequential work | work analysis |
| `span-efficient` | minimize the critical path | span analysis |
| `asymptotic` | reason about scaling, then validate constants/crossover | complexity model |
| `bounded` | enforce explicit resource limits | resource budget |

## Security, authority, and boundaries

| Word | Activated behavior | Cash-out | Critical distinction |
|---|---|---|---|
| `hygienic` | prevent unintended capture of names/context/authority/state | Capture Audit | unlike hermetic isolation, this governs transformation capture |
| `end-to-end` | place verification at the endpoint that can actually check it | endpoint map | intermediaries cannot guarantee everything |
| `least-authority` | give each component only required capabilities | capability matrix | sharper than generic least privilege |
| `capability-secure` | represent authority through explicit unforgeable capabilities | capability graph | rejects ambient authority |
| `complete-mediation` | check every access path | mediation coverage | entrypoint-only checks are incomplete |
| `privilege-separated` | split high-risk authority from ordinary computation | privilege map | limits compromise blast radius |
| `noninterfering` | prevent forbidden influence on protected observations | Information-Flow Matrix | stronger than simple isolation |
| `constant-time` | prevent secrets from affecting timing/control/resource behavior | timing audit | formal/empirical burden is high |
| `side-channel-aware` | account for leakage through timing, caches, logs, errors, resources | side-channel inventory | broader than constant time |
| `memory-safe` | prevent invalid memory access and ownership violations | unsafe-boundary audit | do not claim casually |
| `attack-surface-minimizing` | reduce exposed operations, parsers, privileges, protocols, dependencies | attack-surface delta | security-focused ablation |
| `sandboxed` | confine untrusted execution under explicit limits | sandbox policy + escape tests | policy is not proof of confinement |

## Data and schema evolution

| Word | Activated behavior | Cash-out |
|---|---|---|
| `lossless` | preserve information required by the live contract | round-trip/losslessness proof |
| `dependency-preserving` | keep constraints locally checkable after decomposition | dependency matrix |
| `referential-integrity-preserving` | maintain valid references across lifecycle changes | reference audit |
| `schema-evolution-aware` | make versions/defaults/unknown fields/migrations explicit | evolution matrix |
| `append-only` | express history through additions and supersession | append contract |
| `event-sourced` | treat events as authority and state as replayable projection | event schema + reducer + replay |
| `lineage-preserving` | retain derivation from source to result | lineage graph |

## High-value distinctions

```text
deterministic        = one prescribed path
confluent            = many paths, one joinable result

fixed-point          = stable endpoint
contractive          = each pass shrinks distance to it
terminating          = the process cannot continue forever

optimal              = best under an objective
principal            = most general under constraints
admissible           = heuristic does not overestimate
anytime              = valid incumbent at every interruption point

isomorphic           = invertible structural correspondence
bisimulative         = mutually matching observable transitions
extensional          = equal by selected observations
refinement-preserving = required behavior remains while obsolete/invalid behavior may disappear

total                = defined for every valid input
decidable            = terminates with a judgment for every valid input
sound                = no invalid conclusions
complete             = every valid conclusion is reachable

traceable            = evidence can be followed
proof-carrying       = evidence travels with the result
replayable           = captured state reproduces behavior

hermetic             = isolated from ambient dependencies
hygienic             = protected from unintended capture
noninterfering       = forbidden influence cannot affect observations

serializable         = transactions equal some serial order
linearizable         = operations also respect real-time order
causally-consistent  = cause precedes effect; unrelated events may remain unordered
```

## High-leverage doctrine stacks

### Review and remediation

```text
COUNTEREXAMPLE-GUIDED + SHRINKING + CONTRACTIVE + PROOF-CARRYING
```

### Rewrite and canonicalization

```text
CONFLUENT + TERMINATING + CRITICAL-PAIR-AWARE + NORMALIZING
```

### Architecture and API design

```text
PRINCIPAL + PARAMETRIC + HYGIENIC + CONSERVATIVE-EXTENDING
```

### State machines and protocols

```text
BISIMULATIVE + COINDUCTIVE + TOTALIZING + PROGRESS-AWARE
```

### Verification without a direct oracle

```text
ORACLE-AWARE + METAMORPHIC + DIFFERENTIAL + SHRINKING
```

### Durable agent workflows

```text
MONOTONE + CONTRACTIVE + ANYTIME + SELF-STABILIZING
```

### Distributed correctness

```text
CAUSALLY-CONSISTENT + PARTITION-AWARE + QUORUM-AWARE + DEDUPLICATING
```

### Security boundaries

```text
LEAST-AUTHORITY + CAPABILITY-SECURE + COMPLETE-MEDIATION + NONINTERFERING
```

## Selection discipline

More vocabulary is useful only while the distinctions remain sharp.

- Prefer the exact technical term when the task carries its proof obligation.
- Do not use a concurrency guarantee as a metaphor for ordinary coordination.
- Do not claim `optimal`, `complete`, `linearizable`, `constant-time`, or `proof-carrying` without proportionate evidence.
- Use a lighter adjacent term when the full formal claim cannot be supported.
- In runtime prompts, select the smallest non-overlapping stack; the catalog is for discovery, not simultaneous invocation.
