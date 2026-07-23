# Example Invocations

## Strategy

```md
Use $cybernetic.

We keep missing quarterly targets even though each team is hitting its local KPIs. Diagnose the system and recommend the highest-leverage intervention.
```

## Product

```md
Use $cybernetic.

Our onboarding funnel improved one metric but retention fell. Map the feedback loops and incentive/proxy risks before recommending changes.
```

## Engineering workflow

```md
Use $cybernetic with $negative-ledger.

Our review process keeps creating more code and more review findings. Identify the system type, feedback loops, leverage points, and intervention.
```

## Incident

```md
Use $cybernetic in Fast mode.

The deployment is causing customer-impacting failures and signals are unclear. What system type are we in and what should we do first?
```

## Non-activation

```md
A parser rejects one documented token because a single branch compares the wrong enum variant. The failing test names the branch and the direct owner is known.
```

Expected result: do not turn the task into a systems exercise. Route the clear local defect to its implementation owner and proof.

## Worked DART trace: recurring review loop

**Situation.** Three successive local patches address review findings in the same ownership cluster. Each patch adds another predicate, and the next review finds a sibling case.

### Deconstruct

- Boundary: the repeated review cluster, its current owner, mutation route, and review feedback path.
- Stable components: review protocol and owner boundary.
- Changing components: local predicates and sibling cases.
- Repeating pattern: each point fix expands surface without eliminating the finding class.
- Missing information: whether the current owner can represent the governing law directly.

### Analyze

- Classification: `complicated` for identifying the governing law and canonical owner; `complex` for predicting all future sibling cases from examples alone.
- Alternative: `clear` only if the recurrence is caused by one known checklist omission rather than a representation or ownership problem.
- Evidence that could flip the classification: a single existing invariant that covers every recurrence and was merely not executed.

### Recognize

- Analogue: whack-a-mole validation caused by an owner that stores examples instead of the governing law.
- Shared mechanism: local predicates react to observed instances while the admissible state space remains too broad.
- Important difference to check: recurrence may instead come from stale review fixtures.
- Likely next state if unchanged: another sibling predicate and a larger review surface.

### Test

- Mode: `hypothesis_validation`.
- Action: derive the governing law, enumerate the current sibling cases against it, and test whether one owner-level representation or transition excludes the entire class.
- Prediction: if owner shape is causal, the law-level candidate covers existing examples without new peer predicates.
- Failure signal: the candidate cannot express distinct accepted laws without conflating them.
- Stop condition: do not apply another local point patch while the owner-level hypothesis is unresolved.

### Cybernetic compilation

```yaml
cybernetic_context:
  required: yes
  trigger: same-cluster recurrence after claimed local closure
  system_type: mixed
  pattern: local fixes expand surface while preserving the invalid state class
  feedback_loop: review finding -> local predicate -> more surface -> sibling finding
  leverage_level: stock_flow_structure
  selected_intervention:
    status: selected
    route: handoff
    downstream_skill: universalist
  local_patch_allowed: no
  temporary_containment:
    allowed: no
    expiry_or_review: not_applicable
    durable_followup_owner: actuating
  monitoring_or_probe: law-level candidate must exclude the existing class without adding sibling predicates
```

## Worked DART trace: chaotic containment

**Situation.** A rollout is actively failing for customers, signals are incomplete, and the same component has a history of local patches.

Expected result:

- classify the active incident subsystem as chaotic;
- permit a bounded containment action if it reduces current harm;
- monitor the containment concurrently;
- keep durable local mutation denied until the system is reclassified and the recurring route is examined;
- record an expiry or review condition so containment does not silently become the permanent design.
