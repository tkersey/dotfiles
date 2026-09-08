# Prove It Round Lenses

Load the assigned round only when constructing its worker assignment. The root
retains the topology, packet, and oracle authority rules in SKILL.md.

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
