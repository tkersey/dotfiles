---
name: plan
description: Plan and beadify work end-to-end (clarify → options → beads); stop before implementation.
---

# Plan

## Contract
- Pipeline: `$clarification-expert` → `$creative-problem-solver` → `$gen-beads`.
- Default to executing the Transformative tier unless the user picks another.
- Hard-stop after bead creation (no implementation).
- Swarm rules: split work that exceeds 1 day or >3 files; cap epics at 7.

## Phase 1: Clarify (CE)
1. Research first; don’t ask for discoverable facts.
2. Keep a running snapshot (facts, decisions, open questions).
3. Ask only judgment calls under:
   `CLARIFICATION EXPERT: HUMAN INPUT REQUIRED`.
4. Repeat until open questions are empty.

Snapshot template:
```
Snapshot
- Facts:
- Decisions:
- Open questions:
```

## Phase 2: Options (CPS)
1. Reframe the constraint.
2. Produce a portfolio:
   - Quick Win
   - Strategic Play
   - Advantage Play
   - Transformative Move
   - Moonshot
3. For each option: expected signal + escape hatch.
4. Score options (Signal, Cost, Reversibility, Time).
5. Default to Transformative unless the user chooses another tier.

## Phase 3: Beads (Gen-Beads)
Follow the `gen-beads` workflow to create beads via `bd`.

## Deliverable
- CE snapshot + human input block (if needed).
- CPS portfolio + scores.
- Beads created with a compact index.
- Stop.
