# Roadmap for using the skill

## Level 0: identify the boundary

- What is old/core/specified?
- What is new/ambient/extended?
- What maps old into new?
- What behavior must be preserved?

Output: `C`, `D`, `K`, `F` draft.

## Level 1: choose direction

- Need generation/free completion? Try `Lan`.
- Need coherent observations/compatibility? Try `Ran`.
- Need old view of new thing? Try `K*`/`Δ`.

Output: direction plus unit/counit.

## Level 2: build witness

Pick one `d ∈ D` and compute/approximate:

- `K ↓ d` for `Lan`, or
- `d ↓ K` for `Ran`.

Output: a concrete module, adapter, row, endpoint, AST node, or plugin.

## Level 3: implement laws

Start with:

- unit/counit naturality;
- one factorization test;
- one failure-mode regression.

Output: test files or test plan.

## Level 4: scale

- Replace toy finite computation with generated code, database query, typeclass, trait, or runtime adapter.
- Add source ledger and architecture decision record.
- Benchmark if optimization is involved.

Sources: `[KAN-RIEHL-CTIC]`, `[KAN-HINZE-2012]`, `[KAN-MACLANE-CWM]`.
