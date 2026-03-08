# Universalist Case Studies

## Table of contents
- Case 1: Workflow flags to coproduct (TypeScript)
- Case 2: Shared-id join to pullback witness (Go)
- Case 3: Repeated validation to refined type (Java or Python)
- Case 4: Branchy policy logic to exponential (Java or C#)
- Case 5: Rule engine to free construction (TypeScript or Python)

## Case 1: Workflow flags to coproduct (TypeScript)
**Domain**: A document lifecycle uses `status`, `approved`, `publishedAt`, and `archivedReason` fields that drift out of sync.

**Construction**: Coproduct for the lifecycle plus a product for shared metadata.

**Architecture change**
- Replace string flags and booleans with a tagged union.
- Keep stable fields such as title and body in a product type.
- Add a boundary decoder so API or DB rows can stay in the legacy shape during a small refactor.
- Centralize transitions in one pure function.

**Why this fits**
- Each document is in exactly one state.
- Eliminating impossible combinations is the main win, not algebraic combination.

**Testing**
- Exhaustive handling for every state.
- Migration test from the legacy row shape to exactly one variant.
- Deterministic fixtures for invalid legacy field combinations.
- Differential check that legal transitions still behave the same.

## Case 2: Shared-id join to pullback witness (Go)
**Domain**: An API handler pairs a `Customer` record and a `Subscription` record but must reject mismatched `AccountID` values.

**Construction**: Pullback-shaped join over `AccountID`.

**Architecture change**
- Introduce a checked constructor such as `NewCustomerSubscription`.
- Preserve both projections so callers can still access each original view.
- Delete scattered `if customer.AccountID != subscription.AccountID` checks from business code.

**Why this fits**
- The real invariant is agreement over a shared projection.
- A plain pair plus repeated assertions leaks the proof obligation everywhere.

**Testing**
- Constructor accepts matching pairs.
- Constructor rejects mismatches.
- Follow-up operations preserve the witness or require reconstruction.

## Case 3: Repeated validation to refined type (Java or Python)
**Domain**: Email addresses or non-empty identifiers are revalidated in controllers, services, and serializers.

**Construction**: Equalizer or refined type at the boundary.

**Architecture change**
- Replace raw strings with a value object or wrapper built through one checked constructor.
- Normalize once, for example lowercase and trim, if the domain allows it.
- Parse once in controllers and serializers, keep services and repositories on the refined type, and unwrap only at explicit I/O boundaries.

**Why this fits**
- The main property is membership in a stable legal subset.
- A single constructor is simpler than re-running the same predicate everywhere.

**Testing**
- Accept valid inputs.
- Reject invalid inputs.
- Prove normalization is idempotent if normalization exists.
- Add boundary tests showing the raw string becomes the refined value exactly once.

## Case 4: Branchy policy logic to exponential (Java or C#)
**Domain**: Pricing or policy code switches on flags to decide which calculation to run.

**Construction**: Exponential encoded as a strategy, closure, or function object.

**Architecture change**
- Replace a large branch with a supplied function or strategy interface.
- Compose reusable behaviors instead of appending more conditionals.
- If combination laws matter, apply ADD inside the strategy outputs, for example a monoid for audit logs.

**Why this fits**
- The real variation is behavior from input to output.
- The code wants parameterized computation, not a larger state machine.

**Testing**
- Fixture-based behavior tests for each supplied strategy.
- Composition-order tests when strategies chain.
- Differential check against the old branchy implementation during migration.

## Case 5: Rule engine to free construction (TypeScript or Python)
**Domain**: A workflow or rule engine mixes business syntax, evaluation, and logging inside one class hierarchy.

**Construction**: Free construction or initial algebra via an AST plus interpreters.

**Architecture change**
- Model the rules as syntax nodes.
- Add one interpreter for execution and one for explanation or logging.
- Keep constructors dumb and interpreters explicit, then add adapters from the legacy class tree into the shared rule AST.

**Why this fits**
- Multiple interpretations are valuable.
- Separating syntax from execution makes testing and migration easier.

**Testing**
- Interpreter consistency on a shared corpus of rules.
- Explanation output should line up with the same branch decisions used by evaluation.
- Fold or evaluation tests for representative trees.
- Differential tests against the legacy evaluator until migration is complete.
