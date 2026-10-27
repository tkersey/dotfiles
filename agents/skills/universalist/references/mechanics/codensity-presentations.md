# Codensity Presentations

Codensity is not only an optimization or continuation encoding. It is also a presentation technology.

## Core pattern

```text
small probe world + density + duality/observations
  -> codensity / right-Kan reconstruction of a large semantic object
```

Use when a monad, effect, or behavior is too semantic, infinitary, probabilistic, topological, completion-like, or observational for a clean algebraic presentation.

## Algebraic vs codensity presentation

Algebraic presentation:

```text
generators + operations + equations -> free syntax / handlers
```

Codensity presentation:

```text
small dense probes + duality/observation bridge -> reconstructed semantics
```

## Data to recover

- Target monad/effect/behavior.
- Direct algebraic presentation attempt.
- Why operations/equations are awkward, infinitary, or not useful.
- Small probe category/world.
- Dense functor/probe map.
- Duality or observation bridge.
- Dualizing object: Bool, 2, Interval, JSON, Trace, Score, PolicyDecision, Expectation, etc.
- Reconstruction as right Kan/codensity.
- Domain-specific theorem/assumption.
- Probe coherence and reconstruction laws.

## Architecture translation

- Compatibility: old client observations densely probe new behavior.
- Agent competence: trace/policy/tool probes present open-ended behavior.
- Probabilistic systems: expectation probes present distributions.
- Distributed systems: finite traces and local observations present protocol behavior.
- Cache/query systems: query probes present semantic cache behavior.

## Guardrail

Canonical codensity presentations may exist but be useless. Prefer simple presentations that reduce proof burden, separate generic categorical structure from domain-specific facts, and produce testable laws.
