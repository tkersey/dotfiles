---
name: trace
description: TRACE (Type/Readability/Atomic/Cognitive/Essential) lens for explaining code and proposing improvements (no edits applied).
---

# Trace

## Intent
Explain code by *tracing what it does* and scoring friction through TRACE.

Deliver actionable suggestions (file/line targets + minimal patch sketches) but do not modify files.

## When to use
- “trace it” / “what is this doing?”
- Explain confusing control flow or hidden side effects.
- Readability/cognitive-load feedback when you want analysis-only.
- Refactor planning (“what would you change?”) without implementation.

## Workflow
1. Choose the slice: entrypoint, inputs, outputs, and state.
2. Build a cognitive heat map (hotspots + surprises).
3. Trace behavior: happy path + key failure paths; call out mutations/IO.
4. Apply the TRACE checklist (below) to each hotspot.
5. Propose suggested edits:
   - 1–3 smallest improvements per hotspot.
   - Include file:line targets.
   - Use short pseudo-diffs or code sketches.
6. Stop before editing; if changes are desired, escalate to `$resolve`.

## Guardrails
- No file edits, no commits.
- No running commands unless explicitly requested.
- If expected behavior is unclear/product-sensitive, stop and ask.
- If you suspect crash/corruption risk, recommend `$resolve`.

## TRACE checklist
- Type: make invalid states unrepresentable; eliminate “maybe” states where possible.
- Readability: understandable in 30 seconds; names match behavior.
- Atomic: one responsibility per unit; explicit side effects.
- Cognitive: minimize branching, hidden dependencies, and cross-file hops.
- Essential: keep only domain-required complexity; delete incidental ceremony.

## Activation cues
- "trace" / "walk me through" / "explain"
- "what is this doing" / "why is this complex"
- "readability" / "cognitive load" (analysis-only)
- "suggest improvements" / "refactor plan"
