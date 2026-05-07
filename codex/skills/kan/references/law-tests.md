# Law tests

## Test taxonomy

| Law | Mathematical form | Software approximation |
|---|---|---|
| Unit naturality | `(Lan F)(Kf) · η_c = η_c' · Ff` | old behavior preserved under renamed/embedded morphisms |
| Counit naturality | `Ff · ε_c = ε_c' · (Ran F)(Kf)` | projections commute with old transformations |
| Left factorization | `α = (α#K) · η` | all compatible extensions pass through central adapter |
| Right factorization | `β = ε · (β#K)` | all compatible observations pass through central facade |
| Pointwise colimit | quotient respects source morphisms | normalization/canonicalization test |
| Pointwise limit | family satisfies all equations | coherence/constraint validation test |
| Round trip | restriction after extension preserves intended behavior | migration/golden snapshot tests |

## Minimal `Lan` law test

Given `f : c -> c'` and `x ∈ F(c)`, assert:

```text
lan_map(K(f), eta(c, x)) == eta(c', F(f)(x))
```

## Minimal `Ran` law test

Given `f : c -> c'` and `family ∈ Ran_K F(Kc)`, assert:

```text
F(f)(epsilon(c, family)) == epsilon(c', ran_map(K(f), family))
```

## Factorization test strategy

For `Lan`:

1. Define a sample target semantics `G`.
2. Define `α : F -> G·K`.
3. Implement the induced extension `α#`.
4. Assert `α#(η(x)) == α(x)` for all witness values.
5. Assert no public API bypasses `α#` for old values.

For `Ran`:

1. Define sample observations `β : G·K -> F`.
2. Implement induced view `β# : G -> Ran_K F`.
3. Assert `ε(β#(g)) == β(g)` for all witness values.
4. Assert overlapping observations commute.

## Property-test templates

- Random old AST expression: old interpreter equals new interpreter after `K`.
- Random schema row: old row equals restricted migrated row, modulo documented quotienting.
- Random plugin/exporter: output for core nodes factors through central core semantics.
- Random read-model update: all old queries after projection match legacy query results.
- Random monadic program: direct result equals lowered codensity result.

## Law-test failure interpretation

- Unit naturality failure: old behavior is not preserved by extension.
- Counit naturality failure: old projections are inconsistent.
- Factorization failure: there is an ungoverned implementation path.
- Quotient failure: two paths that should be equal are represented differently.
- Coherence failure: the facade/read model is satisfying local constraints but not global compatibility.
