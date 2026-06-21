# Composition Geometry Selector

Universal Architecture must select not only *what artifact exists*, but *how compositions are allowed to form*. Use the weakest structure that makes legal assembly and sequencing explicit.

| Pressure | Structure | What becomes explicit |
| --- | --- | --- |
| sequential transformations | category | identities and sequential composition |
| independent context / lawful parallelism | monoidal category | side-by-side composition and interchange |
| pure values + ordered call-by-value effects | Freyd/premonoidal category | pure embedding, centrality, evaluation order |
| typed many-input one-output hierarchy | colored operad | ports, operations, substitution, nested assembly |
| genuine many-input many-output networks | PROP/properad | network composition without product bundling |
| feedback and cyclic behavior | traced monoidal / temporal wiring / coalgebra | feedback, state, traces, ongoing interaction |
| consumable or graded resources | linear/graded/resource-sensitive category | ownership, duplication, cost, capability use |

## Selection discipline

Use ordinary categories first. Add monoidal structure only when side-by-side composition is real. Use a Freyd category when effects invalidate interchange. Use an operad when wiring itself is domain syntax. Escalate to PROPs/properads only when multiple outputs matter structurally, and to traced/coalgebraic structure only when feedback is essential.

Do not grant symmetry, commutation, duplication, discard, feedback, or parallelism for free. Each is an architectural law with a witness.

## Core law shapes

```text
Operadic substitution:
interpret(substitute(f,g1,...,gn))
  == compose(interpret(f), interpret(g1), ..., interpret(gn))

Freyd effect order:
J(id) = id
J(g . f) = J(g) . J(f)
reorder(m,n) is legal only when observe(m;n) == observe(n;m)
```

## Anti-overreach

Use a plain function/interface when it already captures the exact composition. An operad or Freyd model is justified only when it changes legal wiring, sequencing, tests, ownership, static validation, simulation, or interpretation.
