# Common soundness doctrine

This suite treats code and claims as untrusted until witnessed.

## The high-value questions

### Witness

What concrete artifact witnesses the claim?

Prefer direct witnesses:

- direct tests
- exhaustive handling
- constructor / eliminator discipline
- boundary refinement
- explicit guards with bounded failure modes
- no-code proof that the current owner already enforces the contract

A witness is not just "some green signal". It must match the claim.

### Preservation

What must still be true after each step?

Look across:

- transformations
- retries
- rollbacks
- persistence hops
- cache round-trips
- serialization / normalization passes
- API boundary crossings

If a guarantee holds only at entry, preservation is incomplete.

### Progress

Can execution always take a legal next step?

Look for stuck states:

- partial initialization
- sentinel states
- ambiguous defaults
- swallowed errors
- impossible-but-representable values
- recovery paths with no legal continuation

### Totality

Where a case split matters, are all cases visible and forced?

Make partiality explicit when it cannot be removed.

### Refinement

Push raw-to-validated narrowing toward the boundary.

Separate raw, normalized, and validated states when correctness depends on that distinction.

### Inhabitance

Ask which illegal states are still inhabitable.

When practical, make them uninhabitable by construction. When not practical, make them explicit and forced to handle.

## Strong doctrine words

These words steer models well because each carries an obligation:

- `untrusted-until-witnessed`
- `witness-bearing`
- `preservation`
- `progress`
- `total`
- `refinement-first`
- `inhabitation-aware`
- `canonical`
- `surface-accounted`

## Engineering translation

A material soundness gap exists when one or more of these is true:

- a material claim has no concrete witness
- the witness is stale, partial, or contradictory
- a critical guarantee is not preserved through the full path
- execution can get stuck in a partial or impossible state
- a critical case split is partial in a hidden way
- raw values leak past the boundary that was supposed to refine them
- duplicate owners disagree or require caller-side repair
