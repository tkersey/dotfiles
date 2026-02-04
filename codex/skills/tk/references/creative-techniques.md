# Creative Techniques (TK)

## Technique picker (default: Lotus blossom)
- Need breadth across seams (subproblems → options): Lotus blossom.
- Need to mutate an existing approach: SCAMPER.
- Need lots of ideas fast: Brainwriting 6-3-5 (solo ok).
- Need structured combinations: Morphological analysis.
- Need to resolve contradictions: TRIZ.
- Need parallel perspectives: Six Thinking Hats.
- Need to harden against failure: Reverse brainstorming.
- Need a fresh spark: Random stimulus or provocation.

## Technique library (short)
- Lotus blossom: expand outward from a core problem into 8 TK-native “petals,” then expand each petal to force breadth and populate the portfolio.
- SCAMPER: Substitute/Combine/Adapt/Modify/Put to use/Eliminate/Reverse.
- Brainwriting 6-3-5: timed rounds to generate + iterate quietly.
- Morphological analysis: enumerate combinations across dimensions.
- TRIZ: state the contradiction, then apply separation principles.
- Six Thinking Hats: facts → feelings → risks → benefits → ideas → process.
- Reverse brainstorming: “how do we make it worse?” then invert.
- Random stimulus / provocation: force a lever from an unrelated prompt.

## Lotus blossom (TK use)
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
