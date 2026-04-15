# Cost Model and False Positives

## Default rule

Choose the smallest construction that:

- removes the most repeated obligation
- lands in one seam
- has a clear proof signal
- preserves boundaries when possible

Elegance is not a reason to choose a larger construction.

## Blast-radius checklist

Score each candidate move as **low**, **medium**, or **high** on:

- file count touched
- public API impact
- serializer or wire impact
- persistence impact
- testability
- rollback difficulty

Prefer low-to-medium blast radius unless the user explicitly asked for a broader redesign.

## Construction-specific cost profile

| Construction | Usual cost | Main risk | Best first seam |
| --- | --- | --- | --- |
| Product | low | hiding illegal combinations in a record | constructor or value object |
| Coproduct | medium | touching many exhaustiveness sites too early | decoder + one central state consumer |
| Refined type | low to medium | raw primitive leaks everywhere | parse / factory boundary |
| Pullback | low | witness is bypassed by public fields or constructors | checked constructor |
| Exponential | low to medium | injected behavior still depends on hidden mutable global state | policy or handler seam |
| Free construction | medium to high | AST added without enough interpreter value | one rule or workflow family |

## False-positive guide

### Product mistaken for coproduct
If fields are independently meaningful and legal together, keep a product.

### Coproduct mistaken for product
If optional fields are really mutually exclusive states, use a coproduct.

### Refined type mistaken for helper validation
If the same stable predicate appears repeatedly, move it into a constructor or wrapper.

### Pullback mistaken for pair
If agreement over a shared projection is the main invariant and appears in multiple call sites, create a witness.

### Exponential mistaken for state machine
If the core problem is "which behavior should run" rather than "which state am I in", prefer supplied behavior.

### Free construction mistaken for object hierarchy
If syntax and execution are intertwined and multiple interpreters matter, use an AST. If there is only one evaluator and no explanation or translation path, do not.

## Stop conditions

Stop after any of these:

- one seam is stronger and verified
- external shape is still stable and adapters are explicit
- the repeated proof obligation is now centralized
- the next step would materially widen blast radius

## Escalation triggers

Consider a second seam only when:

- the first seam proved the shape and the repo still benefits
- boundary adapters are already explicit
- the next seam uses the same construction
- rollback remains easy
