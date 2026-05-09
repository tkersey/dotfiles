# Framework boundaries

Structural refactors should respect framework seams.

Good landing spots:

- request decoder / DTO parser;
- controller or handler boundary;
- command factory;
- ORM mapper or repository adapter;
- serializer/deserializer;
- projection/read-model layer;
- plugin registry boundary;
- policy/rule dispatch boundary;
- test harness or contract verification boundary.

For public API, storage, queue, or wire formats, keep the external shape stable behind adapters unless the user explicitly asks for a breaking change.

For lift-shaped refactors, identify the projection function `P` concretely: controller response, serializer, trace emitter, report extractor, view builder, or test observation harness.
