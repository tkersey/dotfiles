# Syntax / semantics mechanics

Use when behavior should be manipulated as explicit syntax and interpreted into observed semantics.

## Mechanics

```text
Syntax S
Interpreter I : S -> Semantics
Observations O : Semantics -> Obs
Law: O(I(transform(s))) == expected observation
```

## Design checklist

- constructors / formation rules;
- invalid syntax cases;
- interpreter/handler ownership;
- totality table over constructors;
- semantic observations;
- soundness law;
- adequacy/completeness law;
- falsifier.

## Agentic examples

- `ToolOperation` syntax interpreted by tool handlers into traces;
- `Plan` syntax interpreted into execution traces;
- `PolicyRule` syntax interpreted into decisions;
- `ContextSchema` syntax interpreted/rendered into decision packets;
- `PatchIntent` syntax interpreted into verification obligations.
