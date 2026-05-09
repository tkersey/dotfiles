# Sources and source discipline

This skill is primarily operational. It uses category-theory vocabulary only when it selects a code artifact and proof signal.

Safe source claims:

- Products, coproducts, equalizers, pullbacks, exponentials, free constructions, adjunctions, Kan extensions, Kan lifts, Yoneda/Coyoneda, and defunctionalization are stable theory/program-transformation vocabulary.
- Freyd's adjoint functor theorem can be used as an existence/diagnostic intuition for when a well-behaved projection/forgetful functor admits a free builder.

Unsafe source use:

- Claiming a codebase literally satisfies a theorem without explicit categories, functors, and universal properties.
- Using Freyd/AFT as proof that an implementation exists without a concrete projection, templates, and tests.

Operational source discipline:

- Label advanced material as an engineering interpretation unless formalized.
- Prefer law/proof signals and negative fixtures over theorem-name authority.
- Hand off to `kan` for detailed theorem mechanics.
