# Composition Certificate Elaboration for Kan

`kan` should elaborate Composition Certificates, not replace them. A certificate is the architectural unit; Kan mechanics explain why its artifact is `Lan`, `Ran`, `Delta`, `Lft`, `Rft`, Yoneda, Coyoneda, defunctionalized IR, free builder, or obstruction.

## Mapping

| Certificate field | Kan elaboration |
| --- | --- |
| Worlds | categories, posets, schemas, syntactic worlds, behavior worlds, indexed families |
| Boundary | `K : C -> D`, `P : B -> C`, interpreter, handler, serializer, observer |
| Unknown location | after boundary / before boundary / observation / generation / control-flow |
| Artifact | Kan extension, Kan lift, precomposition, Yoneda, Coyoneda, codensity, explicit IR, Freyd builder |
| Interpreter/projection | unit, counit, comparison cell, handler, `runObservation`, `lowerGenerated`, `apply` |
| Law witness | naturality, factorization, projection, lowering, observation, handler, defunctionalization equivalence |
| Falsifier | no required limit/colimit, lossy projection, incoherent observations, invalid generated path, missing IR case |

## Elaboration modes

### Extension certificate

Use when the unknown is after `K : C -> D`.

- `Lan_K F` for free/generative transported semantics.
- `Ran_K F` for coherent observations.
- `Delta_K` for restriction.

### Lift certificate

Use when the unknown is before `P : B -> C`.

- `Lft_P F` for realization.
- `Rft_P F` for residual obligation.
- Freyd/AFT diagnostic for possible `Free : C -> B`.

### Representation certificate

Use when the artifact is local to a boundary value.

- Yoneda for observations.
- Coyoneda for raw payload plus deferred path.
- Defunctionalization for explicit first-order IR.

## Output requirement

Every Kan elaboration should end with certificate status:

```text
verified / obstructed / approximate / planned / primitive exception
```
