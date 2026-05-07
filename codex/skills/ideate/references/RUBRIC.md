# Idea Evaluation Rubric

Score each idea from 1-5 on the criteria that apply. Use the weights to rank, but do not let arithmetic override strong judgment.

## Core criteria

| Criterion | Weight | What to ask |
|---|---:|---|
| Useful | 2.0x | Does it solve a real, frequent, painful, or strategically important problem? |
| User / maintainer pain | 2.0x | Is there a concrete pain signal for a user, maintainer, contributor, operator, or future implementer? |
| Evidence strength | 2.0x | Is this grounded in concrete repo signals rather than vibes? |
| Leverage | 2.0x | Does this unlock multiple future improvements, reduce recurring friction, or lower future risk? |
| Pragmatic | 2.0x | Is it realistic given visible constraints and likely effort? |
| Accretive | 1.5x | Does it clearly add value without making the system worse? |
| Originality / latentness | 1.5x | Is it non-obvious but natural once the evidence is seen? |
| Architecture fit | 1.5x | Does it work with the current architecture rather than fighting it? |
| Validation cheapness | 1.5x | Can we test or de-risk the idea before committing to a full plan? |
| Behavior risk | 1.5x inverse | How likely is this to change behavior unintentionally? Lower risk scores higher. |
| Robust | 1.0x | Does it handle important edge cases and failure paths? |
| Reliable | 1.0x | Will it work consistently, not just in the happy path? |
| Performant | 1.0x | Is speed or efficiency good enough for the user context? |
| Intuitive | 1.0x | Will users or maintainers understand what it does and how it behaves? |
| Ergonomic | 1.0x | Does it remove friction, steps, or cognitive load? |
| Compelling | 1.0x | Will the target users or maintainers actually care? |
| Maintenance delta | 1.25x | Does it reduce or contain future maintenance burden? |
| Strategic fit | 1.25x | Does it reinforce the project's direction rather than distract from it? |

## Scoring guide

Use this rough meaning for 1-5 scores:

- **5**: Strong evidence, high value, clear fit, obvious next-step candidate.
- **4**: Good evidence and value, with manageable uncertainty.
- **3**: Plausible, but evidence, value, or fit is mixed.
- **2**: Weakly supported, generic, high-risk, or low-leverage.
- **1**: Should probably be cut.

## Hard cut rules

Cut an idea if:

- it has no repo evidence and was not explicitly requested as speculative
- it is just "add tests" or "write docs" without a sharper underlying opportunity
- it is a refactor with no behavior-preservation strategy
- it duplicates an existing issue, roadmap item, TODO, or recently completed change without a compelling delta
- it requires a large rewrite before any value appears
- it optimizes an area with no evidence of user, maintainer, reliability, or performance pain
- it needs miracle assumptions
- it creates more complexity than value
- it cannot be validated until very late
- it is mostly an implementation detail disguised as strategy

## Tie-breakers

Use these when several ideas score similarly:

| Tie-breaker | What to ask |
|---|---|
| Cheapest credible validation | Which idea can be tested with the smallest real evidence-gathering step? |
| Asymmetric leverage | Which idea makes many future changes easier? |
| Reversibility | Which idea can be contained or undone if wrong? |
| Clarity of ownership | Which idea has the clearest owner and adoption path? |
| Portfolio diversity | Which idea adds a useful different angle to the top set? |
| Behavior stability | Which idea creates the least risk of unintended user-visible change? |

## Winnowing process

1. **Hard cuts** — Remove ideas with fatal flaws, obvious duplication, or no evidence.
2. **Threshold** — Remove ideas with poor weighted scores.
3. **Evidence review** — Remove or downgrade ideas whose evidence is generic or too thin.
4. **Originality review** — Remove or downgrade ideas that could be suggested for any repository.
5. **Ranking** — Rank the remainder by weighted score and rationale quality.
6. **Synergy check** — Keep complementary ideas in view even if they are not individually #1.
7. **Overlap check** — Downgrade duplicates, merge adjacent ideas, and flag conflicts.
8. **Selection** — Pick the leading direction only after validation potential and behavior risk are considered.

## Red flags

Be skeptical of ideas justified mainly by:

- "it would be cool"
- "users can learn it"
- "we can document it later"
- "it's technically possible"
- "this is cleaner"
- "every project should have this"
- "AI could do it"
- "it sounds more ambitious"
- "this might be useful someday"

## Good signs

Prefer ideas that have at least two of:

- repeated repo evidence across different artifacts
- direct connection to a public surface or maintainer workflow
- a plausible hidden primitive or negative-space signal
- a clear behavior-preserving validation path
- a small first step that produces learning
- a likely reduction in future maintenance burden
- an obvious reason now is a good time
