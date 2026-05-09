# Yoneda, Coyoneda, and Defunctionalization for Universalist

These are representation lenses for Track D.

## Yoneda lens: observation vocabulary

Use when duplicated selectors, projections, reports, or policy checks are the smell.

Code shape:

```text
data Observation = ...
runObservation : Observation -> Subject -> Result
```

Proof signal:

```text
runObservation(obs, repack(subject)) == runObservation(obs, subject)
```

Plain-language reading: make sanctioned observations first-class.

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

Plain-language reading: carry the raw payload and the deferred path until the boundary lowers it.

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

Plain-language reading: replace anonymous behavior with named cases and one interpreter.

## Combined pattern

For a lifted-implementation boundary:

- Yoneda side: public observations.
- Coyoneda side: candidate implementation payload plus projection path.
- Defunctionalization: observations and paths become first-order constructors.
- Freyd/AFT side: ask whether the projection supports a canonical builder or exposes an obstruction.

Proof signal:

```text
runObservation(obs, project(lowerGenerated(realizer))) == expected(case, obs)
```
