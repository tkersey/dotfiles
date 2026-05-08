# Applying ADD to Codebase Implementation

This reference turns ADD analysis into code, tests, refactors, and implementation plans.

## 1. Implementation thesis

ADD implementation is the process of making the domain algebra executable.

```text
Carrier      -> data type, schema, value object, state type
Operation    -> function, method, command, event, endpoint, handler
Observation  -> view, projection, API response, trace, assertion
Law          -> property test, invariant, constraint, runtime guard
Interpreter  -> adapter, service implementation, tool executor, database gateway
```

The central implementation rule:

```text
Do not optimize until you have a simple semantic oracle.
```

The oracle may be a reference implementation, a deep embedding interpreter, a mathematical normal form, or a golden trace model.

## 2. Codebase analysis workflow

When analyzing an existing codebase, inventory these elements.

### Carriers

Look for:

- domain models;
- aggregate roots;
- DTOs;
- database tables;
- request/response schemas;
- workflow state enums;
- event types;
- configuration objects;
- permission/policy objects;
- agent state structures.

Record:

```text
Carrier | Source files | Meaning | Valid states | Observed by | Problems
```

### Operations

Look for:

- public methods;
- endpoint handlers;
- command handlers;
- event handlers;
- reducers;
- service methods;
- batch jobs;
- external tool calls;
- database mutations;
- validators;
- mappers.

Record signatures:

```text
operation : Input -> Output
operation : State × Command -> State × Event
operation : Context × ToolCall -> Effect[Observation]
```

### Observations

Look for:

- API responses;
- UI rendering;
- database state;
- event logs;
- audit logs;
- metrics;
- emails/messages;
- external API calls;
- generated reports;
- user-visible errors.

### Mutation inventory

Find every place state changes. Classify:

```text
pure transformation
state mutation
persistent write
external effect
audit/log effect
notification effect
```

ADD usually improves implementation by separating these.

## 3. Implementation sequence

### Step 1: Define carriers as explicit types

Bad:

```python
def process(data: dict) -> dict: ...
```

Better:

```python
@dataclass(frozen=True)
class Cart:
    lines: tuple[LineItem, ...]
```

### Step 2: Define operations with signatures

Bad:

```python
def update_cart(request): ...
```

Better:

```python
def add_item(cart: Cart, item: ItemId, qty: Quantity) -> Cart: ...
def apply_coupon(cart: Cart, coupon: CouponCode) -> Cart: ...
def observe_cart(cart: Cart) -> CartView: ...
```

### Step 3: Define observation equality

Example:

```python
def cart_observation(cart: Cart) -> CartView:
    return CartView(lines=normalize_lines(cart.lines), total=price(cart))
```

Then tests compare observations rather than private representation when appropriate.

### Step 4: Write law tests

Example:

```python
def test_merge_identity(cart):
    assert observe(merge(empty_cart(), cart)) == observe(cart)
    assert observe(merge(cart, empty_cart())) == observe(cart)
```

### Step 5: Write a reference implementation

Reference implementation may be slow but should be simple.

Example:

```python
def merge_reference(a: Cart, b: Cart) -> Cart:
    lines = list(a.lines) + list(b.lines)
    return normalize_cart(Cart(tuple(lines)))
```

### Step 6: Build optimized implementation

Example:

```python
def merge_optimized(a: Cart, b: Cart) -> Cart:
    # map by item id for speed
    totals = dict(a.as_quantity_map())
    for item_id, qty in b.as_quantity_map().items():
        totals[item_id] = totals.get(item_id, 0) + qty
    return Cart.from_quantity_map(totals)
```

### Step 7: Parity test optimized against reference

```python
def test_merge_matches_reference(a, b):
    assert observe(merge_optimized(a,b)) == observe(merge_reference(a,b))
```

### Step 8: Enforce laws in runtime

Some laws require runtime mechanisms:

- idempotency key store;
- unique constraints;
- locks or version checks;
- policy engine;
- approval gates;
- state transition validation;
- event sequence numbers;
- canonicalization;
- schema validation.

## 4. Data representation patterns

### Algebraic data types / discriminated unions

Use when states or events have distinct variants.

Python:

```python
@dataclass(frozen=True)
class Authorized:
    authorization_id: str

@dataclass(frozen=True)
class Captured:
    capture_id: str

PaymentState = Authorized | Captured
```

TypeScript:

```ts
type PaymentState =
  | { kind: "Authorized"; authorizationId: string }
  | { kind: "Captured"; captureId: string };
```

Why:

- prevents illegal states;
- makes pattern matching explicit;
- avoids flag combinations.

### Value objects

Use when a primitive value has laws or constraints.

Examples:

```text
Money, Quantity, EmailAddress, IdempotencyKey, Percentage, DateRange.
```

### Command/event split

Use when commands request effects and events record accepted facts.

```text
Command: CapturePayment(orderId, amount, idempotencyKey)
Event:   PaymentCaptured(orderId, amount, providerCaptureId)
```

Why:

- commands can fail;
- events are facts;
- idempotency belongs to command handling;
- reducers apply events deterministically.

### Reducer

```python
def apply_event(state: State, event: Event) -> State:
    ...
```

Reducer laws:

```text
fold(s, []) = s
fold(s, xs ++ ys) = fold(fold(s, xs), ys)
```

### Interpreter interface

Use when abstract operations have multiple implementations.

Python:

```python
class PaymentPort(Protocol):
    def authorize(self, request: AuthorizationRequest) -> AuthorizationResult: ...
    def capture(self, request: CaptureRequest) -> CaptureResult: ...
```

Test interpreter records calls. Production interpreter calls external provider.

### Normalizer

Use when many representations have same observation.

```python
def normalize(cart: Cart) -> Cart:
    ...
```

Laws:

```text
normalize(normalize(x)) = normalize(x)
observe(normalize(x)) = observe(x)
```

## 5. Reference implementation patterns

### Deep embedding

Represent the domain language as data.

```python
@dataclass(frozen=True)
class AddItem:
    item_id: str
    qty: int

@dataclass(frozen=True)
class ApplyCoupon:
    code: str

CartProgram = AddItem | ApplyCoupon
```

Then write interpreters:

```python
def interpret(program: list[CartProgram], cart: Cart) -> Cart: ...
def interpret_for_trace(program: list[CartProgram]) -> list[TraceEvent]: ...
```

Good for:

- tool workflows;
- event sourcing;
- test generation;
- optimization passes;
- simulations;
- workflows that need audit.

### Shallow embedding

Represent operations directly as functions.

```python
CartOp = Callable[[Cart], Cart]
```

Good for:

- simple domains;
- local pure transformations;
- performance-critical code after laws are tested.

### Normal form oracle

Define canonical representation and compare it.

```python
def normal_form(x: A) -> CanonicalA: ...
```

Good for:

- sets/maps;
- expression simplification;
- permission rules;
- query predicates;
- plan simplification.

### Trace oracle

For effects, compare traces rather than values.

```text
execute(program) -> Trace
```

Trace equality may ignore timestamps but include externally visible calls.

Good for:

- agents;
- external APIs;
- workflow engines;
- email/payment/shipping integrations.

## 6. Law tests by language

### Python with Hypothesis

Associativity:

```python
from hypothesis import given

@given(a=values(), b=values(), c=values())
def test_combine_associative(a, b, c):
    left = combine(combine(a, b), c)
    right = combine(a, combine(b, c))
    assert observe(left) == observe(right)
```

Identity:

```python
@given(a=values())
def test_combine_identity(a):
    assert observe(combine(empty(), a)) == observe(a)
    assert observe(combine(a, empty())) == observe(a)
```

Idempotency:

```python
@given(a=values())
def test_normalize_idempotent(a):
    assert observe(normalize(normalize(a))) == observe(normalize(a))
```

### TypeScript with fast-check

```ts
import fc from "fast-check";

fc.assert(
  fc.property(valueArb, valueArb, valueArb, (a, b, c) => {
    expect(observe(combine(combine(a,b),c))).toEqual(
      observe(combine(a,combine(b,c)))
    );
  })
);
```

### Java/Kotlin/C#/Go

If property testing libraries are not available or not accepted by the team:

- generate random test data manually;
- use table-driven tests for laws;
- generate traces from fixtures;
- create metamorphic tests;
- compare optimized implementation to reference implementation;
- run state-machine tests.

## 7. Generator quality

Property tests are only useful if generators cover meaningful cases.

Generator checklist:

- includes empty values;
- includes singletons;
- includes duplicates;
- includes boundary values;
- includes invalid or rejected operations when testing validators;
- includes conflicting operations;
- includes repeated command ids;
- includes out-of-order events;
- includes terminal states;
- includes permission edge cases;
- shrinks to understandable counterexamples.

Common mistake:

```text
Generator creates only valid happy paths, so laws appear true but fail in production.
```

## 8. Refactoring with ADD

### Refactor 1: Extract carrier

Before:

```python
def submit_order(user_id, items, coupon, payment_method, address): ...
```

After:

```python
@dataclass(frozen=True)
class OrderDraft:
    user_id: UserId
    items: tuple[LineItem, ...]
    coupon: Coupon | None
    shipping_address: Address
```

### Refactor 2: Split command from event

Before:

```python
def capture_payment(order):
    order.status = "captured"
    provider.capture(order)
```

After:

```python
def decide_capture(order: Order, cmd: CapturePayment) -> list[PaymentCommand]: ...
def apply_event(order: Order, event: PaymentCaptured) -> Order: ...
def interpret_payment_command(cmd: PaymentCommand, port: PaymentPort) -> PaymentEvent: ...
```

### Refactor 3: Extract observation

Before:

```python
assert cart1 == cart2
```

After:

```python
assert observe_cart(cart1) == observe_cart(cart2)
```

### Refactor 4: Introduce normalizer

Before:

```python
# duplicate line items handled everywhere
```

After:

```python
cart = normalize_cart(cart)
```

### Refactor 5: Replace flags with state variants

Before:

```python
class Order:
    paid: bool
    shipped: bool
    cancelled: bool
    refunded: bool
```

After:

```text
OrderState = Draft | Authorized | Captured | Shipped | Cancelled | Refunded
```

### Refactor 6: Wrap effects with ports

Before:

```python
def checkout(cart):
    db.save(cart)
    stripe.charge(...)
    email.send(...)
```

After:

```python
def decide_checkout(cart, command) -> list[EffectCommand]: ...
def interpret_effect(command, ports) -> Event: ...
```

## 9. Implementation by law

### Associativity implementation checklist

- Is there a `combine` operation?
- Does it avoid hidden side effects?
- Does grouping change logs, timestamps, order, or IDs?
- Can chunks be processed independently?
- Is there a property test over three values?
- Is there a chunking parity test?

### Identity implementation checklist

- Is identity represented explicitly?
- Does identity allocate observable IDs or timestamps?
- Is identity safe as a default?
- Are both left and right identity tested?

### Commutativity implementation checklist

- Is order truly unobservable?
- Are duplicates handled?
- Are audit logs excluded or modeled separately?
- Does the database query return deterministic order when order is observed?
- Is commutativity tested over generated pairs?

### Idempotency implementation checklist

- Does each command have a stable identity?
- Is there a processed-command ledger?
- Is there a unique constraint or atomic guard?
- Are repeated calls given the same observable response?
- Are external provider idempotency features used if available?
- Is duplicate submission tested?

### Inverse/compensation checklist

- Under which observation is inverse claimed?
- Are external effects observed?
- If not invertible, what compensating action exists?
- Is compensation modeled as a new event?
- Are audit obligations preserved?

### Annihilator checklist

- What value blocks composition?
- Is blocking enforced in code, not just instructions?
- Are blocked traces impossible to execute?
- Is deny precedence tested?
- Are validation failures clearly separated from warnings?

## 10. Database implementation

ADD laws often need database constraints.

Examples:

```text
Idempotency             -> unique(command_id)
No duplicate line item  -> unique(cart_id, item_id)
Event ordering          -> unique(stream_id, sequence_number)
Valid transition        -> transaction + current_state check
Foreign reference       -> foreign key
Monotonic version       -> optimistic lock/version column
Permission denial       -> policy decision table/audit
```

Never rely only on application code for laws that must survive concurrency.

## 11. API implementation

Map endpoint semantics to laws.

```text
GET    observation, should be side-effect-free except logs/metrics
PUT    often idempotent replacement
PATCH  transformation; idempotency depends on patch semantics
POST   command; often not idempotent unless key supplied
DELETE may be idempotent if deletion observation is tombstone/absent
```

ADD API questions:

- What is the carrier?
- What operation is this endpoint exposing?
- What observation does response represent?
- Is retry safe?
- Does operation require idempotency key?
- What state transitions are invalid?
- What audit event is emitted?
- What policy law blocks this call?

## 12. Agent/tool implementation

For agentic codebases:

```text
Tool schema         -> operation signature
Tool result         -> observation
Tool side effect    -> trace event
Approval check      -> policy annihilator
Planner output      -> abstract program
Executor            -> interpreter
Validator           -> idempotent checker
Repair              -> transformation preserving deliverable carrier
```

Implementation rules:

- separate plan generation from execution;
- make tool calls typed;
- record traces;
- validate before finalization;
- enforce destructive action approval in tool executor;
- treat untrusted content as data, not instruction;
- compare traces in tests.

## 13. Deliverable: codebase implementation plan

Use this template:

```markdown
# ADD Codebase Implementation Plan

## Target domain

## Carriers and files

## Operations and signatures

## Observations

## Laws and tests

## Reference implementation

## Optimized implementation

## Interfaces and interpreters

## Database/API changes

## Refactor sequence

## Risks and counterexamples

## Acceptance criteria
```

## 14. Code review checklist

During code review, ask:

- Does this code preserve the stated laws?
- Does it introduce hidden observations such as time, IDs, logs, ordering, or external calls?
- Does it conflate command and event?
- Does it compare representation when it should compare observation?
- Does it make invalid states representable?
- Does it require distributed consistency accidentally?
- Does it include property tests for laws?
- Does it include counterexample tests for rejected laws?
- Does optimized code have a reference parity test?
- Are policy laws enforced by runtime checks?

## 15. Production monitoring from laws

Some laws should be checked in production through metrics and traces.

Examples:

```text
Duplicate command produced duplicate effect count > 0
Event sequence gap detected
Projection replay mismatch
Validation failure followed by publish event
Unauthorized destructive tool call attempted
Compensation flow not completed within SLA
Cache served value older than freshness law
```

ADD does not stop at tests. Critical laws become runtime observability.

## 16. Strong implementation principle

```text
A codebase implements an algebra well when every important operation is explicit, every important observation is named, every critical law is executable, and every effect is interpreted through a boundary that can be tested.
```
