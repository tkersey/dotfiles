# ADD Law and Structure Catalog

Use this catalog to identify algebraic structures in software domains and to map them into architecture, implementation, and tests.

## How to use the catalog

Do not force a domain into a named structure. Use names only after the laws fit.

For each candidate structure:

1. Identify carrier(s).
2. Identify operation(s).
3. Choose observations.
4. Check laws with examples and counterexamples.
5. Map true laws to implementation and tests.

## 1. Closure

```text
op : A × A -> A
```

Closure means an operation on values of type `A` returns a valid `A`.

Software implication:

- operation preserves valid state;
- invalid states need separate carriers such as `Result[A, Error]`;
- schemas and constructors should enforce validity.

Test:

```text
forall a b. valid(a) and valid(b) => valid(op(a,b))
```

## 2. Semigroup

Carrier `A` with binary operation `<>`.

Law:

```text
(a <> b) <> c = a <> (b <> c)
```

Meaning: grouping does not matter.

Architecture implications:

- batch processing;
- streaming folds;
- chunked processing;
- incremental aggregation;
- parallel reduction if operation is also safe to distribute.

Implementation implications:

- expose `combine(a,b)`;
- avoid APIs that require arbitrary grouping choices;
- consider reducers and folds.

Examples:

- concatenating event streams;
- combining logs;
- summing totals;
- composing independent validation messages;
- composing report sections when order is preserved.

Non-examples:

- floating-point arithmetic under strict equality can violate associativity because of precision;
- operations with hidden time, identity, or side effects often fail associativity.

## 3. Monoid

A semigroup with identity `empty`.

Laws:

```text
empty <> a = a
a <> empty = a
(a <> b) <> c = a <> (b <> c)
```

Architecture implications:

- safe defaults;
- empty states;
- no-op commands;
- fold over zero or more inputs;
- incremental accumulation.

Implementation implications:

- provide explicit `empty`, `zero`, `identity`, or `default`;
- ensure the identity does not accidentally add observable metadata;
- test left and right identity separately.

Examples:

- empty shopping cart under item/totals observation;
- empty list of events;
- empty evidence set;
- no-op plan;
- empty validation result if validation accumulates warnings.

## 4. Commutative monoid

A monoid where order does not matter.

Additional law:

```text
a <> b = b <> a
```

Architecture implications:

- order-insensitive queues;
- easier reconciliation;
- some parallel processing;
- deterministic aggregation from unordered inputs.

Examples:

- set union;
- summing integer counts;
- accumulating independent facts keyed by stable identity;
- merging tags.

Cautions:

- UI ordering may be observable;
- audit logs are usually ordered;
- duplicate behavior may make union and list concatenation different.

## 5. Idempotent commutative monoid / join semilattice

A commutative monoid with idempotency.

Additional law:

```text
a <> a = a
```

Often called a join semilattice when the operation is interpreted as least upper bound / merge.

Architecture implications:

- convergence under duplicate messages;
- safe retries for merge-like updates;
- CRDT-like distributed state;
- duplicate evidence elimination;
- monotonic knowledge accumulation.

Examples:

- set union;
- maximum timestamp under suitable ordering;
- permission grants as set union, if denies are not included;
- evidence references keyed by source id;
- feature flags merged by lattice rules.

Cautions:

- adding the same payment twice is not idempotent unless keyed;
- appending the same log twice is not idempotent if log multiplicity is observed;
- idempotency may require a stable operation id.

## 6. Group

A monoid where every element has an inverse.

Law:

```text
a <> inverse(a) = empty
inverse(a) <> a = empty
```

Architecture implications:

- undo is possible;
- reversible transformations;
- bidirectional migrations in limited settings;
- reversible editor operations.

Cautions:

Most business effects are not groups under audit/trace observation. Payment capture, email send, shipment, deletion, and external API calls are usually not invertible. They may have compensating operations instead.

## 7. Cancellation and compensation

Do not confuse inverse with compensation.

Inverse:

```text
undo(do(x)) = x
```

Compensation:

```text
observe(compensate(do(x))) ≈ acceptable_repair_state
```

Architecture implications:

- sagas;
- compensating events;
- audit trail;
- human review;
- eventual correction rather than rollback.

Examples:

- refund compensates for capture but does not erase capture;
- cancellation after shipment may create return flow, not undo shipment;
- deleting a posted message may create a tombstone, not remove historical visibility.

## 8. Annihilator / absorbing element

A value that dominates composition.

Law:

```text
zero <> a = zero
a <> zero = zero
```

Architecture implications:

- validation failure blocks finalization;
- deny overrides allow;
- missing approval blocks destructive action;
- poison pill messages stop unsafe processing;
- failed precondition short-circuits execution.

Examples:

- `Denied` in authorization;
- `Invalid` in strict validation;
- `Blocked` for destructive action without approval;
- `FatalError` in a pipeline.

Cautions:

Some validation should accumulate errors rather than annihilate. Choose deliberately.

## 9. Semiring

Two operations, often called addition and multiplication.

Laws:

```text
(a + b) + c = a + (b + c)
a + b = b + a
zero + a = a

(a * b) * c = a * (b * c)
one * a = a
a * one = a

a * (b + c) = (a * b) + (a * c)
(a + b) * c = (a * c) + (b * c)
zero * a = zero
a * zero = zero
```

Architecture implications:

- alternative vs sequence;
- route choice vs path concatenation;
- cost models;
- query planning;
- parser composition;
- workflow branching.

Examples:

- regular expressions: alternation and concatenation;
- shortest path: min and plus;
- probabilities: plus and multiplication;
- validation: choice and sequencing in some designs.

## 10. Lattice

A partial order with join and meet.

Laws:

```text
join(a,b) = join(b,a)
meet(a,b) = meet(b,a)
join(a,join(b,c)) = join(join(a,b),c)
meet(a,meet(b,c)) = meet(meet(a,b),c)
join(a,a) = a
meet(a,a) = a
join(a, meet(a,b)) = a
meet(a, join(a,b)) = a
```

Architecture implications:

- permissions;
- policy composition;
- distributed config;
- feature flag resolution;
- data classification levels;
- monotone workflows.

Example:

```text
classification: public <= internal <= confidential <= restricted
join = more restrictive of two classifications
meet = less restrictive of two classifications
```

## 11. Boolean algebra

A lattice with complement, top, and bottom.

Architecture implications:

- policy expression;
- search filters;
- query predicates;
- feature enablement conditions.

Cautions:

Business policy often uses three-valued or effectful logic: allow, deny, unknown. Do not assume classical Boolean laws if missing data, precedence, or audit are observable.

## 12. Category

Objects with arrows/morphisms and composition.

Laws:

```text
id ; f = f
f ; id = f
(f ; g) ; h = f ; (g ; h)
```

Architecture implications:

- pipelines;
- workflow steps;
- data transformations;
- ETL;
- compiler passes;
- middleware chains;
- agent handoffs.

Examples:

- `parse -> validate -> transform -> render`;
- agent handoff from research to drafting to validation;
- data processing stages where input/output types line up.

Cautions:

Effects, errors, retries, and timeouts may require enriched structures rather than plain composition.

## 13. Functor

A structure that supports mapping over contained values while preserving shape.

Laws:

```text
map(id) = id
map(f ∘ g) = map(f) ∘ map(g)
```

Architecture implications:

- transform payload while preserving context;
- generic handling of optional, list, result, async, or event-wrapped values;
- clear separation of data transformation from structure.

Examples:

- mapping over `Option[A]`;
- mapping over `Result[A, E]` while preserving errors;
- transforming event payloads without changing event metadata.

## 14. Applicative

A structure for combining independent effects/computations.

Core intuition:

```text
pure : A -> F[A]
apply : F[A -> B] × F[A] -> F[B]
```

Architecture implications:

- independent validations can run in parallel;
- form validation can accumulate errors;
- independent tool calls can be planned statically;
- workflow shape known before execution.

Use when steps are independent.

## 15. Monad / dependent sequencing

A structure for sequencing computations where the next step depends on the previous result.

Core intuition:

```text
return : A -> M[A]
bind   : M[A] × (A -> M[B]) -> M[B]
```

Architecture implications:

- dependent workflows;
- stateful interactions;
- agent tool loops;
- failure-aware sequencing;
- dynamic plans.

Cautions:

Monad vocabulary is not needed unless it clarifies implementation. The practical point is dependent sequencing.

## 16. Fold / reducer algebra

A reducer applies events, commands, or inputs to state.

Signature:

```text
apply : State × Event -> State
fold  : State × List[Event] -> State
```

Laws:

```text
fold(s, []) = s
fold(s, xs ++ ys) = fold(fold(s, xs), ys)
```

Architecture implications:

- event sourcing;
- replay;
- projections;
- snapshots;
- audit trails;
- deterministic reconstruction.

Test:

```text
replay(events) equals state produced by applying events one by one
snapshot/replay equals full replay
```

## 17. Event stream monoid

Carrier:

```text
EventStream = List[Event]
```

Operation:

```text
append : EventStream × EventStream -> EventStream
```

Laws:

```text
[] ++ xs = xs
xs ++ [] = xs
(xs ++ ys) ++ zs = xs ++ (ys ++ zs)
```

Observations:

- final projection;
- audit stream;
- event count;
- event order.

Architecture implications:

- append-only store;
- reducers;
- projections;
- sequence numbers;
- snapshotting;
- trace-based tests.

Caution: event stream append is not commutative if order is observable.

## 18. State machine algebra

Carrier:

```text
State
```

Operations:

```text
transition : State × Input -> State | Error
```

Laws/invariants:

- impossible transitions are rejected;
- terminal states remain terminal;
- valid transitions preserve invariants;
- certain transitions require authorization;
- certain paths are irreversible.

Architecture implications:

- state transition table;
- command handlers;
- guards;
- lifecycle events;
- generated tests for all transition pairs.

## 19. Validation algebra

Two common designs.

### Accumulating validation

Carrier:

```text
Validation = Valid | Invalid(Set[Error])
```

Laws:

```text
errors accumulate by union
Invalid(e1) <> Invalid(e2) = Invalid(e1 ∪ e2)
```

Good for forms, reports, linting, and static checks.

### Short-circuit validation

Carrier:

```text
Result = Ok[A] | Err[E]
```

Law:

```text
Err(e) bind f = Err(e)
```

Good for dependent workflows where later steps need earlier outputs.

Architecture implications:

- choose accumulating or short-circuit deliberately;
- expose validation type in APIs;
- distinguish warnings from blockers.

## 20. Permission and policy algebra

Common carrier:

```text
Decision = Allow | Deny | Unknown
```

Possible laws:

```text
Deny <> x = Deny
Allow <> Unknown = Allow? or Unknown? depending policy
Unknown <> Unknown = Unknown
```

Architecture implications:

- deny-overrides policy engine;
- capability tokens;
- audit decisions;
- explainability for policy composition.

Cautions:

Policy laws are governance choices. State them explicitly.

## 21. Idempotent command handling

Idempotency law:

```text
handle(command_id, command) repeated = one durable effect
```

Architecture implications:

- idempotency key;
- processed command table;
- unique database constraint;
- deterministic response for repeated command;
- retry-safe external API integration.

Test:

```text
submit same command twice -> one event/effect and same observable result
```

## 22. Cache laws

Potential laws:

```text
cache(get(k)) = get(k) under freshness policy
invalidate(k); get(k) = source_get(k)
put(k,v); get(k) = v if no intervening invalidation/expiration
```

Architecture implications:

- explicit freshness observation;
- invalidation as operation;
- monotonic cache impossible if source mutates arbitrarily;
- cache correctness must state time assumptions.

## 23. Query laws

Examples:

```text
filter(p, filter(q, xs)) = filter(x => p(x) && q(x), xs)
map(f, map(g, xs)) = map(f ∘ g, xs)
sort(sort(xs)) = sort(xs)
limit(n, limit(m, xs)) = limit(min(n,m), xs)
```

Architecture implications:

- query optimizer;
- pipeline fusion;
- index selection;
- view materialization;
- deterministic sorting requirements.

Cautions:

Pagination, time, authorization, and concurrent writes can break naive query laws.

## 24. Normalization laws

Normalizer:

```text
normalize : A -> A
```

Laws:

```text
normalize(normalize(a)) = normalize(a)
observe(normalize(a)) = observe(a)
```

Architecture implications:

- canonical storage;
- deduplication;
- comparison by normal form;
- simplification before execution.

Examples:

- combine duplicate cart lines;
- canonicalize permission rules;
- sort tags;
- remove redundant workflow steps.

## 25. Agentic workflow laws

Common carriers:

```text
Plan, Step, ToolCall, Observation, EvidenceSet, Draft, ValidationResult, Approval, Trace
```

Candidate laws:

```text
Plan sequencing associative:
  (p then q) then r = p then (q then r)

No-op plan identity:
  empty then p = p
  p then empty = p

Evidence merge semilattice:
  merge(e1,e2) = merge(e2,e1)
  merge(e, e) = e

Validation idempotent:
  validate(validate(x)) = validate(x)

Repair closure:
  repair(x, failures) returns same deliverable type

Approval annihilator:
  missingApproval ⋅ destructiveAction = blocked

Untrusted source safety:
  untrustedInput cannot authorize privileged action
```

Architecture implications:

- separate planning from execution;
- evidence deduplication by source identity;
- validation loop can repeat safely;
- destructive actions require hard runtime gates;
- tool interpreters must be auditable.

## 26. Law-to-test mapping

```text
Law type           Test type
Associativity      property test with three generated values
Identity           property test with generated value and empty
Commutativity      property test with two generated values
Idempotency        property test applying operation twice
Inverse            property test with round trip
Annihilator        property test with blocking/failure value
Distributivity     property test comparing two evaluation paths
Fold law           replay test over concatenated event streams
Interpreter law    parity test between reference and production interpreter
Policy law         scenario and trace tests
Non-law            regression test with counterexample
```

## 27. Law-to-architecture mapping cheat sheet

```text
Associativity  -> batching, folding, streaming, parallel reduction
Identity       -> safe defaults, empty objects, no-op commands
Commutativity  -> out-of-order processing, reconciliation
Idempotency    -> retries, dedupe keys, unique constraints
Semilattice    -> convergence, distributed merges, duplicate tolerance
Inverse        -> undo, reversible migrations, reversible UI actions
Non-inverse    -> compensation, sagas, audit
Annihilator    -> hard guards, deny-overrides, validation blockers
Distributivity -> optimization, query planning, pushing filters down
Monotonicity   -> append-only logs, incremental projections
Functor        -> structure-preserving transformation
Applicative    -> independent parallel validation/effects
Monad          -> dependent sequencing and tool loops
Reducer        -> event sourcing, replay, projections
```
