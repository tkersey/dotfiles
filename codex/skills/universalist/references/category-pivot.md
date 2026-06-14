# Category Pivot / Easy-World Transfer

## Core idea

Universal Architecture should not force every hard operation to remain in the ordinary executable-program world. That world is expressive, but it often hides structure inside functions, callbacks, services, mutable state, prompts, and runtime effects.

Use a **Category Pivot** when another world makes the hard part explicit:

```text
current world -> easy world -> certified interpretation back
```

Slogan:

```text
Do not force a problem to stay in Hask when syntax, semantics, posets, relations, coalgebras, schemas, resources, or presheaves make the structure explicit.
```

Here `Hask` means the ordinary executable-program world of computer science, not literal Haskell.

## Common pivots

| Current hard world | Easy world | What becomes easier |
|---|---|---|
| opaque functions / callbacks | syntax / IR | inspect, serialize, replay, validate, authorize, totalize |
| branchy runtime policy | poset / lattice | joins, meets, weakest obligations, capability envelopes |
| mutable state transitions | coalgebra / trace world | protocol observations, trace laws, bisimulation-style checks |
| raw text / retrieved chunks | schema-shaped context instance | provenance, constraints, missingness, contradiction, freshness |
| local call-site meanings | presheaf / usage site | overlap checks, gluing, sheafification |
| resource/permission logic | resource category / separation model | ownership, disjointness, capability transfer |
| partial/nondeterministic specs | relation / profunctor world | backward reasoning, compatibility, bidirectional views |
| generated outputs | Coyoneda-like payload + path | provenance and lowering laws |

## Track H protocol

1. Name the current world.
2. Name the hard operation.
3. Name the easy world.
4. Explain what becomes easy there.
5. Define the transfer/encoding into the easy world.
6. Define the interpretation/transport back.
7. State what is forgotten, approximated, or intentionally made syntax.
8. Add a preservation law.
9. Add a falsifier.

## Certificate fields

Use `templates/category-pivot-certificate.md` when the pivot is significant enough to guide code.

## Guardrail

Do not pivot categories merely to sound profound. A pivot is justified only when it changes code shape, test shape, proof obligation, or the set of possible states/actions/observations.
