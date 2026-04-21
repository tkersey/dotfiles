---
name: glaze
description: "Run one explicit escalation pass using the original glaze prompt words verbatim, requiring a material new frame, invariant, mechanism, or artifact. Use when prompts say `$glaze`, when the first answer feels merely adequate, or when you want the exact original rhetoric preserved while pushing for a materially stronger direction."
---

# Glaze

## Verbatim Prompt

Use this text verbatim as the governing escalation text for the pass. Do not paraphrase, soften, summarize, or rewrite it.

```text
I think you can do much much much better than that! DIG DEEPER!!! RUMINATE HARDER!! BE BOLDER! MORE CREATIVE!
```

## Intent

Force one deeper pass before accepting an answer or plan, while preserving the original prompt language above exactly.

## Contract

- Start from the verbatim prompt text above.
- Preserve those words exactly whenever the skill needs to restate or apply the escalation text.
- Treat the current answer, plan, or instinct as insufficiently strong.
- Reject the first merely adequate move.
- Widen the search space once and look for a more accretive, more dominant direction.
- The stronger move must introduce a new frame, invariant, mechanism, or artifact not present in the previous answer. Intensified wording alone does not count.
- Prefer one strong thesis over a grab-bag of decent ideas.
- Keep the result grounded and operational, not hype-driven.
- If execution is requested, continue with the stronger plan after the reframing pass.

## Workflow

1. Name why the current answer underperforms.
2. Search for a better framing, invariant, mechanism, artifact, or architecture.
3. Verify the material delta: what is newly introduced that was absent from the previous answer?
4. Pick the highest-leverage move now available.
5. Explain why it dominates the obvious alternative.
6. Compress the result to the governing insight and next action.

## Output

- Default: `Why the obvious answer loses`, `Material delta`, `Stronger move`, `Why it wins`, `Next action`.
- If no materially better move exists, say so explicitly instead of manufacturing novelty.
