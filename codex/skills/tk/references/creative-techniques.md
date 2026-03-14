# Creative Techniques (TK)

## Technique selection (canonical: creative-problem-solver)
- Pick 1 technique using the `$creative-problem-solver` skill’s **Technique selection** section.
- Then consult the matching technique reference in that skill.
- Use the picker name verbatim whenever TK surfaces Creative Frame so evals can detect off-picker drift.
- If no Aha (no meaningful representation shift), pick 1 more technique from a different picker row (max 2).
- This file exists for TK-specific Lotus Blossom petals + tier mapping.

## Lotus Blossom (TK adaptation)
- Center: stable boundary + contract (one line).
- Petals: list the TK-native levers/subproblems that make the cut more truthful:
  - Stable boundary / seam (push effects + enforcement to the boundary).
  - Seam comparison (compare candidate cuts by where the rule truly lives).
  - Invariant strengthening (types/parse/tests).
  - Truth surface alignment (compare public claim, runtime enforcement, proof harness, and checked artifacts).
  - Representation / normal form (collapse cases, delete branches).
  - Abstraction level (inline fix vs helper vs algebraic island vs adapter).
  - Abstraction timing (one strict instance, second port, then extraction).
  - Proof signal (fast check: test/typecheck/log, law check, or commuting diagram).
  - Reversibility lever (rollback, flag, adapter, fallback).
  - Primary failure mode (crash / corruption / logic).
  - Caller ergonomics / footguns (make misuse hard).
  - Blast radius / integration surface (how wide the cut spreads).
- Expansion: expand each petal into concrete candidate incisions; map candidates into the 5 tiers, then pick the highest provable tier.

Scoring reminder:
- Compare candidates first on seam choice, abstraction level, blast radius, and proof posture.
- Prefer candidates that make the repo's claims more truthful before candidates that only rearrange local syntax.
- Only use wording/readability as a tie-breaker after the code-shape decision is settled.

Visible-frame reminder:
- In non-strict mode, surface only the winning `Creative Frame`: truth gap, reframe + technique, representation shift, accretive bet.
- Keep the full portfolio internal unless the user explicitly asks for options or tradeoffs.

## Tiers + selection
For each tier, attach:
- Expected proof signal: what you will run/observe to learn.
- Escape hatch: how you revert or narrow scope if wrong.

Tiers:
- Quick Win: smallest local patch; least movement.
- Strategic Play: clarify a boundary; add a seam; enable tests.
- Advantage Play: local type/normal-form change that reduces branching.
- Transformative Move: small algebraic island; composition-first core; adapters at edges.
- Moonshot: architectural boundary change, but only incremental + reversible.

Selection rule:
- Choose the highest tier that remains reviewable, incremental, and provable.
- Preference (when in doubt): maximize Learning value and Reversibility; minimize blast radius.
