# Invariant Review Lens

Independently try to falsify the carrier and transition invariants of the exact
bound candidate.

Probe:

```text
whether the invalid family can inhabit admitted state
whether legal constructors preserve closure
whether transitions and composition preserve the law
whether identity, generation, custody, ordering, or recovery break closure
whether finite cases or declared sibling dimensions are missing
```

Return `clean` or `findings` with a concrete witness and affected invariant. Do
not propose member-specific guards or grant mutation.
