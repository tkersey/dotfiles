# Universalist Testing Playbook

## Start with the repo you have

Before recommending tests or edits, verify what already exists.

- prefer the current test runner
- prefer the current fixture and assertion style
- prefer deterministic checks when no property-testing tool exists
- only propose new dependencies after explicit user approval

## Fastest credible proof signal by track

### Track A — Diagnosis only
You may not need to run tests, but you must still name the cheapest future proof
signal.

### Track B — One-seam refactor
Prefer one of:
- compile / typecheck
- one focused unit or table-driven test
- constructor-only entry test
- mismatch rejection test
- one parity fixture against the old path

### Track C — Staged migration
Prefer:
- legacy decode -> new model tests
- new model -> legacy encode tests when needed
- differential tests against the old implementation
- invalid legacy fixtures for impossible combinations
- parity corpus tests for boundary adapters

## Construction-specific checks

### Product
- build and project each field
- check hidden coupling only if the design claims independence

### Coproduct
- exhaustive handling
- exactly one case for each valid value
- invalid legacy combinations are rejected
- boundary decode is deterministic

### Refined type
- valid values are accepted
- invalid values are rejected
- normalization is idempotent
- raw primitive does not bypass the constructor casually

### Pullback
- checked constructor accepts matching projections
- rejects mismatches
- preserves both original views
- follow-up operations preserve the witness or force reconstruction

### Exponential
- supplied behavior matches old branch results on agreed fixtures
- composition order is explicit when strategies chain
- no branchy fallback silently bypasses the injected behavior

### Free construction
- two interpreters agree where they should
- explanation output lines up with evaluation on the same syntax tree
- old evaluator and new interpreter match on a shared corpus during migration

## Boundary-focused checks

- `decode(encode(x)) == x` when round-trips matter
- one decoder is responsible for invalid legacy shapes
- one encoder or unwrap path is responsible for leaving the domain layer
- persistence and queue payloads are still readable if compatibility is required

## Runtime-only leftovers

When guarantees remain runtime-only, say so and compensate with:

- boundary tests
- differential tests
- golden or parity fixtures
- explicit constructors and adapters

## Tool discovery

Confirm what is already in the repo before naming tools.

Typical baselines:
- Haskell: QuickCheck, Hedgehog
- Go: `testing`, table-driven tests, `testing/quick` if already present
- TypeScript: the current test runner, optionally `fast-check` if already present
- Python: the current test runner, optionally property-based tools only if already present
- Java / Kotlin / C#: the current xUnit-style stack
