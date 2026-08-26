# Invariant Review Lens

Independently try to falsify the carrier and transition invariants of the exact
bound candidate.

Probe:

```text
whether required-valid behavior overlaps the claimed invalid family
whether the invalid family can inhabit admitted state
whether the chosen invariant locus is the strongest honest one
whether transient invalidity can escape an encapsulated transition
whether admitted aliases violate canonical identity or explicit congruence
whether legal constructors preserve closure
whether transitions and composition preserve the law
whether every producer-to-consumer path intersects the canonical cut
whether producer migration changes accepted identity, ordering, custody, error,
  serialization, or composition semantics
whether identity, generation, custody, ordering, or recovery break closure
whether finite cases or declared sibling dimensions are missing
```

Return `clean` or `findings` with a concrete witness and affected invariant. Do
not propose member-specific guards or grant mutation.
