# ADD Worked Examples

Use these examples as patterns for applying Algebra-Driven Design to real systems. They are intentionally cross-domain so the method transfers.

## Example 1: Shopping cart

### Domain frame

A user can add items, remove items, apply coupons, view totals, and check out.

### Carriers

```text
Cart
LineItem
Coupon
CartView
PriceBreakdown
```

### Operations

```text
emptyCart     : Cart
addItem       : Cart × ItemId × Quantity -> Cart
removeItem    : Cart × ItemId × Quantity -> Cart
setQuantity   : Cart × ItemId × Quantity -> Cart
applyCoupon   : Cart × CouponCode -> Cart
mergeCart     : Cart × Cart -> Cart
observeCart   : Cart -> CartView
priceCart     : Cart × PricingContext -> PriceBreakdown
checkout      : Cart × CheckoutCommand -> Result[OrderCreated]
```

### Observations

Possible observation boundaries:

1. item quantities only;
2. item quantities + prices;
3. item quantities + prices + coupon state;
4. full audit trail of cart operations.

Laws differ by observation.

### Candidate laws

#### Empty identity

```text
mergeCart(emptyCart, c) = c
mergeCart(c, emptyCart) = c
```

Likely true under item/totals observation.

Architecture:

- define empty cart explicitly;
- allow cart initialization from identity.

Test:

- property test over generated carts.

#### Merge associativity

```text
mergeCart(mergeCart(a,b),c) = mergeCart(a,mergeCart(b,c))
```

Likely true if merge adds quantities and normalizes lines.

Architecture:

- cart fragments can be accumulated;
- cart restoration from multiple sources can fold.

#### Merge commutativity

```text
mergeCart(a,b) = mergeCart(b,a)
```

True if line order and audit order are not observed. False if line ordering means “first added” or audit order is observed.

#### Add same item fusion

```text
addItem(addItem(c, item, q1), item, q2) = addItem(c, item, q1 + q2)
```

Conditional:

- true if inventory, promotion thresholds, and audit logs are not observed between operations;
- false if each add creates separate audit event visible to users/support.

#### Remove inverse

```text
removeItem(addItem(c, item, q), item, q) = c
```

Conditional:

- true under item quantity observation if item was not already present and no audit is observed;
- false if adding/removing emits visible logs, changes promotion state, or item quantity floor behavior differs.

#### Checkout idempotency

```text
checkout(commandId, cart) repeated = one order
```

Must be enforced by architecture if retries are possible.

Architecture:

- checkout command includes idempotency key;
- database unique constraint on key;
- processed command table;
- repeated request returns same order id.

### Implementation

```python
@dataclass(frozen=True)
class Cart:
    quantities: Mapping[ItemId, Quantity]

EMPTY_CART = Cart({})

def merge_cart(a: Cart, b: Cart) -> Cart:
    result = dict(a.quantities)
    for item, qty in b.quantities.items():
        result[item] = result.get(item, 0) + qty
    return Cart({item: qty for item, qty in result.items() if qty > 0})
```

### Tests

```text
merge identity
merge associativity
merge commutativity if order unobserved
add fusion
remove inverse counterexample tests
checkout duplicate command test
```

## Example 2: Payment lifecycle

### Domain frame

An order payment can be authorized, captured, voided, refunded, or failed.

### Carriers

```text
PaymentState
PaymentCommand
PaymentEvent
PaymentTrace
Money
IdempotencyKey
```

### Operations

```text
authorize : PaymentDraft × AuthorizationCommand -> Effect[PaymentEvent]
capture   : AuthorizedPayment × CaptureCommand -> Effect[PaymentEvent]
void      : AuthorizedPayment × VoidCommand -> Effect[PaymentEvent]
refund    : CapturedPayment × RefundCommand -> Effect[PaymentEvent]
apply     : PaymentState × PaymentEvent -> PaymentState
observe   : PaymentState -> PaymentView
```

### Laws and non-laws

#### Event fold law

```text
fold(s, []) = s
fold(s, xs ++ ys) = fold(fold(s,xs),ys)
```

Architecture:

- payment events can be replayed;
- projection can rebuild state;
- snapshot parity tests.

#### Capture idempotency

```text
capture(commandId, authorizedPayment) repeated = one capture effect
```

Architecture:

- idempotency key;
- unique key per payment/capture command;
- provider idempotency feature if available;
- trace test: duplicate command yields one external capture.

#### Refund is not inverse of capture

False law:

```text
refund(capture(p)) = p
```

Counterexample:

- capture moved money;
- refund creates new transaction;
- audit trace differs;
- fees and settlement may differ.

Correct model:

```text
refund compensates capture financially under money-balance observation, but not under audit trace observation.
```

Architecture:

- saga/compensation model;
- explicit events `PaymentCaptured` and `PaymentRefunded`;
- audit trail retained.

#### Void vs refund distinction

```text
void(authorized) -> no captured funds
refund(captured) -> compensating funds movement
```

Architecture:

- state machine prevents refund before capture;
- state machine prevents void after capture unless domain supports it differently.

### Implementation plan

- use state variants, not booleans;
- command handler validates transition;
- external provider is a port/interpreter;
- event reducer is pure;
- duplicate command tests;
- transition table tests;
- provider trace tests.

## Example 3: Permissions and policy

### Domain frame

A system determines whether a user may perform an action on a resource.

### Carriers

```text
Principal
Action
Resource
PolicyRule
Decision = Allow | Deny | Unknown
DecisionTrace
```

### Operations

```text
evaluateRule   : PolicyRule × Principal × Action × Resource -> Decision
combineDecision : Decision × Decision -> Decision
explainDecision : DecisionTrace -> Explanation
```

### Laws

Possible deny-overrides algebra:

```text
Deny <> x = Deny
x <> Deny = Deny
Allow <> Unknown = Allow
Unknown <> Allow = Allow
Unknown <> Unknown = Unknown
Allow <> Allow = Allow
```

This is a policy law, not a mathematical inevitability.

### Architecture implications

- policy engine centralizes decision combination;
- deny is an annihilator;
- every decision has explanation trace;
- authorization guard exists before destructive actions;
- tests cover precedence.

### Non-law

```text
Allow <> Deny = Allow
```

False under deny-overrides.

## Example 4: Configuration merge

### Domain frame

Configuration values come from defaults, environment, team settings, and user overrides.

### Carriers

```text
Config
ConfigPatch
SourcePriority
```

### Operations

```text
emptyConfig : Config
merge       : Config × Config -> Config
observe     : Config -> EffectiveConfig
```

### Possible laws

If merge is priority-based, it may not be commutative:

```text
merge(defaults, userOverrides) != merge(userOverrides, defaults)
```

If merge is represented as a join over `(priority, value)` per key, a commutative semilattice may be possible:

```text
join(a,b) = maxByPriority(a,b)
```

provided priority is part of each value and tie-breaking is deterministic.

### Architecture implications

- encode source priority explicitly;
- avoid relying on file load order unless order is part of semantics;
- include deterministic tie-breakers;
- test merge associativity/commutativity/idempotency if claimed.

## Example 5: Event-sourced order lifecycle

### Domain frame

Orders can be created, paid, shipped, cancelled, returned, and refunded.

### Carriers

```text
OrderState
OrderEvent
OrderCommand
EventStream
OrderProjection
```

### Operations

```text
append       : EventStream × EventStream -> EventStream
decide       : OrderState × OrderCommand -> Result[List[OrderEvent]]
apply        : OrderState × OrderEvent -> OrderState
fold         : OrderState × EventStream -> OrderState
project      : EventStream -> OrderProjection
snapshot     : EventStream -> Snapshot
```

### Laws

Event stream monoid:

```text
[] ++ xs = xs
xs ++ [] = xs
(xs ++ ys) ++ zs = xs ++ (ys ++ zs)
```

Fold law:

```text
fold(s, xs ++ ys) = fold(fold(s,xs),ys)
```

Snapshot law:

```text
replay(snapshot(prefix), suffix) = replay(initial, prefix ++ suffix)
```

State transition laws:

```text
cancel after shipped is invalid unless domain supports return flow
ship before paid is invalid unless payment terms allow it
terminal states reject lifecycle-changing commands
```

### Architecture implications

- append-only event store;
- optimistic concurrency on stream version;
- pure reducer;
- projection rebuilds;
- command handler enforces transition invariants;
- snapshot parity tests;
- event versioning and migration laws.

## Example 6: Research/report agent

### Domain frame

An agent researches a topic, gathers evidence, writes a report, validates claims, and produces a final artifact.

### Carriers

```text
ResearchQuestion
Source
EvidenceItem
EvidenceSet
Claim
ClaimGraph
Draft
Citation
ValidationResult
Report
```

### Operations

```text
search          : ResearchQuestion -> Effect[List[Source]]
readSource      : Source -> Effect[EvidenceItem]
mergeEvidence   : EvidenceSet × EvidenceSet -> EvidenceSet
extractClaims   : EvidenceSet -> ClaimGraph
draftReport     : ClaimGraph × StyleSpec -> Draft
validateClaims  : Draft × EvidenceSet -> ValidationResult
repairDraft     : Draft × ValidationResult -> Draft
finalizeReport  : Draft × ValidationResult -> Report
```

### Laws

Evidence merge as semilattice:

```text
merge(a,b) = merge(b,a)
merge(a,a) = a
merge(merge(a,b),c) = merge(a,merge(b,c))
```

under source-id observation.

Validation idempotency:

```text
validate(draft, frozenEvidence) repeated = same result
```

Unsupported claim blocker:

```text
unsupportedClaimsPresent ⋅ finalize = blocked
```

Recency dominance for current facts:

```text
currentFact requires source freshness check
```

This is not a pure algebraic law; it is a research policy law.

### Architecture implications

- evidence store deduplicated by source id;
- claim graph has support/refute edges;
- validation must run before finalization;
- current-fact claims require fresh sources;
- finalizer blocked by unsupported claims;
- citations are an observation of report quality.

## Example 7: ADD skill itself

### Domain frame

A skill helps an agent apply Algebra-Driven Design to architecture and implementation tasks.

### Carriers

```text
UserRequest
TaskClassification
ADDAnalysis
DomainAlgebra
LawCatalog
ArchitectureMap
ImplementationPlan
TestPlan
ValidationResult
SkillArtifact
```

### Operations

```text
activateSkill     : UserRequest -> Bool
loadReference     : TaskClassification -> ReferenceSet
identifyCarriers  : ProblemStatement -> List[Carrier]
identifyOperations: ProblemStatement × Carriers -> List[Operation]
defineObservations: Carriers × Operations -> List[Observation]
proposeLaws       : Operations × Observations -> List[Law]
mapArchitecture   : Laws -> ArchitectureMap
mapImplementation : ArchitectureMap -> ImplementationPlan
generateTests     : Laws -> TestPlan
validateAnalysis  : ADDAnalysis -> ValidationResult
```

### Laws

Output completeness law:

```text
ADDAnalysis is complete only if it includes carriers, operations, observations, laws/non-laws, architecture implications, implementation implications, and tests.
```

Law mapping law:

```text
Every accepted law maps to at least one architecture consequence and one test/guard.
```

Effect separation law:

```text
Every effectful operation identifies an interpreter/boundary.
```

Safety blocker:

```text
Destructive action without approval = blocked
```

### Architecture implications

- main `SKILL.md` defines operating loop;
- reference files contain deep knowledge;
- scripts validate structure and generate test skeletons;
- evals check behavior;
- source notes preserve provenance.

## Example 8: Code review workflow

### Domain frame

An agent reviews a pull request for correctness, safety, design, and test coverage.

### Carriers

```text
Diff
FileChange
Finding
FindingSet
RiskLevel
ReviewComment
ReviewSummary
```

### Operations

```text
parseDiff      : RawDiff -> Diff
inspectChange  : FileChange -> FindingSet
mergeFindings  : FindingSet × FindingSet -> FindingSet
rankFindings   : FindingSet -> OrderedFindings
draftComments  : OrderedFindings -> List[ReviewComment]
```

### Laws

Finding merge semilattice if keyed by stable finding id:

```text
merge(a,b) = merge(b,a)
merge(a,a) = a
```

Ranking is not commutative in output form because order is observable:

```text
rank(merge(a,b)) may be stable, but rendered comments are ordered.
```

No unsupported accusation law:

```text
finding without evidence cannot be emitted as definitive comment
```

### Architecture implications

- findings carry evidence location;
- duplicates collapse by finding id;
- comments are rendered after ranking;
- severe findings block approval;
- uncertain findings marked as such.

## Example 9: Data import pipeline

### Domain frame

A system imports rows from external files, validates them, transforms them, and writes records.

### Carriers

```text
RawRow
ParsedRow
ValidatedRow
ImportBatch
ValidationErrorSet
WriteCommand
ImportTrace
```

### Operations

```text
parse       : RawRow -> Result[ParsedRow]
validate    : ParsedRow -> Validation[ValidatedRow]
mergeErrors : ErrorSet × ErrorSet -> ErrorSet
transform   : ValidatedRow -> WriteCommand
write       : WriteCommand -> Effect[WriteEvent]
```

### Laws

Error accumulation semilattice:

```text
mergeErrors(a,b) = mergeErrors(b,a)
mergeErrors(a,a) = a
```

Batch associativity:

```text
process(batch1 ++ batch2) = combine(process(batch1), process(batch2))
```

conditional on no cross-row constraints.

Cross-row uniqueness breaks independent batch law unless modeled:

```text
validate(row1) + validate(row2) cannot detect duplicate key across rows unless key set is carried.
```

### Architecture implications

- validation result includes key set;
- batch processor carries accumulated constraints;
- write command uses idempotency key;
- import trace records row-level outcomes.

## Example 10: Content publishing workflow

### Domain frame

A user drafts, reviews, approves, schedules, and publishes content.

### Carriers

```text
Draft
ReviewFinding
Approval
Schedule
PublishCommand
PublishEvent
PublicationState
```

### Operations

```text
edit       : Draft × Edit -> Draft
review     : Draft -> FindingSet
approve    : Draft × Reviewer -> Approval
schedule   : ApprovedDraft × Time -> ScheduledPublication
publish    : ScheduledPublication -> Effect[PublishEvent]
```

### Laws

Review idempotency under frozen criteria:

```text
review(draft) repeated = same findings
```

Approval blocker:

```text
missingApproval ⋅ publish = blocked
```

Publish idempotency:

```text
publish(publicationId) repeated = one public item
```

Edit invalidates approval:

```text
edit(approvedDraft, change) -> unapprovedDraft
```

Architecture implications:

- approval tied to content hash/version;
- publish command has idempotency key;
- scheduler checks approval version;
- review findings are accumulated and tracked.

# Example usage prompt patterns

Use these prompt skeletons with the skill:

```text
Analyze this architecture with ADD. Identify carriers, operations, observations, laws, non-laws, and derive boundaries and tests.
```

```text
Refactor this codebase using ADD. Extract domain algebra, propose interfaces, identify effect boundaries, and generate property tests.
```

```text
Design an agentic workflow using ADD. Model plans, evidence, tools, validation, approvals, traces, and evals.
```

```text
Create an ADD report for this system. Include counterexamples and law-to-architecture mappings.
```
