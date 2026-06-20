---
name: simplify-and-refactor-code-isomorphically
description: >-
  Run a proof-heavy simplification campaign that factors code, classifies duplication,
  quotients proven-equivalent distinctions, ablates redundant surface, and normalizes the
  survivors. Use when simplification must preserve a declared observation set or exact
  structure. This skill treats isomorphism as an optional strict preservation relation,
  not as the reduction objective. Route intentional contractions of obsolete, invalid,
  or legacy behavior to `reduce` or `resolve` under a refinement-preserving contract.
---

# Simplify and Refactor Code Isomorphically

## Mission

Shrink and unify code under an explicit preservation relation.

```text
FACTORING
-> QUOTIENTING
-> ABLATIVE
-> NORMALIZING
```

The reduction operators decide what disappears. The preservation relation decides what must remain.

## Preservation relations

Choose before editing:

- `isomorphic`: reversible structure-preserving correspondence.
- `observationally-equivalent`: all declared external observations remain equal.
- `refinement-preserving`: all required behavior remains while invalid, obsolete, duplicated, or unrequired behavior may disappear.
- `intentional-contract-change`: approved behavior change.

Default this skill to `observationally-equivalent`. Use `isomorphic` only when reversible structure matters. If the goal intentionally contracts behavior, route to `reduce` or `resolve`.

## One rule

```text
Select the reduction candidate.
Declare the preservation relation.
Prove it.
Then remove surface.
```

No proof -> no reduction.

## Mandatory loop

```text
1. BASELINE    -> tests, typecheck/lints, representative observations, surface snapshot
2. FACTOR      -> obligations, owners, callsites, state/effect factors
3. CLASSIFY    -> clone type, live obligation, dominance, risk
4. QUOTIENT    -> equivalence relation and congruence checks
5. PROVE       -> preservation card before editing
6. ABLATE      -> one certified lever per patch group
7. NORMALIZE   -> canonical owner/representation/path
8. VERIFY      -> declared observations, tests, types, lints, surface delta
9. RECOMPOSE   -> prove every live obligation remains covered
10. LEDGER     -> RC-v1 and rejection log
11. REPEAT     -> rescan only if new candidates appear
```

Each phase must leave an artifact. A “cleaner” claim without evidence is not a simplification result.

## Preflight

Before editing:

- baseline relevant tests;
- capture representative outputs/observations;
- snapshot types/lints and surface;
- map callsites and owners;
- choose one reduction lever;
- state rollback;
- state the preservation relation.

Do not require bit-identical output when the declared contract is weaker. Do not claim equivalence outside the declared observation set.

## Duplication classification

Use exactly one:

- `exact-clone`
- `parametric-clone`
- `gapped-clone`
- `semantic-clone`
- `accidental-rhyme`

Rules:

- Exact and parametric clones are quotient candidates.
- Gapped clones require bounded variance and congruence checks.
- Semantic clones require explicit observational equivalence proof.
- Accidental rhymes must not be merged.

## Abstraction ladder

```text
0 copy-paste
1 local function
2 parameterized function
3 enum/strategy over bounded variance
4 interface/trait for open implementors
5 generic abstraction
6 DSL/macro
```

Do not skip rungs. One case is unique; two may be coincidence; three may be a pattern. One axis of variance per rung. If variance exceeds shape, keep the factors separate.

## Candidate score

```text
Reduction Score =
  (semantic_surface_removed × confidence × ownership_clarity)
  / risk
```

Do not chase reductions whose coupling or proof cost exceeds the removed surface.

## Preservation Card

```yaml
preservation_card:
  candidate_id: "..."
  reduction_operator: factor | quotient | ablate | normalize
  preservation_relation: isomorphic | observationally-equivalent
  inputs_and_callsites: []
  observation_set: []
  ordering_preserved:
  tie_breaking_preserved:
  error_semantics_preserved:
  laziness_and_short_circuit_preserved:
  floating_point_rng_hash_order_preserved:
  side_effect_order_and_payload_preserved:
  type_narrowing_preserved:
  UI_rerender_or_lifecycle_preserved:
  quotient_congruence_checks: []
  proof_commands: []
  status: pass | validate-first | fail | blocked
```

For non-applicable axes, say `not-applicable`; do not silently omit material axes.

## Reduction Certificate

Every implemented patch group emits `RC-v1` from [reduction-certificate.md](references/reduction-certificate.md).

Required:

- every factor has a live obligation or removal disposition;
- every retained distinction has a witness;
- quotient classes are congruent;
- every removed factor is accounted for;
- recomposition covers every live obligation;
- no orphan surface remains.

## Common candidates

- pass-through wrappers and adapters;
- orphan `_v2`, `_new`, `_old`, or `_improved` surfaces;
- dead flags, imports, mocks, exports, and compatibility paths;
- duplicate truth owners;
- repeated branch structure;
- wrapper chains and re-export webs;
- boilerplate whose replacement has matching semantics;
- abstraction rungs that exceeded evidence.

## One lever per patch group

Examples:

```text
delete dead branch
collapse wrapper chain
quotient duplicate state variants
canonicalize one owner
retire flag
replace repeated boilerplate
```

Do not combine unrelated reductions unless they are one factorization/recomposition move.

## Verification

Run:

- declared observation checks;
- relevant tests;
- typecheck/lints;
- surface delta;
- recomposition audit.

A green test suite alone does not prove isomorphism or observational equivalence.

## Handoff boundary

Route to:

- `complexity-mitigator` for read-only local comprehension;
- `reduce` for broad architectural winnowing or refinement-preserving contraction;
- `review-compression-compiler` / `resolve` for behavioral quotienting driven by review observations;
- `fixed-point-driver` to realize an already-certified normal form;
- `universalist` when reduction reveals missing essential structure.

## Output

End with:

```text
Reduction Bottom Line:
- factors:
- quotient:
- ablation:
- normal form:
- preservation relation:
- proof:
- recomposition:
- surface delta:
- next:
```

## Resources

- [reduction-certificate.md](references/reduction-certificate.md)
