# Applying ADD to Software Architecture

This reference explains how to derive architecture from algebraic laws.

## 1. Architecture as law preservation

In ADD, architecture is the set of boundaries, representations, services, adapters, workflows, and runtime controls required to preserve the domain laws under real-world conditions.

The central mapping is:

```text
Domain law -> architectural boundary -> implementation mechanism -> executable test/trace
```

Examples:

```text
Idempotency -> command boundary -> idempotency key store -> duplicate-command property test
Associativity -> aggregation boundary -> streaming fold -> chunking parity test
Deny overrides -> policy boundary -> policy engine -> deny precedence scenario test
Non-invertible payment -> saga boundary -> compensation flow -> trace test
```

## 2. Architecture derivation workflow

### Step 1: Name the carriers

Examples:

```text
Order, Payment, Shipment, EventStream, Projection, PolicyDecision, Plan, EvidenceSet.
```

### Step 2: Name the operations

Examples:

```text
appendEvent, applyEvent, authorize, capture, refund, mergePolicy, project, validate, executeTool.
```

### Step 3: State observations

Architecture cannot be correct until equality is defined.

Observation examples:

- API response equality;
- final database state;
- domain projection;
- audit trace;
- external effect trace;
- policy outcome;
- user-visible UI state;
- generated artifact contents.

### Step 4: Classify laws

Mark each candidate law as:

```text
true, conditional, false, policy-required, unknown.
```

### Step 5: Derive boundaries

Each law suggests a boundary or runtime mechanism. Each non-law suggests a guard or explicit sequence.

### Step 6: Select patterns

Choose architecture patterns only after identifying the algebraic need.

## 3. Law-to-boundary mappings

### Associativity

Law:

```text
(a <> b) <> c = a <> (b <> c)
```

Architectural consequences:

- batch processing and chunking are safe;
- stream processing can fold in chunks;
- partial aggregates can be combined;
- tree-shaped parallel processing can preserve results.

Patterns:

- reducers;
- map/reduce;
- streaming pipelines;
- event-log folds;
- batch windows.

Implementation mechanisms:

- accumulator type;
- reducer function;
- chunk parity tests;
- deterministic aggregation.

Cautions:

- floating point, timestamps, audit order, external effects, and nondeterminism can break associativity.

### Identity

Law:

```text
empty <> a = a
```

Architectural consequences:

- define safe empty/default state;
- allow zero-input workflows;
- avoid nullable absence when identity exists;
- support incremental accumulation from empty.

Patterns:

- empty object;
- no-op command;
- default projection;
- seed state for fold.

Cautions:

- default values can be dangerous if they imply permission, money, identity, or irreversible external effects.

### Commutativity

Law:

```text
a <> b = b <> a
```

Architectural consequences:

- order-insensitive processing;
- queue reordering tolerance;
- parallel collection;
- distributed aggregation;
- easier reconciliation.

Patterns:

- set-based events;
- unordered message processing;
- conflict-free merge;
- idempotent accumulators.

Cautions:

- user-facing order, audit trails, generated prose, and temporal workflows often make order observable.

### Idempotency

Law:

```text
f(f(x)) = f(x)
```

or for commands:

```text
execute(commandId, command) repeated = one observable durable effect
```

Architectural consequences:

- retry safety;
- duplicate message handling;
- external API call safety;
- dedupe boundaries.

Patterns:

- idempotency keys;
- unique constraints;
- processed-command ledger;
- deterministic response replay;
- exactly-once effect facade over at-least-once delivery.

Cautions:

- idempotency often requires stable identity. Without a command id, two identical-looking requests may be intentionally distinct.

### Semilattice merge

Laws:

```text
merge(a,b) = merge(b,a)
merge(merge(a,b),c) = merge(a,merge(b,c))
merge(a,a) = a
```

Architectural consequences:

- distributed convergence;
- duplicate tolerance;
- monotonic state growth;
- conflict resolution by join.

Patterns:

- CRDT-like state;
- distributed config;
- evidence accumulation;
- feature flag resolution;
- replicated permissions.

Cautions:

- deletes, revocations, and time-bounded validity require richer structures, not plain set union.

### Monotonicity

Law:

```text
a <= b => f(a) <= f(b)
```

Architectural consequences:

- append-only logs;
- incremental projections;
- static analysis;
- dataflow systems;
- fewer retractions.

Patterns:

- event sourcing;
- materialized views;
- monotone queries;
- immutable facts.

Cautions:

- deletion, revocation, negative facts, and mutable source data break monotonicity unless modeled explicitly.

### Invertibility

Law:

```text
undo(do(x)) = x
```

Architectural consequences:

- reversible transformations;
- undo stack;
- reversible migrations;
- bidirectional edits.

Patterns:

- command pattern with inverse;
- reversible editor operations;
- migration rollback.

Cautions:

- do not claim invertibility for operations with externally visible effects unless the observation boundary excludes those effects.

### Non-invertibility and compensation

Architectural consequences:

- sagas;
- compensation events;
- audit trails;
- eventual correction;
- human escalation.

Patterns:

- payment refund after capture;
- return flow after shipment;
- cancellation request after fulfillment;
- tombstone after deletion.

### Annihilator / blocker

Law:

```text
blocker <> action = blocker
```

Architectural consequences:

- hard guardrail layer;
- validation blockers;
- deny-overrides authorization;
- approval gates;
- fail-closed security posture.

Patterns:

- policy engine;
- guard middleware;
- preflight validation;
- explicit workflow state `Blocked`.

Cautions:

- prompt-only policy is insufficient for high-impact actions; enforce blockers in runtime code.

### Distributivity

Law:

```text
f(a <> b) = f(a) <> f(b)
```

Architectural consequences:

- push computation closer to source;
- query optimization;
- pipeline fusion;
- incremental materialization.

Patterns:

- map-reduce;
- predicate pushdown;
- compiler optimization;
- SQL query planning.

### Fusion

Law:

```text
observe(transform2(transform1(x))) = observe(fusedTransform(x))
```

Architectural consequences:

- eliminate intermediate allocations;
- combine workflow steps;
- optimize pipelines;
- reduce tool calls.

Cautions:

- only safe when intermediate observations, logs, and failure modes are not externally significant.

## 4. Architecture patterns through ADD

### Event sourcing

ADD fit:

```text
EventStream forms a monoid under append.
State is a fold over events.
Projection is an observation of event history.
```

Core laws:

```text
fold(s, []) = s
fold(s, xs ++ ys) = fold(fold(s, xs), ys)
snapshot(fold(s, prefix)) + replay(suffix) = replay(prefix ++ suffix)
```

Architecture:

- append-only event store;
- deterministic reducer;
- projection builders;
- snapshotting;
- event versioning;
- trace tests.

Use when:

- audit matters;
- lifecycle matters;
- replay matters;
- projections change over time;
- business events are meaningful.

Avoid or constrain when:

- event ordering is unclear;
- schema evolution is uncontrolled;
- teams only need CRUD;
- audit trail is not worth operational complexity.

### CQRS

ADD fit:

```text
Commands request state transitions.
Events record accepted transitions.
Queries observe projections.
```

Architecture:

- separate command model and query model;
- reducers build projections;
- query laws define consistency expectations;
- command handlers enforce invariants.

Key question:

```text
Which observations must be immediately consistent, and which may lag?
```

### Ports and adapters / hexagonal architecture

ADD fit:

```text
Domain algebra is abstract.
Interpreters implement external effects.
```

Architecture:

- pure domain core;
- ports for abstract operations;
- adapters for databases, HTTP, queues, tools, external APIs;
- test interpreters for law tests.

Use when:

- external dependencies should not define the domain;
- same algebra needs multiple runtimes;
- tests need deterministic effects.

### Domain-driven design bounded contexts

ADD fit:

```text
A bounded context owns a coherent algebra and its vocabulary.
```

Architecture:

- separate carriers and operations by domain language;
- anti-corruption layers translate between algebras;
- context maps describe homomorphisms or lossy translations.

Warning:

If two teams use the same words with different laws, they are likely separate bounded contexts.

### Workflow/saga architecture

ADD fit:

```text
Workflow = sequence/graph of operations with compensation and policy laws.
```

Architecture:

- state machine;
- command/event separation;
- compensation operations;
- timeout policies;
- retry/idempotency boundary;
- approval gates.

Use when:

- operations span services;
- effects are not atomic;
- rollback is impossible;
- external systems participate.

### Data pipeline architecture

ADD fit:

```text
Pipeline stages are composable arrows.
Aggregation uses monoids/semigroups.
Filtering/mapping laws enable optimization.
```

Architecture:

- typed stage contracts;
- deterministic transformations;
- replayable inputs;
- stage-level observations;
- golden outputs and property tests.

### Microservices

ADD fit:

Microservice boundaries should follow algebraic cohesion, not just entity nouns.

Good boundary indicators:

- coherent carrier and operations;
- laws mostly internal;
- external communication is via stable observations/events;
- invariants do not require distributed transactions across services.

Bad boundary indicators:

- one law requires simultaneous state changes across services;
- every operation needs synchronous cross-service calls;
- semantic equality depends on data owned by another service;
- error handling is dominated by distributed compensation.

### API architecture

ADD fit:

API endpoints expose operations and observations.

Design questions:

- Which endpoint is a command vs observation?
- Which commands are idempotent?
- Which observations define resource equality?
- Which transitions are invalid?
- Which operations need stable command ids?
- Which operations expose non-invertible effects?

API rules from ADD:

- `PUT`-like operations should be idempotent by design.
- `POST` operations that create effects should accept idempotency keys when retry is expected.
- query parameters should obey query laws where possible.
- destructive endpoints need explicit approval/authorization laws.

### Agent architecture

ADD fit:

```text
Agent workflow = algebra over plans, tool calls, observations, evidence, validation, and approval.
```

Architecture:

- planner produces abstract plan;
- tool executor interprets plan steps;
- evidence accumulator deduplicates sources;
- validator is idempotent and repeatable;
- repair loop uses validation failures;
- approval gate blocks destructive actions;
- finalizer observes validated state.

See `references/agentic-skill-application.md`.

## 5. Architecture output template

Use this structure when producing an architecture analysis.

```markdown
# ADD Architecture Analysis

## Executive summary

## Domain algebra

### Carriers

### Operations

### Observations

## Laws and non-laws

| Law | Status | Consequence |
|---|---|---|

## Architecture derived from laws

| Law | Boundary | Mechanism | Test |
|---|---|---|---|

## Proposed components

## Data/event model

## Effect and interpreter model

## Runtime guardrails

## Migration/refactor plan

## Risks and assumptions

## Next decisions
```

## 6. Architecture review checklist

Use this checklist to evaluate an architecture proposal.

- Does every component correspond to carriers, operations, observations, or interpreters?
- Are boundaries justified by laws or non-laws?
- Are effects isolated behind explicit interfaces?
- Are irreversible operations modeled as such?
- Are retries safe where retries are possible?
- Are idempotency keys or dedupe stores present where needed?
- Are distributed merges lawful or merely hopeful?
- Are projections tied to event/reducer laws?
- Are permissions modeled with explicit precedence?
- Are approval gates enforced by runtime mechanisms?
- Are optimizations justified by preservation of observation?
- Are caches governed by freshness laws?
- Are tests derived from laws?

## 7. Migration strategy from legacy architecture

When applying ADD to an existing codebase:

1. Inventory existing operations from endpoints, service methods, jobs, and event handlers.
2. Group operations by carrier and observation.
3. Identify hidden laws already assumed by the system.
4. Identify laws violated by implementation.
5. Extract pure reducers/validators first.
6. Add reference implementation around high-value workflows.
7. Introduce property/trace tests before broad refactor.
8. Wrap external effects with interpreters or ports.
9. Migrate one algebraic boundary at a time.
10. Use counterexamples to prioritize fixes.

## 8. Architecture smells ADD detects

### Retry without idempotency

Symptom: duplicate payments, duplicate emails, duplicate jobs.

ADD diagnosis: command execution lacks idempotency law or stable operation identity.

### Distributed transaction by accident

Symptom: multiple services must update atomically for invariant to hold.

ADD diagnosis: invariant crosses service boundaries; bounded context split is wrong or saga semantics are missing.

### Unclear equality

Symptom: teams disagree whether two states are “the same.”

ADD diagnosis: observations are not defined.

### CRUD masking lifecycle

Symptom: update endpoint accepts impossible transitions.

ADD diagnosis: state machine carrier is missing; operations are too generic.

### Optimized implementation has no semantic oracle

Symptom: performance rewrite changes behavior.

ADD diagnosis: no reference implementation or law tests.

### Prompt-only guardrail

Symptom: agent instructed not to do unsafe action, but tool/runtime allows it.

ADD diagnosis: policy law is not enforced in architecture.

## 9. Strong architecture principle

```text
The architecture is correct only if it preserves the domain observations under the operations and laws the business depends on.
```
