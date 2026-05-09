# Universalist overview

Universalist is an inner lens for codebase refactors where the shape of truth should change.

Default discipline:

```text
one signal -> one seam -> one smallest honest construction -> one proof signal
```

Use the construction ladder before reaching for advanced machinery:

1. product;
2. coproduct;
3. refined type / equalizer;
4. pullback witness;
5. exponential / function object;
6. free construction / initial algebra;
7. canonical boundary artifact.

The skill should prefer plain engineering language. Category words are useful only when they select code shape, tests, migration strategy, or a boundary artifact.

Track D exists for boundary artifacts. It does not replace the ladder; it is reached only when the smell lives at an architectural boundary.
