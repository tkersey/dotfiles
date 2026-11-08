# Defunctionalization

Defunctionalization represents higher-order behavior with first-order data and an interpreter.

```text
callback / continuation / selector / handler / predicate / builder
  -> constructor carrying captured fields
  -> apply / interpret / project / satisfy
```

Investigate this correspondence in local algorithms as well as at architecture boundaries. Identify the function family, captured environments, constructors, and interpreter, and establish evaluation preservation for the claimed domain.

Introducing the representation needs a material benefit such as inspection, serialization, analysis, or optimization. Recognizing an existing defunctionalized implementation needs no further redesign.
