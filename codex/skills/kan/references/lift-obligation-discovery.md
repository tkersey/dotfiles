# Kan lift obligation discovery

## Purpose

Use this guide when a refactor is constrained by external behavior and you need to derive what internals must support before editing broadly.

Obligation discovery is a right-lift-flavored architecture pass:

```text
A --R?--> B
|         |
F         P
v         v
C
```

It asks:

```text
Given observable requirements F and projection P,
what internal obligations in B are sound, necessary, missing, or impossible?
```

Source basis for lift/residual language: `[KAN-NLAB-LIFT]`.

## Inputs

Collect:

- `A`: contract cases, tests, reports, policies, endpoints, workflows.
- `C`: observable outputs, traces, views, externally visible states.
- `F : A -> C`: required behavior for each case.
- `B`: internal artifacts that could support behavior: fields, transitions, services, resources, handlers, tables, capabilities.
- `P : B -> C`: how internal artifacts become observable.
- Comparison relation in `C`: equality, containment, implication, refinement, subset, snapshot equivalence, or trace preorder.

## Obligation kinds

### Data obligation

The required observation needs information that must be stored or derivable.

Example:

```text
Public view needs cancellation reason.
Internal model currently stores only cancellation status.
```

### Transition obligation

The required behavior needs an internal state transition or workflow branch.

Example:

```text
Refund after settlement must be rejected.
Internal workflow has no Settled -> RefundRejected transition.
```

### Capability obligation

The required behavior needs an external or internal capability.

Example:

```text
Payment capture needs gateway authorization capability.
```

### Temporal obligation

The required behavior depends on order, retry, idempotency, timeout, or exactly-once/at-least-once semantics.

Example:

```text
Second refund request must return the same result as the first.
```

### Observation obligation

The required behavior exists internally but is not exposed through `P`.

Example:

```text
Audit event is emitted, but public trace projection ignores audit sink.
```

### Coherence obligation

Several observations must agree.

Example:

```text
Order status endpoint and invoice report must agree about cancellation.
```

## Discovery algorithm

For each witness case `a`:

1. Enumerate public observations of `F(a)`.
2. For each observation, ask whether `P` can produce it from current `B`.
3. If yes, record the projection path and test.
4. If no, classify the missing obligation.
5. Decide whether to repair `B`, repair `P`, weaken `F`, or accept an approximation.
6. Add one law test for each repaired obligation.

Pseudo-shape:

```text
for a in A_witnesses:
  for obs in observations(F(a)):
    if exists b_path in B such that observe(P(b_path), obs) compares_to observe(F(a), obs):
      record present obligation
    else:
      record no-exact-lift obstruction
```

## No-exact-lift obstruction template

```text
Case:
Observation:
Required behavior F(a):
Current projection P can produce:
Missing in B:
Obstruction type: data / transition / capability / temporal / observation / coherence
Repair options:
  - enrich B:
  - change P:
  - weaken F:
  - external dependency:
Approximation available:
Witness test:
```

## Law tests for obligations

### Soundness

```text
project(obligation) <= required_behavior
```

### Coverage

```text
required_behavior <= project(realizer)
```

### Exactness

```text
project(realizer) == required_behavior
```

### Necessity approximation

For finite candidate sets:

```text
removing obligation causes at least one witness observation to fail
```

### Coherence

```text
all projected observations over the same public fact agree
```

## How to use with agents

Ask the agent to produce the obligation ledger before refactoring:

```text
Use $kan.
Treat this as a right-lift obligation discovery pass.
Do not modify code yet.
Inventory A, B, C, P, F.
For each public commitment, derive missing internal data, transitions, capabilities, temporal guarantees, and observation paths.
Classify exact lift, approximate lift, or no exact lift.
Produce tests first.
```

This prevents architecture edits that merely reshuffle code without satisfying external commitments.
