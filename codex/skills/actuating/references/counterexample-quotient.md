# Counterexample Quotient

A raw validation matrix can become another accumulation engine.

Prefer:

```text
raw combinations
-> observations
-> equivalence under one invariant/owner/route
-> representative counterexample class
-> one proof law
```

## Equivalence test

Rows may be grouped when they share:

```text
same accepted observation
same canonical owner
same invalid-state mechanism
same repair route
same proof obligation
```

Keep rows separate when an accepted observation distinguishes them or their owners/cleanup/proof differ.

## Class shape

```yaml
counterexample_class:
  class_id:
  governing_invariant:
  canonical_owner:
  representative_witness:
  covered_combinations: []
  excluded_combinations: []
  route:
  proof_obligation:
  falsifier:
  status:
```

## Stop rule

If a new counterexample does not fit an existing class:

```text
stop realization
return to frontier
add/revise class
reselect route
```

Do not append another local branch and claim the original class was still complete.
