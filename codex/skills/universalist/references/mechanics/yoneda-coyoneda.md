# Yoneda and Coyoneda

Ordinary observation and deferred-map APIs are useful without these theorems.
Use a structure proof unless the stronger categorical representation is needed.

## Observation preservation versus Yoneda

```text
data Observation = ...
runObservation : Observation -> Subject -> Result
runNew(obs, repack(subject)) == runOld(obs, subject)
```

This law preserves chosen observations. It does not show that those observations
characterize every required distinction. Before quotienting, test stability under
permitted operations and future observations; equal current status can conceal
different legal retries. State any bounded observation domain explicitly.

For the actual Yoneda claim, specify a locally small category `C`, an object `c`,
a functor `F : C -> Set`, and the natural correspondence:

```text
Nat(C(c,-), F) ~= F(c)
eta -> eta_c(id_c)
x   -> (f : c -> d |-> F(f)(x))
```

Establish naturality and that these maps are inverse in the declared setting.
A finite probe list, one runner, or a private constructor does not supply this
argument. See Riehl, [Category Theory in Context, chapter 2](https://emilyriehl.github.io/files/context.pdf).
Full faithfulness or representation-independence claims need their corresponding
hypotheses; do not inherit them from a category-shaped API name.

## Deferred maps versus Coyoneda

```text
data Generated = { payload, path }
lowerGenerated(payload,path) == directInterpret(path,payload)
```

This is an interpretation law. A Coyoneda claim additionally specifies the
index category, variance, functor, and reindexing/coend equivalence. In the
covariant set-valued case, pairs `(x in F(b), f : b -> a)` lower by `F(f)(x)`;
the reindexing relation identifies `(F(h)(x), f)` with `(x, f composed with h)`.
The implementation must realize the required representation and equations,
not merely carry arbitrary provenance metadata. A bounded path vocabulary may
remain an adequate ordinary artifact without claiming the full correspondence.

## With Kan lifts

Use public observations in `C0` and deferred realization paths in `B` when those
are the actual boundaries; defunctionalize an evidenced family when it must be
first-order. Establish any claimed Yoneda, Coyoneda, or Kan property separately.
