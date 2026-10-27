# Defunctionalization

Defunctionalization turns higher-order boundary behavior into first-order IR.

```text
callback / continuation / selector / handler / predicate / builder
  -> constructor carrying captured fields
  -> apply / interpret / project / satisfy
```

Use it when behavior crosses architecture boundaries and must be inspected, serialized, generated, audited, or law-tested.

Do not use it for small local callbacks that do not participate in a boundary.
