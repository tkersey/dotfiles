# Yoneda, Coyoneda, and Defunctionalization for Universalist

These are representation lenses for Track D.

## Observation vocabulary; Yoneda only with its additional hypotheses

Use when duplicated selectors, projections, reports, or policy checks are the smell.

Code shape:

```text
data Observation = ...
runObservation : Observation -> Subject -> Result
```

Proof signal:

```text
runNew(obs, repack(subject)) == runOld(obs, subject)
```

Plain-language reading: make sanctioned observations first-class. This is a
structure/preservation claim, not automatically Yoneda. Before identifying states,
show that the observation equivalence survives every required permitted continuation;
current projections alone can hide different retry, failure, or authority behavior.
See the counterexample in `effects-and-coalgebras.md` and the exact Yoneda claim
in `mechanics/yoneda-coyoneda.md`. Do not require that theorem when an ordinary
observation API suffices.

## Coyoneda lens: deferred generation path

Use when generated artifacts lose provenance or maps happen too early.

Code shape:

```text
data GenerationPath = ...
data Generated = { payload, path }
lowerGenerated : Generated -> Target
```

Proof signal:

```text
lowerGenerated({ payload, path }) == directInterpret(path, payload)
```

Plain-language reading: carry the raw payload and the deferred path until the
boundary lowers it. A payload/path record alone is not a Coyoneda theorem witness.
Keep effect ordering and required provenance observable; do not quotient a path
merely because its final payload happens to match. Use the mechanics reference
only when the stronger functorial/coend representation matters.

## Defunctionalization lens: explicit IR

Use when higher-order behavior crosses the boundary.

Code shape:

```text
data Case = ...captured fields...
apply : Case -> Input -> Output
```

Proof signal:

```text
apply(encode(oldFunction), input) == oldFunction(input)
```

Plain-language reading: replace anonymous behavior with named cases and one
interpreter for the evidenced family. `encode` covers that family, not arbitrary
runtime functions. Preserve captured environments, required effects, and partiality;
unsupported cases fail explicitly rather than inventing a total encoding.

## Combined pattern

For a lifted-implementation boundary:

- Observation side: public observations, without an unearned Yoneda claim.
- Generation side: candidate payload plus projection path, without an unearned Coyoneda claim.
- Defunctionalization: observations and paths become first-order constructors.

Proof signal:

```text
runObservation(obs, project(lowerGenerated(realizer))) == expected(case, obs)
```
