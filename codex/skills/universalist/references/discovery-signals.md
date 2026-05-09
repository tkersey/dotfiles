# Discovery signals

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
- observable/public behavior fixed while internals are underdetermined;
- a projection, serializer, or report loses evidence required by public behavior.

Classify each signal by the smallest construction that would make the invariant obvious.
