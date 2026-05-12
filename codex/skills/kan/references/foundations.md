# Foundations

## Kan extensions

A left Kan extension of `F : C -> E` along `K : C -> D` is `Lan_K F : D -> E` with unit:

```text
η : F -> Lan_K F · K
```

It is initial among extensions compatible with `F`.

A right Kan extension is `Ran_K F : D -> E` with counit:

```text
ε : Ran_K F · K -> F
```

It is terminal among coherent observation-like extensions.

When both exist:

```text
Lan_K ⊣ K* ⊣ Ran_K
```

where `K*` is precomposition.

## Pointwise intuition

```text
Lan_K F(d) = generated pieces from arrows Kc -> d, quotiented by source equations
Ran_K F(d) = coherent families over observations d -> Kc
```

## Kan lifts

Given `P : B -> C0` and `F : A -> C0`, a lift solves for an `A -> B` behind `P`.

```text
A --?--> B
|        |
F        P
v        v
C0
```

Use `Lft_P F` for realization and `Rft_P F` for residual/sound obligation, with the comparison direction named explicitly.

## Yoneda/Coyoneda

Yoneda: represent a subject by sanctioned observations.

Coyoneda: represent generated artifacts by raw payload plus deferred path.

## Defunctionalization

Replace function-like boundary artifacts with first-order constructors plus an interpreter/apply/project function.
