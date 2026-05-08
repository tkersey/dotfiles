# Algebra-Driven Design Knowledge Base

This reference contains the conceptual knowledge needed to apply Algebra-Driven Design (ADD) to architecture, codebase implementation, and agentic workflows.

## 1. What ADD is

Algebra-Driven Design is a method for designing software by discovering the algebra of a domain: the values being manipulated, the operations that construct or transform those values, the observations that define their meaning, and the laws that must hold among the operations.

In this context, “algebra” does not mean arithmetic. It means:

```text
A carrier type + operations over that carrier + equations/laws that characterize behavior.
```

A minimal algebraic signature might be:

```text
Carrier:      Cart
Operations:   empty : Cart
              add   : Cart × Item × Quantity -> Cart
              merge : Cart × Cart -> Cart
Observation:  render : Cart -> CartView
Laws:         merge(empty, c) = c
              merge(a, merge(b,c)) = merge(merge(a,b), c)
```

The design goal is not to sound mathematical. The goal is to produce abstractions that are compositional, testable, optimizable, and resistant to leakage.

## 2. Why ADD matters

ADD provides a disciplined route from domain understanding to implementation.

Ordinary software design often starts from nouns, classes, components, screens, endpoints, or database tables. That frequently creates designs that match today’s surface requirements but fail when composition, ordering, retries, concurrency, or new features appear.

ADD starts from the operations and laws that the domain requires. This gives the designer leverage:

- If an operation is associative, it can be batched, chunked, folded, streamed, or parallelized.
- If an operation is commutative, order may not matter.
- If an operation is idempotent, retries and duplicate messages are safer.
- If a merge is a semilattice, distributed convergence is possible.
- If an operation is non-invertible, undo must be replaced with compensation and audit.
- If an observation ignores representation details, internal implementations can change without changing behavior.
- If laws are executable as tests, refactors and optimized implementations can be checked against the original semantics.

## 3. Core vocabulary

### Carrier

The domain set or type being acted upon. Examples:

```text
Cart, Order, Payment, PermissionSet, Config, EventStream, Plan, EvidenceSet, Draft, WorkflowState.
```

A carrier should have:

- a name;
- a semantic meaning;
- valid states;
- invalid states;
- operations that preserve validity;
- observations that define equality.

### Operation

A function, command, constructor, transformation, interpreter, or observation.

Operation kinds:

```text
Nullary constructor:  empty : A
Unary transformation: normalize : A -> A
Binary combinator:   combine : A × A -> A
Observation:         render : A -> View
Command:             submit : Command -> Effect[Event]
Event application:   apply : State × Event -> State
Interpreter:         run : Program[A] × Env -> Effect[A]
```

### Observation

An observation is the externally meaningful way to inspect a value. Observations define semantic equality.

Examples:

```text
Cart equality       = same user-visible line items, totals, promotions, and errors.
Order equality      = same lifecycle state, fulfillment state, audit obligations.
Report equality     = same claims, citations, validation status, and final deliverable.
Workflow equality   = same approved external effects and final result.
```

Observation selection is a central design act. If audit logs are observable, many laws fail. If audit logs are not observable but must be retained internally, laws may hold for user-visible behavior while not holding structurally.

### Law

A law is a statement about operations that should always hold under a chosen observation.

Examples:

```text
normalize(normalize(x)) = normalize(x)
merge(x, y) = merge(y, x)
append(append(a,b),c) = append(a,append(b,c))
project(eventsA ++ eventsB) = project(eventsB, project(eventsA, initial))
```

Laws can be unconditional, conditional, policy-enforced, or rejected as non-laws.

### Non-law

A non-law is a candidate rule that does not hold. Non-laws are design information.

Example:

```text
refund(capture(auth)) = auth
```

This is usually false because capture may move money, create settlement records, and introduce audit obligations. A refund may compensate financially, but it is not an inverse under trace or audit observations.

### Algebraic signature

A collection of carrier types and operation signatures, without implementation.

Example:

```text
Carrier: Order
Operations:
  create        : CustomerId × Items -> Order
  authorize     : Order × PaymentMethod -> Order
  capture       : Order -> Order
  cancel        : Order -> Order
  refund        : Order × Amount -> Order
  observe       : Order -> OrderView
```

### Model, denotation, and interpreter

A model or denotation gives meaning to the algebra. An interpreter maps abstract operations into a concrete implementation.

For example:

```text
Abstract operation:  sendEmail(to, subject, body)
Test interpreter:    append EmailRequested event to an in-memory list
Prod interpreter:    call email provider API and record provider message id
```

The operation is stable; the interpreter changes.

### Deep embedding

A deep embedding represents operations as data, often an abstract syntax tree or command list.

Example:

```text
Program = AddItem(item) | ApplyCoupon(code) | Checkout
```

Benefits:

- inspectable;
- serializable;
- easy to test;
- can have multiple interpreters;
- good for reference implementations and optimization passes.

Costs:

- more boilerplate;
- requires interpreter design;
- may be awkward for simple domains.

### Shallow embedding

A shallow embedding represents operations directly as functions.

Example:

```text
Cart -> Cart
```

Benefits:

- simple;
- efficient;
- direct;
- idiomatic in many languages.

Costs:

- less inspectable;
- harder to serialize or optimize globally;
- may entangle behavior with effects.

### Reference implementation

A simple, obviously correct implementation. It may be slow or memory-heavy. Its purpose is to define semantics.

### Optimized implementation

A production-oriented implementation. It must be tested against the reference implementation using laws, examples, and parity tests.

### Normal form

A canonical representation used to compare semantic equality.

Example:

```text
normalize(add(add(empty, A, 1), A, 2)) = { A: 3 }
```

Normal forms make equality, simplification, and optimization easier.

## 4. The ADD method in depth

### Phase A: Explore the domain language

Extract nouns, verbs, constraints, and observable outcomes from the domain.

Ask:

- What values exist?
- What actions are users or systems allowed to take?
- What is visible to users?
- What is visible to auditors, logs, analytics, or downstream systems?
- What is irreversible?
- What can be retried?
- What can be merged?
- What can be reordered?
- What must be sequenced?
- What counts as the same result?

### Phase B: Choose the observation boundary

The same representation can support different observations.

Example: cart update laws.

If only line items are observed:

```text
add(item, 1); add(item, 1) = add(item, 2)
```

If audit trail is observed:

```text
[Added item by click 1, Added item by click 2] != [Added item quantity 2]
```

So the law is either false, conditional, or scoped to a particular observation.

### Phase C: Build a candidate algebra

Define carriers and primitive operations. Keep operations small and composable.

Prefer:

```text
empty
single
combine
map
filter
validate
observe
```

over a large set of special-case operations unless the special cases reveal real domain distinctions.

### Phase D: Discover laws

Use multiple discovery strategies.

#### Identity search

Ask: is there an operation input that does nothing?

```text
empty <> x = x
x <> empty = x
```

#### Associativity search

Ask: does grouping matter?

```text
(a <> b) <> c = a <> (b <> c)
```

If yes, you can fold and batch.

#### Commutativity search

Ask: does order matter?

```text
a <> b = b <> a
```

If yes, you may support out-of-order processing or parallel accumulation.

#### Idempotency search

Ask: does doing it twice equal doing it once?

```text
f(f(x)) = f(x)
x <> x = x
```

If yes, retries and duplicate suppression may be simpler.

#### Inverse search

Ask: can an operation be undone under the chosen observation?

```text
undo(do(x)) = x
```

If not, model compensation instead of undo.

#### Annihilator search

Ask: is there a value that dominates or blocks composition?

```text
failure <> x = failure
deny <> allow = deny
missingApproval <> destructiveAction = blocked
```

#### Distributivity search

Ask: can one operation be pushed through another?

```text
map(f, xs ++ ys) = map(f, xs) ++ map(f, ys)
validate(a <> b) = validate(a) <> validate(b)
```

#### Fusion search

Ask: can adjacent operations be combined without changing observation?

```text
render(normalize(x)) = render(x)
map(f, map(g, xs)) = map(f ∘ g, xs)
```

#### Monotonicity search

Ask: does more input produce more or equal knowledge/state?

```text
a <= b => f(a) <= f(b)
```

Monotonicity is important for incremental computation, event logs, permissions, and distributed systems.

### Phase E: Find counterexamples

Every candidate law should be attacked.

Counterexample prompts:

- What if time is observed?
- What if audit logs are observed?
- What if permissions change between operations?
- What if inventory changes?
- What if external service call succeeds once and fails once?
- What if duplicate command ids appear?
- What if items have quantities, discounts, taxes, or dependencies?
- What if two operations touch the same resource?
- What if order is visible in the UI?
- What if partial failure happens?

### Phase F: Refine the algebra

When laws fail, respond by refining the model:

- weaken the law;
- add a precondition;
- change the observation;
- split one operation into two;
- add event/command distinction;
- add a carrier for audit/trace;
- introduce an error or validation carrier;
- make impossible states unrepresentable;
- move effects behind an interpreter.

### Phase G: Derive implementation

Implementation should preserve the algebra.

Canonical sequence:

```text
1. Define carriers.
2. Define primitive operations.
3. Define observations.
4. Define reference interpreter.
5. Write law tests against reference interpreter.
6. Implement optimized interpreter.
7. Compare optimized interpreter to reference interpreter.
8. Add runtime guards for policy laws.
9. Add migrations, monitoring, and trace checks.
```

## 5. ADD deliverables

### Domain algebra table

```text
Carrier | Meaning | Operations | Observations | Laws
```

### Law table

```text
Law | Formula | Holds? | Preconditions | Counterexample | Architecture implication | Test implication
```

### Architecture map

```text
Law -> Boundary -> Runtime mechanism -> Test
```

Example:

```text
Idempotency -> command boundary -> idempotency key store -> repeat command property test
```

### Implementation map

```text
Carrier -> Data type/schema
Operation -> Function/interface/command/event
Observation -> API response/view/projection
Law -> Property test/invariant/constraint
Interpreter -> Adapter/service/tool
```

### Risk register

```text
Risk | Failed law | Impact | Mitigation
```

## 6. ADD and architecture

Architecture is not a diagramming exercise first. It is a set of boundaries that preserve the domain algebra under real-world forces.

Examples:

- If retries are unavoidable, model idempotency.
- If order cannot be guaranteed, avoid laws that rely on ordering or introduce sequence numbers.
- If events are the source of truth, design around append/replay/fold laws.
- If approvals are required, model approval as a carrier and missing approval as an annihilator for destructive actions.
- If many adapters implement one abstract behavior, define an interpreter boundary.
- If users observe only projections, optimize storage while preserving projection equality.

## 7. ADD and codebase implementation

ADD is practical during implementation because it tells you what to code.

For each law, ask:

```text
What type encodes this?
What function preserves this?
What interface abstracts this?
What database constraint enforces this?
What test executes this?
What trace proves this in production?
```

Example: idempotent command handling.

```text
Law:
  handle(commandId, command) repeated = one durable effect

Code:
  Command has commandId.
  Handler checks processed_commands.
  DB has unique constraint on commandId.
  Tests submit duplicate command and assert one event/effect.
```

## 8. ADD and agentic workflows

Agentic systems are especially suited to ADD because they compose plans, tools, observations, memory, validations, approvals, and outputs.

Typical carriers:

```text
Task, Context, Plan, Step, ToolCall, Observation, EvidenceSet, Draft, ValidationResult, Approval, Trace, FinalAnswer.
```

Typical laws:

```text
Evidence merge is often commutative/idempotent under citation identity.
Validation is usually idempotent.
Plan sequencing is associative when steps are independent of grouping.
Destructive tool call without approval is blocked.
Untrusted source cannot authorize privileged action.
Finalization after failed validation is blocked.
```

The skill should convert these laws into workflow nodes, tool contracts, guardrails, tests, and evals.

## 9. How to handle uncertainty

Laws depend on the observation boundary and business assumptions. When uncertain:

- label the law as candidate or conditional;
- state the missing domain fact;
- provide a counterexample;
- design an architecture that can support both possibilities if feasible;
- recommend validation with domain experts or tests.

Do not hide uncertainty behind jargon.

## 10. ADD anti-patterns

### Algebra cosplay

Using words like monoid, functor, or semiring without deriving decisions.

Fix: Always map law -> architecture -> implementation -> test.

### Over-lawing

Declaring laws that the business domain does not support.

Fix: Write counterexamples before committing.

### Under-observing

Ignoring logs, time, identity, authorization, cost, latency, or external effects.

Fix: Make observations explicit.

### Representation lock-in

Treating the current data model as the domain algebra.

Fix: Define semantic carriers first; map existing data structures afterwards.

### Effect leakage

Mixing pure domain behavior with network, database, or tool effects.

Fix: separate operations from interpreters.

### Testing only examples

Examples are necessary but insufficient for algebraic laws.

Fix: add property tests, generated traces, and parity tests.

## 11. Practical ADD questions for interviews with stakeholders

Ask these to discover the algebra:

1. What does “same result” mean here?
2. Which operations can be repeated safely?
3. Which operations can be reordered?
4. Which operations can be batched?
5. Which operations have a no-op input?
6. Which operations can be undone, and under what observation?
7. Which operations must leave an audit trail?
8. Which errors dominate the workflow?
9. Which states should be impossible?
10. Which actions require approval?
11. Which queries must agree with which events?
12. Which behavior must survive refactoring?
13. Which external systems observe the difference between two internal representations?
14. Which operations are compensating rather than inverse?
15. Which laws would let us parallelize, cache, deduplicate, or retry?

## 12. Core ADD mantra

```text
Find the carriers.
Name the operations.
Choose the observations.
State the laws.
Break the false laws.
Derive the architecture.
Implement the algebra.
Test the laws.
Optimize only under preserved observation.
```
