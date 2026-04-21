---
name: accretive
description: "Activate maximal ambition, include a non-obvious candidate frame, then choose one dominant accretive move grounded in the current project state. Preserve the original accretive prompt wording exactly except for an injectable target parameter."
---

# Accretive

## Parameterized Prompt Form

Use this template to preserve the historical wording while injecting a target:

```text
What's the single smartest and most radically innovative and accretive and useful and compelling {target} you could make to the project at this point?
```

## Intent

Use the historical grandiose sentence to widen the search radius. Then apply a strict dominance test so the result is genuinely high-leverage rather than merely theatrical.

Think with maximal ambition. Decide with maximal discipline.

## Contract
- Start from the parameterized prompt form above.
- Preserve the historical sentence exactly except for the injected `{target}` value.
- Treat `target` as an explicit parameter.
- Use `addition` and `change` as the built-in historical targets.
- Allow other targets when the user names them or when another lane has higher leverage.
- If the user supplies no target, choose the target lane that best fits the current project state and state it explicitly.
- Inspect the current project state before choosing the move.
- Ground the choice in concrete evidence from the present state: code paths, interfaces, tests, docs, bottlenecks, failure modes, TODOs, repetition, missing capabilities, or missing proof.
- Generate a small set of plausible moves and choose exactly one only if it clearly dominates nearby alternatives.
- At least one candidate must come from a non-obvious frame, not merely from the current roadmap, conventional architecture, or nearest visible TODO.
- Keep the candidate set crisp enough that it can be handed to a separate evaluator without being rewritten.
- Prefer moves that compound future leverage: new capabilities, simpler architecture, stronger invariants, better tooling, tighter proof surfaces, cleaner interfaces, reusable artifacts, or reduced future cost of change.
- Reject churn, cosmetic polish, and broad cleanup without a governing payoff.
- Do not confuse novelty with leverage. A boring move can win if it unlocks more future value, reduces uncertainty, or produces better proof.
- If no move clearly dominates, abstain. Say that no dominant move exists yet, name the blocked decision, and state the missing evidence that would resolve it.
- If the user asked for execution, implement the move with minimal decisive incision and report concrete validation. Otherwise stop at recommendation.

## Target Parameter
- `target=addition`: yields the original historical `add` prompt shape.
- `target=change`: yields the original historical `chng` prompt shape.
- `target=<other phrase>`: inject that phrase into the parameterized prompt form and keep the rest of the sentence unchanged.
- Prefer singular noun phrases that fit the sentence naturally.
- Preferred target lanes include `capability`, `interface`, `tooling`, `invariant`, `proof surface`, `refactor`, or another named lane that better captures the dominant opportunity.
- Ask for clarification only if the target wording is ambiguous enough to change the selected move.

## Dominance Test

A move is dominant only if it materially beats plausible alternatives on at least one important axis without losing badly on the others.

Important axes include:
- capability expansion
- future-work compression
- invariant strengthening
- proof or measurement value
- interface simplification
- reversibility and diff discipline

## Validation / Proof

Validation must be concrete whenever possible. Prefer one or more of:
- a new or previously failing test that now passes
- a benchmark delta
- a narrower error surface or stronger type/check/assertion boundary
- a simpler interface or reduced configuration surface
- a generated artifact, trace, or reproducible example that proves the new behavior
- documentation that now describes a capability that actually exists

## Workflow

1. Inspect the current state and note concrete evidence.
2. Resolve the target parameter from the request, or choose one if absent.
3. Form the governing prompt sentence using the exact historical wording.
4. Generate two to four plausible moves within the chosen target lane, including at least one non-obvious frame candidate.
5. Compare them by leverage, accretion, reversibility, and proof value.
6. Pick the single dominant move, or abstain if none dominates.
7. State the governing reason it wins, or why the decision is blocked.
8. Execute only if the user asked for action.
9. Report the first proof signal or completed validation.

## Output

- Recommendation mode: `Target`, `Prompt sentence`, `Current-state evidence`, `Move`, `Why it wins`, `Why not the next-best alternatives`, `First proof signal`, `Next step`.
- Abstention mode: `Target`, `Prompt sentence`, `Why no move dominates yet`, `Missing evidence`, `Fastest way to get that evidence`.
- Execution mode: make the move, then report `Target`, `Move made`, `Evidence used`, `Validation`, `Residual risk`, `Next step`.
