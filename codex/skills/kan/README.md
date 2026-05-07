# Kan skill bundle

`kan` is a Codex/Agent Skills bundle for implementing Kan extensions and using them as an architecture calculus.

It covers left and right Kan extensions, pointwise formulas, ends/coends, density/codensity, finite-category algorithms, Haskell/TypeScript/Rust/Python implementation patterns, functorial data migration, DSL/interpreter and plugin architecture, law tests, failure modes, and source ledgers.

## Installation

For repo-local Codex use, copy this folder to:

```text
.agents/skills/kan
```

For user-level use, copy it to:

```text
$HOME/.agents/skills/kan
```

For API upload, zip the top-level folder:

```bash
cd /path/to/parent
zip -r kan.zip kan
```

## Validation

```bash
cd kan
./scripts/check_skill.sh
```

## Useful entry points

```bash
./scripts/emit_kan_stub.sh plugin-api typescript
./scripts/emit_kan_stub.sh finite-lan python
./scripts/emit_witness_pack.sh codensity haskell
./scripts/emit_law_test_plan.sh lan agnostic
./scripts/emit_source_pack.sh foundations pointwise
```

## Design stance

The skill treats Kan extensions as a design calculus, not as a decoration layer. It asks for `C`, `D`, `K`, `F`, `Lan`/`Ran`, unit/counit, and a witness object before recommending code.
