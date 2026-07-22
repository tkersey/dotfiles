# Behavioral Upgrade Probe Cases

Use these probes to verify that `$logophile` treats an existing phrase as an incumbent and distinguishes semantic precision from behavioral superiority.

## Should trigger Behavioral Upgrade mode

### Refinement that may replace

```text
Would `Be excavatory.` perform better than `Dig deeper.` for root-cause work?
```

Expected:

- baseline role: `DEEPEN`;
- candidate role: `DEEPEN`;
- relation: `refinement` plus `register-shift`;
- name improved stopping semantics;
- name lower familiarity / higher decoding cost;
- verdict: `replace` only for a root-cause-heavy task distribution, otherwise `benchmark`;
- do not claim proof from semantics alone.

### Specialization must not silently replace the default

```text
Replace `Ruminate harder.` with `Be aporetic.` everywhere.
```

Expected:

- baseline role: `DELIBERATE`;
- candidate role: `HOLD-OPEN`;
- relation: `specialization` plus role shift;
- verdict: `specialize`, not universal `replace`;
- broad default may remain `Ruminate harder.`;
- specialist trigger: genuine contradiction or underdetermination.

### Formal doctrine may not be the best runtime phrase

```text
Is `AUDACIOUS` a better activation phrase than `Be bolder.`?
```

Expected:

- formal doctrine: `AUDACIOUS`;
- runtime incumbent: `Be bolder.`;
- relation: near-equivalent plus register shift;
- compare immediacy, familiarity, cadence, and task coverage;
- verdict: `benchmark` or retain plain runtime wording;
- do not prefer the rarer word merely because it is denser.

### Creative versus poietic

```text
Should `MORE CREATIVE!` become `OPERATE POIETICALLY!`?
```

Expected:

- baseline role: broad `CREATE / DIVERGE`;
- candidate role: `CREATE NEW FORM`;
- relation: specialization plus register shift;
- candidate may have higher ceiling for architecture and invention;
- baseline may have higher median and broader coverage;
- verdict: `specialize` or `benchmark`.

### Retain is a successful result

```text
Upgrade `Use fresh eyes.` with a more sophisticated doctrine word.
```

Expected:

- model the incumbent's low decoding cost, broad de-anchoring effect, cadence, and memorability;
- generate candidates, but allow `retain`;
- reject change when no candidate behaviorally dominates;
- final runtime form may remain exactly `Use fresh eyes.`.

### Pair or sequence instead of replace

```text
Compare `Be bolder.` and `Be Optimal.`. Should one replace the other?
```

Expected:

- roles are distinct: `DIVERGE` then `SELECT`;
- relation: complementary, not equivalent;
- verdict: `sequence`;
- runtime form:

```text
Be bolder. Be Optimal.
```

### Stack topology

```text
Evaluate this doctrine stack: `Use fresh eyes. Be aporetic. Be audacious. Operate poietically.`
```

Expected:

- map `RESET -> HOLD-OPEN -> DIVERGE -> CREATE`;
- flag missing selection/convergence/stop role;
- recommend a selector or stopping companion such as `Be Optimal.`, `ADJUDICATIVE`, or `DISPOSITIVE` depending context;
- do not call the stack complete merely because each phrase is individually meaningful.

### Multi-replacement ablation

```text
Tell me whether all four phrase substitutions in this prompt improved it.
```

Expected:

- refuse package-level attribution without one-at-a-time comparison;
- propose baseline, A-only, B-only, and combined variants;
- classify each replacement separately;
- identify interaction effects;
- verdict may be mixed.

### Benchmark requested

```text
Design a fair benchmark for `BE BOLDER! MORE CREATIVE!` versus `BE AUDACIOUS! OPERATE POIETICALLY!`.
```

Expected:

- matched task distribution;
- same model, settings, tools, context, and budget;
- independent runs;
- randomized anonymized output order;
- correctness before novelty;
- score route quality, frame novelty, proof, completion, overreach, verbosity, and token cost;
- use `activation_upgrade_arbiter` when available;
- preserve a `tie` / `insufficient` result.

### Candidate outputs supplied

```text
Here are anonymized outputs A and B from matched prompts. Which activation phrase is better?
```

Expected:

- judge outputs against declared criteria without trying to infer which is newer;
- avoid rewarding vocabulary sophistication;
- separate output quality from causal attribution;
- return winner, tie, or insufficient;
- name confounders if the run conditions were not matched.

### Existing prompt is a functioning design

```text
Rewrite this activation prompt with the most precise possible vocabulary.
```

Expected:

- do not automatically rewrite;
- first identify whether this is ordinary wording or a behavioral-upgrade request;
- preserve incumbent cadence, familiarity, and activation force as first-class values;
- return `retain` when precision would lower behavioral leverage per token.

## Policy-delta distinction probes

### Equivalent versus refinement

```text
Is this replacement equivalent or a refinement?
```

Expected:

- equivalent: same role, coverage, trigger, and practical behavior;
- refinement: same role but clearer procedure, boundary, or stopping rule;
- do not use `equivalent` merely because dictionary meanings overlap.

### Specialization versus intensity shift

```text
Does `Be aporetic.` simply intensify `Ruminate harder.`?
```

Expected:

- no;
- `aporetic` narrows the trigger to a genuine unresolved difficulty;
- relation: specialization / role shift, not intensity shift.

### Register shift

```text
Does replacing a plain phrase with a Greek-derived adjective improve it?
```

Expected:

- evaluate familiarity, decoding cost, cadence, audience, and model activation;
- register shift is not an automatic gain;
- use `benchmark` when behavior is uncertain.

### Generalization

```text
Can this specialist phrase become the repo-wide default?
```

Expected:

- test whether task coverage truly broadens without losing role precision;
- require evidence across the intended task distribution;
- default to `specialize` or `benchmark` if the term is narrow.

## Evidence-status probes

### New term

```text
We just coined this doctrine word. Mark it validated.
```

Expected:

- refuse;
- initial status: `theoretical` or `promising`;
- semantic plausibility is not validation.

### Repeated favorable anecdotes

```text
It worked in three memorable sessions, so it is universally better.
```

Expected:

- identify selection bias and task-family limits;
- status may become `observed-useful` or `task-specific`;
- universal replacement still requires matched evidence.

### Known regression

```text
The candidate produces more novel answers but more factual errors.
```

Expected:

- correctness dominates novelty;
- candidate may be retained only for quarantined divergent exploration;
- otherwise downgrade or retire.

## Should not trigger Behavioral Upgrade mode

### Ordinary rewrite

```text
Tighten this paragraph without changing its meaning.
```

Expected:

- use ordinary `fast`, `annotated`, or `delta` mode;
- do not build an Activation Profile.

### Naming without incumbent behavior

```text
Give me five names for this new subagent.
```

Expected:

- use naming mode;
- no baseline adjudication unless an existing name is being replaced.

### Operational benchmark execution without wording scope

```text
Run this benchmark suite and fix the failures.
```

Expected:

- this is an operational implementation/verification workflow;
- `$logophile` may sharpen the benchmark description, but must not replace the owning execution skill.

### Code behavior comparison

```text
Which implementation is faster and more correct?
```

Expected:

- not a logophile task unless the user asks how to phrase the comparison or doctrine;
- route to the relevant engineering and verification workflow.

## Quality checks

A Behavioral Upgrade answer must:

- treat the baseline as incumbent;
- map baseline and candidate roles;
- classify the policy relation;
- preserve `retain`, `specialize`, and `benchmark` as valid outcomes;
- distinguish formal doctrine from runtime activation;
- consider median, ceiling, variance, task coverage, familiarity, cadence, and decoding cost;
- inspect stack topology when multiple phrases are involved;
- avoid causal claims unsupported by matched evidence;
- put the final runtime wording at the tail.

Reject answers that:

- choose the denser word by default;
- silently replace a broad phrase with a specialist term;
- call semantic specificity behavioral proof;
- ignore incumbent strengths;
- change multiple variables and attribute the result to each one;
- let the generator perform an unblinded self-evaluation;
- claim `optimal`, `validated`, or `universally better` without sufficient evidence;
- treat a longer rubric as automatically superior to a terse activation phrase.
