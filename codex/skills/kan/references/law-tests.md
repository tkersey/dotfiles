# Law Tests

| Artifact | Law |
| --- | --- |
| `Lan` | `lan_map(K(f), eta(c,x)) == eta(c',F(f)(x))` |
| `Ran` | `F(f)(epsilon(c,family)) == epsilon(c',ran_map(K(f),family))` |
| `Delta` | old golden tests pass through restriction |
| Lift | `project(realize(case)) == required(case)` |
| Residual | missing obligation fails; satisfying obligations passes |
| Freyd builder | `P(Free(required(case)))` satisfies required behavior |
| Yoneda | representation change preserves observations |
| Coyoneda | lowering equals direct interpretation |
| Defunctionalization | `apply(encodedCase,x) == oldFunction(x)` |
| Handler | production/test handlers satisfy same declared observations |
| Coalgebra | traces/unfolds satisfy observations |


## Codensity presentation laws

Probe coherence:

```text
compatible probes agree on overlaps
```

Density / coverage law:

```text
required observations factor through the probe family
```

Reconstruction law:

```text
reconstruct(coherentProbes(subject)) agrees with target behavior on observations
```

Falsifier:

```text
there exists required behavior not captured by probes, or a domain-specific representation assumption fails
```
