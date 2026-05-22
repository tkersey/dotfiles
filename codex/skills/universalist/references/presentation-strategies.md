# Presentation Strategies

A canonical boundary artifact is not complete until its presentation strategy is clear.

## Modes

### Algebraic presentation

Use generators, operations, equations, free syntax, effect signatures, and handlers.

Use when:

- behavior is operational or command-like;
- constructors are finite and understandable;
- interpreters/handlers are natural;
- the artifact is an AST, workflow, effect language, or command DSL.

Proof signals:

- interpreter parity;
- handler agreement;
- equations respected;
- missing constructor fails exhaustiveness.

### Codensity / dense-dual presentation

Use a small dense world of probes plus a dual/observational bridge and reconstruction.

Use when:

- behavior is semantic, infinitary, probabilistic, topological, observational, or completion-like;
- generators/equations are awkward or infinitary;
- a small family of probes determines the large behavior;
- a representation theorem or domain assumption supports reconstruction.

Proof signals:

- probe coverage;
- probe coherence;
- reconstruction agrees with direct semantics on witnesses;
- missing probe or failed representation theorem gives falsifier.

### Mixed presentation

Use algebraic syntax for operations and dense probes for semantic competence or safety. Agentic systems often need this:

```text
Agent syntax = algebraic presentation.
Agent competence/safety = dense probe presentation.
Runtime = handlers + coalgebra.
```

### Primitive presentation

Use when the boundary is intentionally treated as an external primitive effect and contained by handlers/observations.

## Rule

Do not accept a universal artifact merely because a canonical construction exists. Prefer a simple, testable presentation that reduces proof burden and separates generic mechanics from domain-specific assumptions.
