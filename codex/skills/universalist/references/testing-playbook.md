# ADD Testing Playbook

## Table of contents
- Law tests (core)
- Property-based testing
- Law discovery
- Model-based testing
- Metamorphic and round-trip checks
- Golden and differential tests
- Tool discovery by language

## Law tests (core)
Every algebra used in the design must have executable laws.
- Monoid: identity + associativity
- Semiring: distributivity + annihilation
- Lattice: commutativity + idempotence
- Functor: identity + composition
- Monad: left/right identity + associativity

## Property-based testing
Use randomized generators to validate laws across large input spaces.
- Keep generators total (no partial constructors).
- Add a shrinker if the framework supports it.
- Prefer small counterexamples to debug laws.

## Law discovery
When you suspect structure but cannot name the laws:
- Use a law-discovery tool (e.g., QuickSpec) to conjecture equations.
- Turn conjectures into property tests.

## Model-based testing
Define a small, trusted model and compare real implementation behavior.
- Useful for state machines and workflows.
- Law: implementation(model(op)) == op(implementation(model))

## Metamorphic and round-trip checks
- Round-trip: decode(encode(x)) == x
- Metamorphic: f(x) and f(g(x)) maintain a relation
- Normalization: normalize(normalize(x)) == normalize(x)

## Golden and differential tests
- Golden: snapshot canonical forms and compare (good for normalizers).
- Differential: compare new algebraic implementation against legacy behavior.

## Tool discovery by language
Always confirm the best tool in the target language and ecosystem.
- First, scan the repo for existing test frameworks; prefer the existing stack.
- If no property-testing tool is present, write deterministic law checks using the current test runner.
- Only introduce new dependencies after explicit user approval.
- Search: "property-based testing <language>"
- Check: standard library, core community libs, CI support
- Prefer: mature, documented, and maintained frameworks

Known baselines (verify in repo context):
- Haskell: QuickCheck, Hedgehog
- Go: testing/quick (stdlib), gopter/rapid (third-party)
- TypeScript: fast-check
