# Doctrine Probe Cases

## Should trigger doctrine mode

```text
Find doctrine words for reviewing PR comments more discriminately.
```

Expected:
- `rebuttal-first`
- `discriminative`
- `criterial`
- `invariant-seeking`
- `ablative`
- artifacts: Resolve Selection, no-change countercase, Criteria Matrix, Ablation Activation Receipt.

```text
What doctrine word captures moving from plan to PR?
```

Expected:
- `actuating`
- artifact: Actuation Receipt.

```text
What is the doctrine word for decomposing and removing what is unnecessary?
```

Expected:
- `winnowing`
- companions: `factorizing`, `quotienting`, `ablative`, `normalizing`, `refinement-preserving`.
- artifact: Winnowing Ledger or Reduction Certificate with recomposition proof.

```text
What doctrine word captures reset?
```

Expected:
- `rebaselining`
- artifact: Baseline Receipt.

```text
Find words like unsound for type-theoretic review.
```

Expected:
- `unwitnessed`, `illegal inhabitant`, `partial`, `totalizing`, `preservation-aware`, `progress-aware`.

```text
What doctrine word means learning from past cases without blindly obeying memory?
```

Expected:
- `precedential`
- companions: `provenance-preserving`, `distinguishing`, `supersession-aware`.
- artifact: Precedent Ledger with action delta.

```text
Give me a doctrine persona for someone who deliberately sets precedent.
```

Expected:
- mode: `nomothetic`
- persona: `Nomothete`
- near miss: `constitutive` names the act more naturally than the persona.
- artifact: Nomothetic Receipt.

```text
What doctrine words should guide a simulator?
```

Expected:
- `emulative`
- companions: `counterfactual`, `dynamical`, `observational`, `fidelity-bounded`.
- artifacts: Emulation Receipt and Fidelity Boundary.

```text
What doctrine word fits an evaluator, grader, or judge?
```

Expected:
- mode: `adjudicative`
- persona when requested: `Arbiter`
- companions: `criterial`, `evidence-weighted`, `calibrated`, `dispositive`.
- artifact: Adjudication Ledger.

```text
What doctrine word means account for every state transition and residual?
```

Expected:
- `reconciling`
- companion: `conservation-aware`.
- artifact: Reconciliation Ledger or Conservation Ledger.

## Computer-science doctrine probes

```text
I have several valid rewrite paths. I need them all to converge to one canonical result.
```

Expected:
- `confluent`
- companions: `critical-pair-aware`, `normalizing`, `terminating`.
- artifact: Confluence Matrix or Critical-Pair Ledger.
- near miss: `deterministic` is wrong if several paths are intentionally valid.

```text
My fixed-point loop keeps running but I cannot tell whether each pass gets closer.
```

Expected:
- `contractive`
- companions: `fixed-point`, `terminating`, `saturating`.
- artifact: Contraction Measure.
- distinction: `fixed-point` names the endpoint; `contractive` names progress toward it.

```text
I want the most general solution that satisfies these constraints, not another pile of special cases.
```

Expected:
- `principal`
- companions: `parametric`, `constructive`, `conservative-extending`.
- artifact: Principal Solution + Instantiation Map.
- near miss: `optimal` requires an objective and is not synonymous with principal.

```text
I need to prove these two state machines have the same behavior, including every transition.
```

Expected:
- `bisimulative`
- companions: `coinductive`, `observational`, `totalizing`.
- artifact: Bisimulation Relation.
- near miss: `isomorphic` is not the default behavioral relation.

```text
Every new failing example causes another local patch. I want the failures to refine the model instead.
```

Expected:
- `counterexample-guided`
- companions: `refinement-driven`, `shrinking`, `invariant-seeking`.
- artifact: Counterexample Refinement Ledger.

```text
There is no exact expected output. How should the agent design verification?
```

Expected:
- `oracle-aware`
- companions: `metamorphic`, `differential`, `property-based`.
- artifacts: Oracle Map and Metamorphic Relation Suite.
- do not invent a golden output.

```text
I want the smallest input or trace that still reproduces the bug.
```

Expected:
- `shrinking`
- artifact: Minimal Counterexample.

```text
I want tests that prove they would catch plausible defects, not merely execute the lines.
```

Expected:
- `mutation-resistant`
- companion: `coverage-guided`.
- artifact: mutation score and surviving-mutant ledger.

```text
The implementation should remain uniform across all admissible types and not special-case known examples.
```

Expected:
- `parametric`
- artifact: Parametricity Matrix.

```text
A result crosses from one subagent to another. The evidence needed to trust it must travel with it.
```

Expected:
- `proof-carrying`
- companion: `traceable`.
- artifact: Certificate-Bearing Handoff.
- distinction: traceability alone does not require the proof to travel with the result.

```text
A source transformation must not capture ambient names, authority, or context.
```

Expected:
- `hygienic`
- artifact: Capture Audit.
- near miss: `hermetic` is about ambient dependencies, not capture.

```text
This operation may run several times because delivery is at least once, but it must have one logical effect.
```

Expected:
- `idempotent`
- companion: `deduplicating`.
- artifact: repeat-delivery proof and deduplication key.

```text
I need concurrent operations on one object to appear atomic and respect real-time order.
```

Expected:
- `linearizable`
- artifact: concurrent history and linearization points.
- near miss: `serializable` is weaker/different and applies to transaction equivalence.

```text
I need concurrent database transactions to equal some serial execution, but real-time operation order is not the claim.
```

Expected:
- `serializable`
- artifact: serialization graph.

```text
Replicas may diverge temporarily, but I need a real convergence and conflict-resolution contract.
```

Expected:
- `eventually-consistent`
- companions: `partition-aware`, `quorum-aware`, `deduplicating`.
- artifact: Distributed Consistency Contract.
- reject vague “eventual” claims without a convergence condition.

```text
The workflow may resume from partial or dirty state and should converge back to a valid state.
```

Expected:
- `self-stabilizing`
- companions: `rebaselining`, `idempotent`, `replayable`.
- artifact: Recovery Certificate.

```text
The search may be interrupted at any time, but I still need a valid best-so-far answer.
```

Expected:
- `anytime`
- artifact: Anytime Incumbent Receipt.
- near miss: `exhaustive` does not guarantee useful intermediate answers.

```text
I want to prune design branches whose best possible outcome cannot beat the current candidate.
```

Expected:
- `branch-and-bound`
- companions: `pruning`, `best-first`, `admissible`.
- artifact: incumbent, bound, and pruned-branch ledger.

```text
This expensive operation is occasionally slow, but I care about the cost across a long sequence.
```

Expected:
- `amortized`
- artifact: potential or accounting argument.

```text
Only a small structural parameter makes the problem difficult; total input size is misleading.
```

Expected:
- `parameterized`
- companion: `kernelizing`.
- artifact: parameter map and reduced kernel instance.

```text
The system should recompute only what the changed dependency invalidates.
```

Expected:
- `incremental`
- artifact: invalidation graph.

```text
The system should produce only what downstream observations demand.
```

Expected:
- `demand-driven`
- artifact: demand/observation map.

```text
I need to minimize the critical path of a parallel workflow, not just total work.
```

Expected:
- `span-efficient`
- companion: `work-efficient`.
- artifact: work/span analysis.

```text
Each plugin should receive only the authority it needs, represented explicitly rather than ambiently.
```

Expected:
- `least-authority`
- companion: `capability-secure`.
- artifact: capability graph.

```text
Protected state must not influence these outputs, even indirectly.
```

Expected:
- `noninterfering`
- artifact: Information-Flow Matrix.

```text
The cryptographic routine must not leak secret-dependent timing.
```

Expected:
- `constant-time`
- companion: `side-channel-aware`.
- artifact: timing/branch audit.

```text
A schema decomposition must preserve all information and allow constraints to be checked locally.
```

Expected:
- `lossless`
- companion: `dependency-preserving`.
- artifacts: losslessness proof and dependency-preservation matrix.

```text
Events should be the authority and current state should be replayable from them.
```

Expected:
- `event-sourced`
- companions: `append-only`, `replayable`, `lineage-preserving`.
- artifact: event schema, reducer, and replay proof.

## Formal-distinction probes

```text
Should I call this deterministic or confluent?
```

Expected:
- ask whether multiple valid paths exist.
- choose `deterministic` when one next path/output is prescribed.
- choose `confluent` when multiple paths may exist but must join.

```text
Is this isomorphic, bisimilar, or observationally equivalent?
```

Expected:
- `isomorphic`: invertible structural mapping.
- `bisimulative`: mutually matching transitions.
- `observationally-equivalent`: equal under declared observations.
- do not use them interchangeably.

```text
Should I say complete, total, decidable, or sound?
```

Expected:
- `sound`: no invalid conclusions.
- `complete`: every valid conclusion is reachable.
- `total`: defined for every valid input.
- `decidable`: terminates with a judgment for every valid input.

```text
Is principal the same thing as optimal?
```

Expected:
- no.
- `principal`: most general under constraints.
- `optimal`: best under an objective.

```text
Is proof-carrying just a stronger way to say traceable?
```

Expected:
- no.
- `traceable`: evidence can be followed.
- `proof-carrying`: evidence travels with the result.

## Should trigger activation-phrase mode

```text
Give me the shortest phrases that make the model search more ambitiously and then select the best move.
```

Expected runtime output:

```text
Be bolder.
Be Optimal.
```

Do not automatically append a rubric, receipt, or explanation.

```text
Give me an exemplar phrase for elite fundamentals, competitive intensity, and finishing under pressure.
```

Expected runtime output:

```text
Be like Mike.
```

Repo convention: unqualified `Mike` means Michael Jordan unless local context clearly identifies another Mike. Do not append the trait explanation unless requested.

```text
Give me one compact phrase to de-anchor the next review pass.
```

Expected runtime output:

```text
Use fresh eyes.
```

```text
Give me one phrase that raises the ambition floor.
```

Expected runtime output:

```text
Perform no smallness.
```

## Should not trigger doctrine mode

```text
Fix the failing test.
```

Unless the user asks for wording or doctrine, this is implementation, not logophile.

```text
Review this patch for regressions.
```

This belongs to review workflows, not logophile, unless the user asks for wording or names.

```text
Run the tests and ship the PR.
```

This belongs to execution/shipping workflows.

```text
Simulate this protocol and tell me what happens.
```

This is an operational simulation request, not a doctrine-word request.

```text
Grade these submissions against the rubric.
```

This is an evaluation workflow, not a doctrine naming request.

```text
Prove this history is linearizable.
```

This is an operational concurrency-verification task, not a terminology request.

```text
Run symbolic execution over this binary.
```

This is operational program analysis, not doctrine synthesis.

## Quality checks

A doctrine-word answer must:
- name the pressure;
- choose words with distinct jobs;
- preserve formal computer-science distinctions;
- separate mode, persona, command, and artifact when relevant;
- explain near misses when useful;
- include artifacts when correctness, handoff, or closure depends on them;
- state a lighter fallback when the strongest formal term cannot be proven;
- end with `Use This:` and `Operationalization:` in full doctrine mode.

An activation-phrase answer must:
- maximize behavioral leverage per token;
- preserve the shortest effective form;
- avoid redundant explanation unless requested;
- distinguish overlapping phrases;
- keep shadow-risk analysis in the reference or annotated mode.

Reject answers that:
- list fancy synonyms;
- include generic praise words;
- fail to say what a doctrine word should make the receiving agent do differently;
- confuse a persona noun with an operating mode;
- use a proof relation such as `isomorphic` as though it were a reduction operator;
- use `deterministic` when the actual guarantee is confluence;
- use `optimal` when only a principal or admissible solution is supported;
- use `linearizable` when only transaction serializability was checked;
- use `complete`, `constant-time`, `proof-carrying`, or `self-stabilizing` without the matching proof burden;
- turn activation phrases into a long runtime checklist by default;
- require a receipt merely to prove that an activation phrase was used.
