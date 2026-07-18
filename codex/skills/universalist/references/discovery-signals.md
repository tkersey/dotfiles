# Discovery signals

Boundary consideration is itself a discovery signal during implementation and resolution. Trigger when a task creates, changes, preserves, validates, migrates, bypasses, removes, or repairs how values, effects, state, evidence, authority, or behavior cross an owner or representation seam.

Look for these repo smells:

- several booleans/nullable fields encode one lifecycle;
- repeated validation at controllers/services/serializers;
- scattered agreement checks on shared ids or versions;
- branchy policy code that wants supplied behavior;
- syntax mixed with execution, explanation, logging, or serialization;
- duplicated projections/selectors/query views;
- generated artifacts without provenance;
- public contract tests implying hidden internal obligations;
- callbacks, closures, or handlers crossing architecture boundaries;
- an edit is called local even though its dependency, owner, policy, test, or provenance neighborhood is implicit;
- a boundary preserves points/entities but loses the local context that makes them valid;
- multiple local references collapse to one global ID before scope or provenance is recorded;
- dependency edges with different meanings are flattened to unlabelled adjacency;
- a fixture, component, or patch catalog covers examples but cannot reconstruct situated objects canonically;
- context is gathered globally and trimmed rather than compiled as a valid local section around a task point;
- graded or indexed families are combined by ad hoc nested loops over decompositions;
- resource predicates manually enumerate splits or repeat overlap checks;
- static plans/build requests/tool descriptions need execution, cost, dependency, documentation, or audit interpreters;
- pointwise, convolutional, substitutional, and sequential composition are conflated;
- partial composition is totalized with invalid sentinel cases instead of an admissibility kernel;
- two spatial/context dimensions are combined by concatenating neighborhoods rather than composing patch systems;
- collections of rules or interfaces compose through matches without a named composition witness or quotient policy.

Classify each signal by the smallest construction that would make the invariant obvious. If the existing boundary is already exact, record it as preserved and continue without adding abstraction.

For locality signals, first test whether an ordinary labelled graph, dependency index, or context object is sufficient. Escalate to comonadic spatiality only when points, patches, nested neighborhoods, restriction, basis/reconstruction, or continuity laws change code or tests.

For indexed-description signals, first name the index world, tensor/unit or partial composition kernel, and actual description family. Escalate to Day convolution only when all lawful decompositions should contribute and coherent reindexings should be quotiented. Use promonoidal convolution for partial/relation-valued composition. Reject the framing when a pointwise product, operadic substitution, monadic sequence, pullback, pushout, or ordinary product is already exact.
