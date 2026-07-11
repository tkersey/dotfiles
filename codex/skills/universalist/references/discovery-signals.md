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
- callbacks, closures, or handlers crossing architecture boundaries.

Classify each signal by the smallest construction that would make the invariant obvious. If the existing boundary is already exact, record it as preserved and continue without adding abstraction.
