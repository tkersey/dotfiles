# Anti-patterns

## “Everything is a Kan extension”

Avoid broad claims. Kan extensions are ubiquitous in theory, but an engineering answer must still name `C`, `D`, `K`, `F`, unit/counit, and a witness.

## “Left means liberal, right means conservative”

This is at most a mnemonic. Always return to the universal property or pointwise colimit/limit formula.

## “Adapters are Kan extensions”

A plain adapter is not automatically a Kan extension. It becomes Kan-shaped only when it satisfies a universal extension or observation property, or when you explicitly use the Kan lens as an engineering analogy.

## “Codensity always speeds things up”

Codensity can improve some bind-heavy workloads but can also add overhead or alter operational behavior. Measure.

## “Type aliases prove laws”

A type alias named `Lan` or `Ran` does not establish naturality, quotienting, coherence, or factorization.

## “Schema migration without path analysis”

Functorial migration depends on paths and equations in the schema category. Ignoring paths usually causes accidental row merges or broken foreign keys.

## “Invisible quotient”

If `Lan` requires quotienting, implement canonicalization or make equivalence explicit. Do not rely on developer memory.

## “Unbounded product”

If `Ran` requires a huge product of observations, design constraint solving, laziness, or partial validation. Do not eagerly enumerate unless finite and small.
