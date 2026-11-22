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

For a resembling retry or potentially applicable exclusion, begin with read-only
`route-candidates` discovery from component, invariant, and failure-mechanism
terms. Assess the candidates, then use the exact `route-gate` with established
scope/artifact identities. For a newly observed failure, first assess its claim,
applicability, and destination using the [entrypoint](../SKILL.md#evidence-and-destination).
Do not resolve storage solely to produce a no-op receipt.

## Capture and exclusion

Use the [capture workflow and scope challenge](capture.md). A retained experiment
may affect a future investigation without supporting an exclusion. An adequate
existing construction, test, policy, native memory, or experiment can make a new
canonical record unnecessary. Preserve uncertain canonical candidates only when
their retention adds decision value; incomplete evidence cannot become `active`.

## Do not activate solely for

- the first red test during an incomplete implementation;
- syntax, formatting, or type errors that merely indicate unfinished work;
- a local typo or discarded edit;
- brainstorming before any route has been attempted;
- positive learnings with no failed-hypothesis semantics;
- generic requests to improve code with no prior-attempt or regression cue;
- terminal handoff or closeout with no failed-route semantics.

## Dispositions

```text
mapped       read-only route check completed
captured     new witnessed record appended
transitioned existing record lifecycle changed
no-op        no new canonical record needed; another destination suffices or evidence does not qualify
blocked      operational gate unavailable/invalid or active exclusion matched
```

## Evaluation

Review empirical decision episodes, not raw mention counts. Compare useful
selection before consequential decisions, unnecessary invocations, outcome
quality, and total work. Zero captures can be correct when existing owners
already retain what future decisions need.

For each candidate episode, ask:

1. Did `$negative-ledger` appear before the next route was selected?
2. When prior failure could constrain a proposed route, did it discover current
   candidates, assess applicability, and project the exact gate rather than rely
   on a label miss or immediately capture?
3. Did transient failures remain `no-op`?
4. Did useful evidence reach an adequate existing or new destination with its
   scope preserved and without redundant capture?
5. Did blocking require an active, fully validated, witnessed, exact native-scope
   match with current applicability and authoritative lifecycle state?
6. Did invalid reads remain distinct from empty results, and did independent
   memory failures remain separate from canonical validity?
7. Did a supported construction remove redundant warnings only for the domain it
   covers, while preserving historical evidence and exclusions valid elsewhere?
