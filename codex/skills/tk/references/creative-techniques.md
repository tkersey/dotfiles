# Creative Techniques (TK)

## Technique selection (canonical: creative-problem-solver)
- Pick 1 technique using the `$creative-problem-solver` skill’s **Technique selection** section.
- Then consult the matching technique reference in that skill.
- If no Aha (no meaningful representation shift), pick 1 more technique from a different picker row (max 2).
- This file exists for TK-specific Lotus Blossom petals + tier mapping.

## Lotus Blossom (TK adaptation)
- Center: stable boundary + contract (one line).
- Petals: list 8 TK-native levers/subproblems:
  - Stable boundary / seam (push effects + enforcement to the boundary).
  - Invariant strengthening (types/parse/tests).
  - Representation / normal form (collapse cases, delete branches).
  - Proof signal (fast check: test/typecheck/log, law check, or commuting diagram).
  - Reversibility lever (rollback, flag, adapter, fallback).
  - Primary failure mode (crash / corruption / logic).
  - Caller ergonomics / footguns (make misuse hard).
  - Blast radius / integration surface (how wide the cut spreads).
- Expansion: expand each petal into concrete candidate incisions; map candidates into the 5 tiers, then pick the highest provable tier.

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
