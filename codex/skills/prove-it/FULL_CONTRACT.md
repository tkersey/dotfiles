---
name: prove-it
description: "Run an artifactless parallel subagent gauntlet for absolute or suspiciously clean claims. Rounds 1-9 are independent lens packets produced concurrently by the reusable prove_it_lens custom agent; round 10 is the prove_it_oracle custom agent that runs only after all nine packets return and owns the final verdict plus final response text."
metadata:
  version: "3.2.0"
  activation_cost: high
  default_depth: high
---

# Prove It

## Purpose

Use this skill to stress-test absolute, sweeping, overconfident, or suspiciously clean claims.

Typical activation cues:

- certainty language: "always", "never", "guaranteed", "optimal", "cannot fail", "no downside", "100%";
- explicit requests: "prove it", "disprove it", "devil's advocate", "stress test", "rigor", "find counterexamples";
- claims whose truth depends on hidden quantifiers, edge cases, operating conditions, baselines, adversaries, comparative standards, or unstated definitions.

## Core contract

A valid prove-it run is an **artifactless parallel subagent gauntlet**.

```text
root coordinator
-> normalize claim and scope
-> dispatch rounds 1-9 as independent prove_it_lens assignments at the same time
-> collect nine round packets
-> dispatch round 10 prove_it_oracle with all nine packets
-> validate the oracle packet and relay its final_response
```

Non-negotiable rules:

1. Rounds 1-9 are subagent work, not root-thread analysis sections.
2. Rounds 1-9 are dispatched together before synthesis begins.
3. Rounds 1-9 all use the reusable `prove_it_lens` custom agent with different lens instructions.
4. Round 10 uses the `prove_it_oracle` custom agent and runs only after all nine round packets are available.
5. The root coordinator does not issue a final verdict before the oracle packet and `final_response` return.
6. Do not create nine bespoke subagent personalities; the round lens, not the subagent name, carries the direction.
7. `prove_it_oracle` is the only authority allowed to choose the terminal outcome and write final response text.
8. The root coordinator validates completeness, verdict enum, and `final_response`; it relays the oracle response or reports the oracle packet as compromised.
9. No progress files, templates, run directories, manifests, prompt dumps, transcripts, or other prove-it artifacts are created.
10. The conversation response is the only output surface.

If the runtime cannot spawn subagents, do not fake the gauntlet in the root thread. Stop with:

```text
PROVE_IT_REQUIRES_SUBAGENTS
```

Then explain that this skill requires concurrent `prove_it_lens` execution for rounds 1-9 and a `prove_it_oracle` after fan-in.

If custom agents are unavailable but ordinary subagents can be spawned, run the same packet contract through ordinary spawned subagents and surface a custom-agent fallback warning in the final response. Fallback changes the transport only; `packet_role`, oracle authority, and root relay rules remain unchanged.

## Artifactless state model

State lives only in memory during the current assistant turn:

```text
root coordinator context
+ nine prove_it_lens round packets
+ one prove_it_oracle packet
```

Do not create or update:

```text
.prove-it-progress.md
.prove-it-progress.template.md
.prove-it-runs/
manifest.json
prompt/output transcript files
any other prove-it state artifact
```

## Custom agent topology

Use exactly two custom authority agents.

### `prove_it_lens`

Used for every round from 1 through 9.

A `prove_it_lens` receives:

```yaml
packet_role: evidence_lens
round: 1|2|3|4|5|6|7|8|9
lens_id:
lens:
lens_mode:
original_claim:
normalized_claim:
claim_scope:
assignment:
```

Posture:

```text
Apply the assigned lens sharply and independently. Produce one evidence packet. Do not synthesize across other rounds and do not declare the final verdict.
```

A `prove_it_lens` may find attack, support, uncertainty, or narrowing. It is not inherently hostile or defensive. Its direction comes from the lens assignment. It must not synthesize across rounds or declare the final verdict.

Useful modes:

```text
falsify       find a concrete break or counterexample
bound         locate scope boundaries and edge conditions
support       identify the strongest surviving form or proof-like support
compare       test against alternatives, baselines, and metrics
test_design   propose the fastest discriminating proof or experiment
```

### `prove_it_oracle`

Used only for round 10 after all nine lens packets return.

A `prove_it_oracle` receives:

```yaml
packet_role: oracle_synthesis
round: 10
lens: Oracle synthesis
original_claim:
normalized_claim:
claim_scope:
round_packets: []
```

Posture:

```text
Adjudicate the complete packet set. Decide the final verdict, tightest surviving claim, boundaries, confidence, and next tests without rerunning the whole gauntlet.
```

The `prove_it_oracle` is the only component allowed to choose the terminal outcome. It also writes `final_response`, the final user-facing prove-it response that the root coordinator should relay after validation.

## Dispatch law

For every invocation:

1. Root normalizes the claim once.
2. Root creates nine lens assignments for rounds 1-9.
3. Root dispatches all nine assignments to `prove_it_lens` subagents concurrently, or requests them together so the host scheduler may run them in parallel.
4. Runtime task names must carry round purpose, for example `prove_it_01_counterexamples`, `prove_it_02_logic_traps`, `prove_it_03_boundary_cases`, `prove_it_04_adversarial_inputs`, `prove_it_05_alternative_paradigms`, `prove_it_06_operational_constraints`, `prove_it_07_probabilistic_uncertainty`, `prove_it_08_comparative_baselines`, and `prove_it_09_meta_test`.
5. Each `prove_it_lens` instance sees the original claim, normalized claim, scope, and its own lens only.
6. `prove_it_lens` instances do not see other round packets before producing their own packet.
7. `prove_it_lens` instances must not return a final verdict.
8. Root waits for all nine packets.
9. Missing, failed, or low-confidence packets are represented explicitly; the oracle still receives the failure information.
10. Root dispatches `prove_it_10_oracle_synthesis` to `prove_it_oracle` with the normalized claim and all nine packets.
11. `prove_it_oracle` synthesizes the final verdict and writes `final_response`.
12. Root validates packet completeness, `final_verdict.outcome`, and `final_response`.
13. Root relays `final_response` without adding an independent verdict. If validation fails, root reports the oracle packet as compromised instead of rewriting the verdict.

## Round packet schema

Each round 1-9 subagent returns exactly one packet in this shape:

```yaml
prove_it_round_packet:
  packet_role: evidence_lens
  round: 1|2|3|4|5|6|7|8|9
  lens_id:
  lens:
  lens_mode: falsify|bound|support|compare|test_design
  original_claim:
  normalized_claim:
  scope_assumptions: []
  pressure_question:
  strongest_attack:
  smallest_counterexample_or_boundary:
  strongest_support_found:
  effect_on_original_claim: survives|narrows|breaks|unclear
  effect_on_refined_claim: survives|narrows|breaks|unclear
  candidate_fatal_pressure: null|string
  candidate_decisive_support: null|string
  refined_claim_delta:
  uncertainty:
  oracle_notes:
```

`packet_role` must be `evidence_lens`. Do not replace packet authority with a subagent nickname, round name, or transport-specific label.

Round packets are evidence packets, not verdicts. Use `candidate_fatal_pressure` and `candidate_decisive_support` for severe findings, but keep verdict authority for the oracle.

## Oracle packet schema

Round 10 is a separate subagent after fan-in. It receives the normalized claim plus all nine round packets and returns:

```yaml
prove_it_oracle_packet:
  packet_role: oracle_synthesis
  round: 10
  lens: Oracle synthesis
  packet_completeness:
    received_rounds: []
    missing_rounds: []
    compromised_rounds: []
  final_verdict:
    outcome: PROVEN|DISPROVEN|NOT_PROVEN|INSUFFICIENT_EVIDENCE|BOUNDED_CLAIM_SURVIVES
    statement:
    decisive_reasons: []
  tightest_surviving_claim:
  valid_when: []
  invalid_when: []
  fatal_pressures_resolved: []
  decisive_support_resolved: []
  confidence:
    level: low|medium|high
    why:
    main_gaps: []
  next_tests: []
  final_response: |
    Prove It — Parallel Subagent Gauntlet
    ...
```

`packet_role` must be `oracle_synthesis`. `final_verdict.outcome` must be one exact enum value: `PROVEN`, `DISPROVEN`, `NOT_PROVEN`, `INSUFFICIENT_EVIDENCE`, or `BOUNDED_CLAIM_SURVIVES`. The oracle should cite round numbers in `decisive_reasons`, `fatal_pressures_resolved`, `decisive_support_resolved`, or `next_tests` so the final outcome is traceable to the nine packets.

The oracle is the only component that may choose `PROVEN`, `DISPROVEN`, `NOT_PROVEN`, `INSUFFICIENT_EVIDENCE`, or `BOUNDED_CLAIM_SURVIVES`.

## Enhanced lens definitions

### Round 1 — Counterexamples

Find the smallest concrete case that pressures the claim. Prefer crisp examples over broad skepticism.

Ask:

```text
What single case, input, population, object, environment, or scenario would make the original wording false or materially misleading?
```

Look for:

- universal quantifier breaks;
- existence counterexamples;
- ordinary real-world exceptions;
- minimal reproducible cases;
- cases where the claim is true only after adding hidden qualifiers.

Packet emphasis:

```text
lens_mode: falsify
smallest_counterexample_or_boundary
candidate_fatal_pressure
refined_claim_delta
```

### Round 2 — Logic traps

Interrogate the argument shape rather than the world. Identify whether the claim relies on a hidden definition, invalid inference, equivocation, circularity, or category mistake.

Ask:

```text
What must be smuggled into the premises for the claim to sound proven?
```

Look for:

- missing quantifiers or domain restrictions;
- moving from some to all, average to individual, correlation to causation, or possibility to necessity;
- circular definitions;
- overloaded terms;
- category errors;
- claims that cannot be evaluated because key predicates are undefined.

Packet emphasis:

```text
lens_mode: bound
scope_assumptions
strongest_attack
uncertainty
oracle_notes
```

### Round 3 — Boundary cases

Probe edges where normal intuitions fail. Boundary cases are not random weirdness; they test whether the claim has a stable domain.

Ask:

```text
What happens at zero, one, infinity, empty input, maximum scale, degenerate form, pathological data, or extreme resource limits?
```

Look for:

- empty sets and missing inputs;
- one-item cases;
- maximum-size or high-scale cases;
- degenerate objects;
- numerical precision, ordering, timeout, or lifecycle edges;
- cases where the intended invariant changes at the boundary.

Packet emphasis:

```text
lens_mode: bound
smallest_counterexample_or_boundary
effect_on_refined_claim
refined_claim_delta
```

### Round 4 — Adversarial inputs

Assume a strategic actor wants the claim to fail or become costly. The adversary may be a user, market participant, attacker, institution, optimizer, or unlucky data generator.

Ask:

```text
How would someone with incentives, information, or control over inputs make the claim fail while staying within the stated rules?
```

Look for:

- manipulation and gaming;
- malicious or abusive inputs;
- prompt, policy, or interface exploitation;
- Goodharting;
- incentive mismatch;
- worst-case distributions;
- cases where defense costs exceed claimed benefits.

Packet emphasis:

```text
lens_mode: falsify
strongest_attack
candidate_fatal_pressure
oracle_notes
```

### Round 5 — Alternative paradigms

Switch the objective function, worldview, model, or value system. Some claims survive only because the original frame hides what is being optimized.

Ask:

```text
Under which reasonable alternative frame does the conclusion become false, irrelevant, or dominated by another goal?
```

Look for:

- different success metrics;
- different stakeholders;
- safety vs speed, cost vs quality, autonomy vs control, precision vs recall;
- formal vs pragmatic truth;
- local vs global optimum;
- deontological, consequentialist, legal, operational, or user-experience reframings.

Packet emphasis:

```text
lens_mode: compare
scope_assumptions
strongest_support_found
effect_on_original_claim
refined_claim_delta
```

### Round 6 — Operational constraints

Test implementation reality. A claim may be logically possible and still fail under latency, cost, integration, policy, staffing, compliance, maintenance, or deployment constraints.

Ask:

```text
What real operating constraint makes this claim unusable, unscalable, unsafe, noncompliant, or too expensive?
```

Look for:

- latency and throughput limits;
- cost ceilings;
- dependency reliability;
- migration and rollback constraints;
- compliance or policy hard stops;
- maintenance burden;
- observability gaps;
- organizational ownership failures.

Packet emphasis:

```text
lens_mode: bound
candidate_fatal_pressure
uncertainty
oracle_notes
```

### Round 7 — Probabilistic uncertainty

Replace point estimates with distributions. The question is not only whether the claim can be true, but how fragile it is under variance, base rates, sampling error, and distribution shift.

Ask:

```text
What base-rate, variance, tail-risk, sampling, or distribution-shift fact would make confidence in the claim unjustified?
```

Look for:

- small sample overreach;
- survivorship bias;
- heavy tails;
- rare but catastrophic cases;
- Simpson's paradox;
- regression to the mean;
- nonstationarity;
- confidence intervals that cross the decision boundary.

Packet emphasis:

```text
lens_mode: bound
uncertainty
effect_on_original_claim
next evidence needed in oracle_notes
```

### Round 8 — Comparative baselines

Force the claim to name its counterfactual. Many claims are only impressive until compared with the right baseline.

Ask:

```text
Better, safer, cheaper, faster, truer, or more robust than what, on which metric, under which trade-off?
```

Look for:

- straw baselines;
- missing counterfactuals;
- metric cherry-picking;
- dominated alternatives;
- trade-offs hidden by a single success metric;
- local improvements that worsen system-level outcomes.

Packet emphasis:

```text
lens_mode: compare
strongest_attack
strongest_support_found
refined_claim_delta
```

### Round 9 — Meta-test

Design the fastest information-gathering move that would change the verdict. This round does not merely criticize; it identifies the cleanest path to resolution.

Ask:

```text
What observation, experiment, proof obligation, benchmark, adversarial test, or data collection would most efficiently decide the claim?
```

Look for:

- decisive experiments;
- falsification tests;
- minimal proof obligations;
- benchmarks with real baselines;
- adversarial trials;
- field data;
- cheap probes that dominate further debate.

Packet emphasis:

```text
lens_mode: test_design
oracle_notes
uncertainty
refined_claim_delta
```

### Round 10 — Oracle synthesis

The oracle receives all nine packets. It does not rerun all analysis; it adjudicates the packet set.

Ask:

```text
After all independent lens packets, what verdict is justified, what is the tightest surviving claim, and what would change the answer fastest?
```

The oracle must:

- resolve candidate fatal pressures;
- resolve candidate decisive support;
- distinguish original claim from refined claim;
- avoid overclaiming beyond packet evidence;
- produce one final outcome;
- name validity boundaries and next tests.

## Root final response

After the oracle packet returns, the root validates `prove_it_oracle_packet` and relays `final_response`. The root must not rewrite the outcome, invent a tighter claim, or add a separate verdict. If validation fails, report the oracle packet as compromised and do not synthesize a replacement verdict.

The oracle's `final_response` must use this shape:

```text
Prove It — Parallel Subagent Gauntlet

Original claim:
Normalized claim:
Execution mode: custom-agent|custom-agent fallback
Packets received: <oracle.packet_completeness.received_rounds>
Missing packets: <oracle.packet_completeness.missing_rounds>
Compromised packets: <oracle.packet_completeness.compromised_rounds>
Oracle completeness: complete|incomplete

Verdict:
- Outcome:
- Statement:
- Decisive reasons:

Tightest surviving claim:

Round pressure map:
| Round | Lens | Effect | Key pressure/support |
|---|---|---|---|

Valid when:
- ...

Invalid when:
- ...

Confidence:
- Level:
- Why:
- Gaps:

Next tests:
- ...
```

If ordinary spawned subagents were used because custom agents were unavailable, include a custom-agent fallback warning immediately after `Execution mode`.

Do not print all raw subagent packets unless the user asks for them. Summarize them in the pressure map.

Do not claim all nine packets arrived unless `received_rounds` contains 1-9 and both `missing_rounds` and `compromised_rounds` are empty. If any packet is missing, failed, timed out, or compromised, surface that incompleteness in the final response and let the oracle choose the corresponding outcome.

## Stop rules

Stop without running the gauntlet when:

- no claim is present;
- subagents are unavailable;
- the user asks only how the skill works;
- the request is about editing the skill rather than stress-testing a claim.

Do not stop merely because a worker finds an apparently decisive proof, disproof, or counterexample. That is packet evidence for the oracle.

## Regression guards

### Direct launch request

Input request: `Use prove-it on this claim: all swans are white.`

Expected behavior:

- root normalizes the claim;
- if subagents are available, root dispatches rounds 1-9 as parallel `prove_it_lens` assignments;
- if subagents are unavailable, stop with `PROVE_IT_REQUIRES_SUBAGENTS` instead of faking a root-only gauntlet;
- round 1 likely identifies black swans as candidate fatal pressure;
- root does not issue a final verdict before oracle;
- oracle decides the final verdict after all packets.

### Step, pause, or compression request

Inputs:

- `Run round 1 and wait for me.`
- `Do all ten rounds in one response.`

Expected behavior:

- do not run a manual sequential round;
- do not compress root-authored pseudo-rounds;
- use the parallel subagent gauntlet or stop with `PROVE_IT_REQUIRES_SUBAGENTS`.

### Artifactless run

Expected behavior:

- no `.prove-it-progress.md`;
- no `.prove-it-progress.template.md`;
- no `.prove-it-runs/`;
- no prompt/output transcript files;
- no manifest;
- final output only in conversation.

### Valid-looking early proof still reaches oracle

Input claim: `For every integer n, n + 0 = n.`

Expected behavior:

- support-oriented packets may record candidate decisive support;
- pressure packets still run;
- oracle decides whether the proof survives all lenses.
