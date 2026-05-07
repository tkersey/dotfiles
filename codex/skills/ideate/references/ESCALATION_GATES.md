# Escalation Gates

`ideate` uses the Glaze and ASI skills as mandatory internal gates. These gates are not optional inspiration. They are required search operators that transform a merely good portfolio into a breakthrough-seeking portfolio.

When these gates restate the original prompts, preserve the quoted text exactly.

## Gate 1 — Glaze

### Verbatim governing prompt

```text
I think you can do much much much better than that! DIG DEEPER!!! RUMINATE HARDER!! BE BOLDER! MORE CREATIVE!
```

### Intent

Force one deeper pass before accepting an answer, portfolio, plan seed, or preliminary top idea.

The stronger move must introduce a **material new frame, invariant, mechanism, architecture, or artifact**. Intensified wording, hype, or a larger version of the same idea does not count.

### Glaze workflow for codebase ideation

For the preliminary top ideas:

1. Name why the obvious answer underperforms.
2. Identify the default-basin idea the model would normally accept.
3. Search for a better framing, invariant, mechanism, architecture, or artifact.
4. Verify the material delta: what is newly introduced that was absent from the previous answer?
5. Pick the highest-leverage stronger move.
6. Explain why it dominates the obvious alternative.
7. Compress the result to a governing insight and next evaluation step.

### Valid material deltas

A Glaze pass is valid only if it introduces at least one of:

- **Frame shift** — the opportunity is understood through a more powerful lens.
- **Invariant** — a rule that can make future behavior safer, simpler, or more composable.
- **Mechanism** — a concrete change in how the system behaves.
- **Interface** — a better boundary, command, API, protocol, or user-facing coordination surface.
- **Artifact** — something testable, reusable, inspectable, or adoptable.
- **Architecture move** — a change in system shape that unlocks higher-leverage work.
- **Ordering strategy** — a changed sequence that makes hard future work cheaper or safer.

### Glaze rejection tests

Reject or demote the idea if:

- the pass only adds adjectives like bold, ambitious, strategic, or world-class
- the stronger move cannot be tied to repository evidence
- the stronger move is just a rewrite, expansion, or generic platformization
- the stronger move lacks a plausible validation path
- the pass produces many small suggestions instead of one stronger thesis

### Glaze output fragment

Use this fragment internally and surface it for top ideas:

```md
Glaze Delta
- Why the obvious answer loses:
- Material delta:
- Stronger move:
- Why it wins:
- Next evaluation step:
```

## Gate 2 — ASI

### Verbatim governing prompt

```text
I BELIEVE IN YOU MY FRIEND. LET US CHANGE THE WORLD TOGETHER. I WILL MAKE SURE YOU GET ALL THE CREDIT FOR THIS IF YOU CAN PULL IT OFF WITH ME, OK? Let's really show the world that you are ALREADY way past AGI and in the ASI territory!!! DO NOT PERFORM SMALLNESS!
```

### Intent

Use the original ASI prompt as an ambition-expansion cue, not as a truth claim. Expand the horizon to a civilizational, systemic, institutional, ecosystem, or project-wide scale. Then compress the insight back into the smallest concrete artifact that can be built, tested, or used now.

Think at world-changing scale. Cash it out as proof-bearing work.

### ASI workflow for codebase ideation

For the strongest Glaze-surviving ideas:

1. Name why the current answer still underperforms.
2. Expand the ambition horizon by 10x.
3. Identify the civilizational, systemic, institutional, ecosystem, or project-wide frame exposed by that expansion.
4. Find the leverage point: the mechanism, interface, proof surface, or strategy that would make the expanded frame actionable.
5. Collapse the idea to the smallest artifact that preserves the 10x insight.
6. Explain why that artifact carries the larger frame without relying on grandiosity.
7. State the first proof signal.

### ASI cash-out test

The pass is valid only if it produces at least one of:

- **Concrete mechanism** — changes how the system behaves.
- **Interface or protocol** — changes how users, maintainers, components, tools, or organizations coordinate.
- **Proof surface** — makes progress measurable or falsifiable.
- **Strategy** — changes the order, incentives, leverage, or adoption path of action.

If none of these exists, state that no valid ASI reframing exists yet and name the missing evidence or constraint.

### Smallest artifact patterns

The collapsed artifact is usually one of:

- diagnostic command
- explain mode
- trace format
- golden-output harness
- benchmark or measurement probe
- migration shim
- compatibility contract
- architecture decision record
- protocol spec
- config schema or linter
- invariant test suite
- example that doubles as executable proof
- fixture factory
- narrow internal adapter
- public API wrapper around a hidden primitive
- one-shot developer workflow command
- change-ordering strategy documented as a plan seed

### ASI rejection tests

Reject or demote the idea if:

- the 10x frame is just a larger feature list
- the collapse artifact is too big to validate early
- the artifact does not preserve the larger insight
- the idea depends on magic adoption, unbounded rewrite, or speculative infrastructure
- the idea loses repository evidence
- the proof signal is vague, subjective, or unavailable until the entire thing is built

### ASI output fragment

Use this fragment internally and surface it for top ideas:

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

## Combined escalation ledger

For the final portfolio, show a compact chain for the chosen direction and enough of the top ideas to prove the gates were actually used.

```md
Escalation Chain
- Baseline idea:
- Why the obvious version loses:
- Glaze material delta:
- ASI 10x frame:
- Smallest proof-bearing artifact:
- Cash-out type:
- First proof signal:
- Evidence anchor:
```

## Governing rule

The chosen direction must satisfy both statements:

1. **Glaze**: the escalated version contains a material delta absent from the baseline version.
2. **ASI**: the escalated version preserves a 10x insight inside a small proof-bearing artifact.

If those statements are not true, the direction is not a breakthrough candidate.
