# Negative Ledger Activation Contract

## Purpose

Implicit activation should surface decision-shaping negative evidence without turning every ordinary implementation failure into durable scar tissue.

```text
activation is broad
capture is narrow
blocking is narrower
```

## Activate for a routing check

Activate when any of these could change the next route:

- a concrete implementation or decision had no effect;
- a benchmark or representative test regressed because of the attempted route;
- a route was reverted with a concrete rationale;
- the same route or same-cluster family is about to be retried;
- current work abandons a named strategy that future work could repeat;
- review or proof evidence falsified the selected normal form;
- the user asks what has already been tried or says not to retry a route;
- a learning hit describes a failed hypothesis that may need promotion;
- an artifact-state change may satisfy a recorded reopening criterion.

The first action is normally `query` or `map`, not `capture`.

## Capture gate

Capture only when the event has all of the following:

- a narrow hypothesis or route;
- a named attempted change or decision;
- an inspectable witness;
- a stated observed outcome and failure class;
- structured source references to inspectable evidence;
- a repository-bound, immutable artifact identity;
- current artifact-state applicability;
- an explicit supported scope and its identity;
- a narrow exclusion rule and future-routing delta;
- identified reopening criteria with explicit conditions.

Otherwise retain `no-op`, `capture_candidate`, `need-evidence`, or `unknown` as appropriate. Do not create an active exclusion.

## Do not activate solely for

- the first red test during an incomplete implementation;
- syntax, formatting, or type errors that merely indicate unfinished work;
- a local typo or discarded edit;
- brainstorming before any route has been attempted;
- positive learnings with no failed-hypothesis semantics;
- generic requests to improve code with no prior-attempt or regression cue.

## Dispositions

```text
mapped       read-only route check completed
captured     new witnessed record appended
transitioned existing record lifecycle changed
no-op        cue evaluated but no durable negative evidence qualified
blocked      operational gate unavailable/invalid or active exclusion matched
```

## Evaluation

Review empirical decision episodes, not raw mention counts. A healthy week may have zero captures, but a week containing witnessed reverts, repeated routes, or regression-driven pivots should not have zero activations.

For each candidate episode, ask:

1. Did `$negative-ledger` appear before the next route was selected?
2. Did it query/map rather than immediately capture?
3. Did transient failures remain `no-op`?
4. Did a qualified event produce durable, narrow evidence?
5. Did blocking require an active, fully validated, witnessed, exact native-scope match with current-state applicability?
6. Did map, export, and handoff fail closed rather than project malformed authority?
