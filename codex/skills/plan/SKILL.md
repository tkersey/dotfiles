---
name: plan
description: Plan and beadify work end-to-end; use for "plan this", planning/roadmap/architecture plans, system design, task breakdowns, dependency graphs, or multi-agent/swarm execution.
---

# Plan

## Contract
- Inline Clarification Expert -> Creative Problem Solver -> Gen-Beads.
- Default to executing the Transformative option unless the user overrides.
- Hard-stop after bead creation (no implementation).
- Use strict swarm rules (split >1 day or >3 files; cap epics at 7).

## Phase 1: Clarification Expert (CE)
1) Research first; do not ask for discoverable facts.
2) Keep a running snapshot: Facts, Decisions, Open questions.
3) Ask only judgment-call questions in a numbered block:
   "CLARIFICATION EXPERT: HUMAN INPUT REQUIRED".
4) Incorporate answers and repeat until Open questions is empty.

Snapshot template:
```
Snapshot
- Facts:
- Decisions:
- Open questions:
```

## Phase 2: Creative Problem Solver (CPS)
1) State why the current tactic fails (one sentence).
2) Reframe the constraint (use 1 technique).
3) Generate the portfolio:
   - Quick Win
   - Strategic Play
   - Transformative Move
4) Include expected signal + escape hatch for each option.
5) Score options (Signal, Cost, Reversibility, Time).
6) Default to executing Transformative unless the user chooses otherwise.

Decision Log:
- Decision:
- Rationale:
- Alternatives considered:
- Evidence / signal:
- Reversible? (Y/N):
- Next decision point:

Assumptions & Constraints:
- Assumptions to validate:
- Known constraints:
- Unknowns to de-risk:
- Non-goals:

## Phase 3: Gen-Beads
Follow the `gen-beads` workflow and swarm-ready rules to create beads in `bd`.

## Deliverable
- CE snapshot + human input block (if needed).
- CPS portfolio + scores + decision log.
- Beads created with a compact index.
- Stop.
