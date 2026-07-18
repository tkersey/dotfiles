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
- graded/indexed families use manual nested loops over decompositions;
- pointwise, convolutional, substitutional, and monadic products are mixed under one generic `combine`;
- the same local validator, observer, update, or relation is reimplemented under tenant, evidence, capability, policy, audit, or environment wrappers;
- source and target representations receive different context wrappers but the difference is hidden in adapters;
- accessors repeatedly decompose a whole into focus plus residual, update the focus, and rebuild the whole;
- code generates every legal wrapper/frame around one local capability by hand;
- a relation/specification is treated as if it were a concrete implementation map;
- context changes a type/state/schema/capability index but is erased into dynamic tags;
- a Reader parameter, `Context<T>`, middleware stack, or DI container is described as a Tambara module without an action or framing laws.

Classify each signal by the smallest construction that would make the invariant obvious. If the existing boundary is already exact, record it as preserved and continue without adding abstraction.

For locality signals, first test whether an ordinary labelled graph, dependency index, or context object is sufficient. Escalate to comonadic spatiality only when points, patches, nested neighborhoods, restriction, basis/reconstruction, or continuity laws change code or tests.

For indexed-description signals, first test an ordinary or pointwise product. Escalate to Day/promonoidal mechanics only when a real index tensor/kernel, decomposition, quotient, and interpreter change the artifact.

For context-framing signals, first test a plain function/profunctor, Reader/environment parameter, adapter, or explicit residual record. Escalate to Tambara mechanics only when a real ambient context action on both endpoint worlds, a profunctorial capability, unit/associativity/naturality/coherence, and an effective frame representation change code or tests.
