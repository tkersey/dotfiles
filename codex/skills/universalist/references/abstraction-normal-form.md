# Abstraction Normal Form

A codebase is in Abstraction Normal Form when every architecture-level abstraction behaves like a sheaf over its intended usage site.

That means:

- local uses agree on overlaps;
- compatible local uses glue to a global meaning;
- global meaning is unique up to intended equivalence;
- impossible global states are unrepresentable or rejected;
- missing valid states are represented by extension points or obligation artifacts;
- redundant meanings normalize to one canonical form;
- bypasses are removed or certified as primitive exceptions.

## Relationship to other normal forms

- Boundary Normal Form certifies cross-world composition boundaries.
- Context Normal Form certifies semantic-consumption context.
- Abstraction Normal Form certifies architecture-level abstractions and their possibility envelopes.

## Audit targets

Look for:

- stringly typed protocols;
- nullable/optional-field state machines;
- `any`/`dict`/untyped payloads carrying domain truth;
- duplicated status/state encodings;
- callback registries hiding operation syntax;
- DTOs whose local meanings diverge by consumer;
- tests that imply an abstraction missing from code;
- generated artifacts with multiple encodings of the same meaning;
- raw context objects consumed as semantic context.
