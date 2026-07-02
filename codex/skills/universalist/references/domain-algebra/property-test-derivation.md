# Property-test derivation

Every Domain Algebra pass should map at least one meaningful law or non-law to an executable check.

## Property-test plan

```text
Property name:
Carrier generators:
Operation sequence:
Observation function:
Law expected:
Counterexample shape:
Shrinking / minimal witness:
Architecture implication if false:
```

## Positive laws

Positive laws should test preserved structure:

```text
observe(op(identity, x)) == observe(x)
observe(compose(a,b,c)) == observe(compose(a, compose(b,c)))
```

## Non-laws

False laws should have explicit counterexamples. A non-law is often more valuable than a law because it prevents over-general architecture.

```text
refund(capture(p)) != p under audit-trace observation
```

## Skill rule

Do not accept a law merely because the operation names resemble a familiar algebra. Laws are relative to observations, effects, ordering, resources, and public contracts.
