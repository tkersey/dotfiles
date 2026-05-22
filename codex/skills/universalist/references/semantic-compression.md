# Semantic Compression

Semantic compression is the practice of presenting a large behavioral world by a smaller dense world of probes, observations, finite cases, or approximants.

## Use when

- the direct semantic object is too large or high-dimensional;
- algebraic syntax is too weak, too operational, or too infinitary;
- public behavior can be certified by a meaningful probe family;
- the codebase needs a small testable representation of a large semantics.

## Pattern

```text
Large behavior:
  full system semantics

Small probes:
  observations / traces / finite tests / policy cases / expectations

Reconstruction:
  coherent probe family -> semantic artifact or accepted approximation

Law:
  reconstruction agrees with required observations

Falsifier:
  missing probe or incoherent probe family breaks reconstruction
```

## Agentic systems

Agent behavior is often not well presented only by operations. Use algebraic syntax for actions, but use dense probes for competence, safety, policy, memory, trace quality, and tool correctness.
