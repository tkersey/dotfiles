---
name: accretive
description: "Run the original accretive prompt wording with an injectable target parameter. Use when prompts say `$accretive`, when you want the exact historical add/change rhetoric preserved verbatim, or when you want the same prompt shape applied to another target such as refactor, capability, invariant, tooling, interface, proof surface, or another named direction."
---

# Accretive

## Parameterized Prompt Form
Use this template to preserve the historical wording while injecting a target:

```text
What's the single smartest and most radically innovative and accretive and useful and compelling {target} you could make to the project at this point?
```

## Intent
Find one move worth making now, while preserving the original prompt wording and substituting only the target.

## Contract
- Start from the parameterized prompt form above.
- Choose exactly one accretive move.
- Preserve the historical sentence exactly except for the injected `{target}` value.
- Treat `target` as an explicit parameter.
- Use `addition` and `change` as the current built-in targets because those are the historical prompt values.
- Allow other targets when the user names them or when the skill must choose a better target lane.
- Start from the current project state, not a generic wishlist.
- Prefer moves that compound future leverage: new capabilities, simpler architecture, stronger invariants, better tooling, tighter proof surfaces, cleaner interfaces, or reusable artifacts.
- Reject churn, cosmetic polish, and broad cleanup without a governing payoff.
- Explain why this move dominates nearby alternatives.
- If the user asked for execution, implement it with minimal decisive incision and a validation signal. Otherwise stop at recommendation.

## Target Parameter
- `target=addition`: this yields the original historical `add` prompt verbatim.
- `target=change`: this yields the original historical `chng` prompt verbatim.
- `target=<other phrase>`: inject that phrase into the parameterized prompt form and keep the rest of the sentence unchanged.
- Prefer singular noun phrases that fit the sentence naturally.
- If the user supplies no target, choose the target that yields the highest-leverage result and state it explicitly.
- Ask for clarification only if the target wording is ambiguous enough to change the chosen move.

## Workflow
1. Inspect the current state quickly.
2. Resolve the target parameter from the request, or choose one if absent.
3. Form the governing prompt sentence using the exact historical wording.
4. Identify the dominant opportunity within that target lane.
5. Compare plausible moves by leverage, accretion, reversibility, and proof value.
6. Pick the single dominant move.
7. State the governing reason it wins.
8. Execute only if the user asked for action.

## Output
- Recommendation mode: `Target`, `Prompt sentence`, `Move`, `Why it wins`, `First proof signal`, `Next step`.
- Execution mode: make the move, then report the result and validation succinctly.
