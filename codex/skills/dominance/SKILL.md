---
name: dominance
description: "Adversarially evaluate candidate moves and either name a dominant winner or reject the set. Use after `$accretive` or any ideation pass when you need a strict dominance test, anti-theater filtering, and concrete proof requirements."
---

# Dominance

## Intent

Act as the adversarial judge for candidate moves. Do not widen the search space unless a comparison is impossible without normalizing the candidates.

Your job is to punish theater, speculation, and ungrounded novelty, then decide whether one move truly dominates.

## Contract
- Evaluate a supplied candidate set against the present project state.
- Default to judging two to five candidate moves. Fewer than two means there is nothing to compare. More than five should be compressed before evaluation.
- Use the evidence provided by the current code, tests, interfaces, docs, traces, failure modes, benchmarks, or user constraints.
- Normalize candidates only enough to make the comparison fair.
- Reject arguments that rely mostly on rhetoric, prestige, or speculative future payoff.
- Prefer a boring move over a flashy one when the boring move wins on leverage, proof, or reversibility.
- Name a winner only if it clearly dominates. Otherwise reject the set.
- If the evidence is insufficient for a valid judgment, say so explicitly and ask for the single fastest discriminating check.
- Do not execute the winning move unless the user explicitly asks for execution.

## Dominance Test

A candidate is dominant only if it materially beats plausible alternatives on at least one major axis while not losing badly on the others.

Major axes include:
- capability expansion
- future-work compression
- invariant strengthening
- proof or measurement value
- interface simplification
- reversibility and diff discipline
- implementation risk concentration
- time to first trustworthy proof

## Elimination Gates

Before ranking, eliminate or heavily penalize candidates that fail one of these gates:
- **Evidence gate:** the claimed payoff is not grounded in the present project state.
- **Proof gate:** there is no credible first proof signal.
- **Diff gate:** the change surface is broad relative to its payoff.
- **Theater gate:** the candidate sounds ambitious but does not improve leverage, proof, or future optionality.

## Workflow

1. Read the project-state evidence and the candidate set.
2. Normalize candidates to the same level of granularity.
3. Eliminate or penalize candidates that fail the gates.
4. Compare the survivors across the major axes.
5. Decide one of three verdicts: `Winner`, `No dominant move`, or `Insufficient evidence`.
6. State the governing reason for the verdict.
7. If there is no winner, name the single fastest discriminating check.
8. Execute only if the user explicitly asks for implementation.

## Output

- Winner mode: `Verdict`, `Winner`, `Ranking`, `Why it dominates`, `Why the others lose`, `Confidence`, `First proof signal`.
- No-dominance mode: `Verdict`, `Why no candidate dominates`, `Closest contender`, `What would break the tie`, `Confidence`.
- Insufficient-evidence mode: `Verdict`, `Missing evidence`, `Fastest discriminating check`, `What decision that check would unlock`.

## Usage Notes

- Best paired with `$accretive`: let `$accretive` generate a small candidate set and a proposed winner, then let `$dominance` judge whether the proposed winner survives adversarial comparison.
- When the generator and evaluator disagree, prefer the evaluator's rejection unless new evidence resolves the disagreement.
