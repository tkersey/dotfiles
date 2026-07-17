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
- context is gathered globally and trimmed rather than compiled as a valid local section around a task point.

Classify each signal by the smallest construction that would make the invariant obvious. If the existing boundary is already exact, record it as preserved and continue without adding abstraction.

For locality signals, first test whether an ordinary labelled graph, dependency index, or context object is sufficient. Escalate to comonadic spatiality only when points, patches, nested neighborhoods, restriction, basis/reconstruction, or continuity laws change code or tests.