# Framework boundaries

Before refactoring, locate framework-owned shapes:

- HTTP request/response DTOs;
- ORM rows/entities;
- JSON serializers/deserializers;
- message bus payloads;
- CLI argument parsers;
- UI component props/state;
- test fixtures and snapshot shapes.

Prefer adapter-first staging. Keep wire/storage shapes stable while introducing a stronger internal model unless the user explicitly wants a breaking change.
