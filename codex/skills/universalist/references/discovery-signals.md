# Discovery Signals

## How to use this file

Start from the code smell or boundary pressure, not the theory label. Match the
observed signal to the smallest construction that explains it, then choose the
smallest seam where that construction can land.

## Core signal table

| Signal in the repo | Default construction | Concrete evidence to look for | First seam to try | Cheapest proof signal | Common false positive |
| --- | --- | --- | --- | --- | --- |
| Several booleans, strings, or nullable fields try to describe one lifecycle | Coproduct | `status`, `state`, `phase`, `isApproved`, `publishedAt`, `archivedReason`, optional fields that should be mutually exclusive | DTO-to-domain decoder or one central state module | exhaustive handling + invalid legacy fixture tests | The fields are actually independent and belong in a product |
| The same predicate is checked at several boundaries | Equalizer / refined type | repeated `validate`, `parse`, `isValid`, trim/lowercase/normalize logic, the same regex or range check in multiple files | constructor, parser, or controller boundary | accept valid / reject invalid / normalization idempotence | The predicate is unstable or depends on external context |
| Two records must agree on a shared key or projection | Pullback witness | `customer.accountId != subscription.accountId`, repeated tenant/schema/version checks | checked composite constructor | mismatch rejection + preserved projections | A plain pair plus one assertion is good enough because the relationship is not stable |
| Large branch chooses pricing, rendering, or policy behavior | Exponential | long `switch`, `if/elif`, strategy flags, behavior selected by option bits | function parameter, strategy interface, or callable object seam | fixture parity against old implementation | The problem is state modeling, not behavior injection |
| A workflow or rule engine mixes syntax with execution and explanation | Free construction / initial algebra | builders that also execute, class trees that both model and evaluate, duplicated interpretive logic | AST + one interpreter | interpreter consistency + differential tests | There is only one execution path and the AST adds no value |
| Several fields always travel together and are consumed independently | Product | the same argument list or object shape passes through many layers unchanged | constructor, record, or object type | constructor + projection consistency | Hidden coupling means some combinations are actually illegal |

## Seam selection rubric

Score each candidate seam from 0 to 2 on each axis:

- **Locality**: how narrowly can you land the change?
- **Boundary stability**: can external wire or storage shapes stay stable?
- **Proofability**: is there an obvious test, compile check, or parity check?
- **Invariant gain**: how much truth becomes unrepresentable or centralized?
- **Rollback ease**: can the seam be reverted without repo-wide fallout?

Prefer the seam with the highest total that still uses the smallest
construction.

## Overreach checks

- Do not choose a larger construction just because it sounds elegant.
- Do not claim a pullback when the code only needs a pair and one runtime assertion.
- Do not claim a free construction unless multiple interpreters, folds, or explanation paths are part of the value.
- Do not claim an equalizer if the predicate is fuzzy, unstable, or depends on mutable external state.
- When two constructions compete, choose the smaller one first and name the larger one only if it unlocks a concrete next step.

## Cost notes by construction

### Product
Cheap and local. Prefer it when fields are genuinely independent.

### Coproduct
Moderate cost. Main pressure comes from decoding legacy shapes and touching exhaustiveness sites.

### Refined type
Usually cheap if construction can be centralized at boundaries. Cost rises when raw primitives leak deeply into persistence or templates.

### Pullback witness
Often cheap and high-value when the agreement check already exists in several places.

### Exponential
Usually cheap if there is already a natural function or strategy seam. More expensive when behavior is spread across shared mutable state.

### Free construction
Highest cost of the core six. Use only when separate syntax and multiple interpretations produce real value.
