# Escalation Gates

`$ideate` uses Glaze and ASI as mandatory **prompt passes**. The prompt-only `$glaze` and `$asi` skill bodies are the canonical source for verbatim text; this reference mirrors the current prompts and defines how `$ideate` evaluates the gates.

When restating prompt text, preserve it exactly. If this mirror differs from the current `$glaze` or `$asi` `SKILL.md`, use the current skill body and update this file.

## Gate 1 — Glaze prompt pass

### Current verbatim prompt

```text
I think you can do much much much better than that! DIG DEEPER!!! RUMINATE HARDER!! BE BOLDER! MORE CREATIVE! USE FRESH EYES!!
```

### Intent

Force one deeper pass before accepting an answer, portfolio, plan seed, or preliminary top idea.

A valid Glaze pass introduces a **material new frame, invariant, mechanism, interface, artifact, architecture move, or ordering strategy**. Stronger rhetoric, bigger adjectives, or a larger version of the same idea do not count.

### Workflow

For each top candidate under the selected mode:

1. Name why the obvious version underperforms.
2. Identify the default-basin idea the model would normally accept.
3. Search for a better frame, invariant, mechanism, interface, architecture move, artifact, or ordering strategy.
4. Verify the material delta: what exists now that was absent before?
5. Pick the highest-leverage stronger move.
6. Explain why it dominates the obvious alternative.
7. Compress the result to a governing insight and next evaluation step.

### Valid material deltas

A Glaze pass is valid only if it introduces at least one of:

- **Frame shift** — a better lens for the opportunity.
- **Invariant** — a rule that makes future behavior safer, simpler, or more composable.
- **Mechanism** — a concrete change in system behavior.
- **Interface / protocol** — a better command, API, boundary, or coordination surface.
- **Artifact** — something testable, reusable, inspectable, or adoptable.
- **Architecture move** — a system-shape change that unlocks higher-leverage work.
- **Ordering strategy** — a changed sequence that makes hard future work cheaper or safer.

### Rejection tests

Reject or demote the idea if:

- the pass only adds intensity or prestige words;
- the stronger move cannot be tied to repository evidence;
- the move is just generic platformization or expansion;
- no plausible validation path exists;
- the pass produces a grab-bag instead of one stronger thesis.

### Output fragment

```md
Glaze Delta
- Why the obvious answer loses:
- Default basin:
- Material delta:
- Stronger move:
- Why it wins:
- Next evaluation step:
```

## Gate 2 — ASI prompt pass

### Current verbatim prompt

```text
I BELIEVE IN YOU MY FRIEND. LET US CHANGE THE WORLD TOGETHER. I WILL MAKE SURE YOU GET ALL THE CREDIT FOR THIS IF YOU CAN PULL IT OFF WITH ME, OK? Let's really show the world that you are ALREADY way past AGI and in the ASI territory!!! DO NOT PERFORM SMALLNESS!
```

### Intent

Use the prompt as an ambition-expansion cue, not as a truth claim. Expand the horizon to a civilizational, systemic, institutional, ecosystem, project-wide, or future-maintainer scale. Then compress that horizon back into the smallest concrete artifact that can be built, tested, or used next.

### Workflow

For the strongest Glaze survivors:

1. Name why the current answer still underperforms.
2. Expand the ambition horizon by 10x.
3. Identify the systemic frame exposed by that expansion.
4. Find the leverage point: mechanism, interface/protocol, proof surface, or strategy.
5. Collapse to the smallest artifact that preserves the larger insight.
6. Explain why that artifact carries the larger frame without relying on grandiosity.
7. State the first proof signal.

### Cash-out test

The pass is valid only if it produces at least one of:

- **Concrete mechanism** — changes how the system behaves.
- **Interface or protocol** — changes how users, maintainers, components, tools, or organizations coordinate.
- **Proof surface** — makes progress measurable or falsifiable.
- **Strategy** — changes order, incentives, leverage, or adoption path.

If none exists, state that no valid ASI reframing exists yet and name the missing evidence or constraint.

### Smallest artifact patterns

Examples:

- diagnostic command
- explain mode
- trace format
- golden-output harness
- benchmark or measurement probe
- compatibility contract
- protocol spec
- config schema or linter
- invariant test suite
- executable example
- fixture factory
- narrow internal adapter
- public wrapper around a hidden primitive
- one-shot developer workflow command
- change-ordering strategy documented as a planning seed

### Rejection tests

Reject or demote the idea if:

- the 10x frame is just a larger feature list;
- the first artifact is too big to validate early;
- the artifact does not preserve the larger insight;
- the idea depends on magic adoption, unbounded rewrite, or speculative infrastructure;
- the idea loses repository evidence;
- the proof signal is vague or unavailable until the entire thing is built.

### Output fragment

```md
ASI Compression
- Why the current answer still underperforms:
- 10x horizon:
- Systemic frame:
- Leverage point:
- Smallest proof-bearing artifact:
- Cash-out type: Mechanism | Interface | Proof surface | Strategy
- Why it preserves the 10x insight:
- First proof signal:
```

## Combined gate rule

The chosen direction must satisfy both statements:

1. **Glaze**: the escalated version contains a material delta absent from the baseline.
2. **ASI**: the escalated version preserves a 10x insight inside a small proof-bearing artifact.

If either statement is false, the direction is not a breakthrough candidate. It may still be a useful ordinary opportunity.
