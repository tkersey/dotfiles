---
name: algebra-driven-design
description: "Apply Algebra-Driven Design. Use for ADD, denotational design, combinator models, law-driven architecture, domain algebra, property tests, codebase modeling, event sourcing, workflow design, or agentic skill design. If the canonical bundle is unavailable, use this wrapper as the minimal ADD kernel and report the missing bundle path."
---

# Algebra-Driven Design Loader

This loadable skill wrapper exists so local Codex skill discovery can find `algebra-driven-design` under `codex/skills/`.

## Canonical bundle resolution

Before using the full skill, try to read the canonical bundle from one of these locations, in order:

```text
codex/algebra-driven-design/SKILL.md
codex/skills/algebra-driven-design/references/source-notes.md
codex/skills/algebra-driven-design/references/agentic-skill-application.md
codex/skills/algebra-driven-design/references/examples.md
```

If `codex/algebra-driven-design/SKILL.md` is absent in the active checkout, do not fail silently and do not invent bundle contents. Use the minimal ADD kernel below, report the missing canonical path as a local-reference gap, and continue only for work that the kernel can support.

## Minimal ADD kernel

Use Algebra-Driven Design for domain algebra:

- carriers / data domains;
- operations / constructors / eliminators;
- observations;
- laws and explicit non-laws;
- interpreters;
- property tests or law-derived examples;
- architecture derived from the laws.

A compact ADD pass should produce:

```text
Domain:
Carriers:
Operations:
Observations:
Laws:
Non-laws:
Interpreters:
Property tests / falsifiers:
Architecture implication:
```

## Boundary summary

Use `algebra-driven-design` for domain algebra. Use `universalist` when the central problem is a boundary equation, certified composition, exact context, sheafification, or a universal-architecture seam.
