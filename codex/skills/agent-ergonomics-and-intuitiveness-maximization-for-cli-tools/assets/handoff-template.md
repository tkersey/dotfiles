# Pass <N> Handoff

**Pass.** <N>
**Mode.** <full|audit-only|...>
**Target SHA at start.** <pre-pass SHA>
**Target SHA at end.** <post-pass SHA>
**Sibling SHA at end.** <sibling commit SHA>
**Feature branch.** <branch name>; status: <pushed|local-only>
**Date range.** <ISO start> — <ISO end>

---

## What we did

- Mode: <mode>
- Surfaces inventoried: <count>
- Surfaces scored: <count>
- Recommendations drafted: <count>
- Recommendations applied: <count> / <total>
- Recommendations deferred: <count>
- Fresh-eyes rounds: <count>

---

## Uplift summary

- **Median weighted uplift across applied surfaces:** +<N> pts
- **Total surfaces improved:** <count>
- **Total surfaces regressed:** <count>
- **Surfaces above Polish-Bar (≥ 750 weighted):** <count>/<total>

### Top 5 wins (by uplift)

- R-NNN: <title> — +<N> pts on <dims>
- ...

### Regressions

(none — clean)
or
| surface_id | dim | prior | new | Δ | likely cause |
|------------|-----|-------|-----|---|--------------|
| ...

---

## Applied recommendations

- R-001: <title> (priority <N>; uplift +<delta>)
- ...

---

## Deferred recommendations

- R-NNN: <title>
  - **Deferred reason:** <reason>
  - **Queued for Pass N+1:** <yes|maybe|no>
- ...

---

## Phase 9 simulation outcomes

- Tasks completed: <K>/<M>
- Median round-trips: <N> (vs pre-pass: <N'>)
- Tasks where simulator got stuck: <list>

---

## Rubric refinements suggested

- **<dim>**: anchor at <level> was confusing because... Propose: ...

---

## CASS findings worth recording

- F-NNN: <pattern> (citing <session_count> sessions)

---

## Idea-wizard outputs (second-order improvements)

### I-1: <title>
- Statement: <...>
- Lifts: <dims>
- Estimated uplift: <N> pts
- Effort: <S|M|L>
- Risk: <...>

---

## Pass <N+1> focus

1. <recommendation cluster>
2. <recommendation cluster>

Estimated effort: <X agent-hours> at <tier>.

---

## Land-the-plane status

- [ ] sibling pushed (commit <sha>)
- [ ] target feature branch pushed (no merge to main)
- [ ] beads created for queued work (count: <N>)
- [ ] manifest updated with `pass_<N+1>_ready: <bool>`

## Open questions for the user

(none, or list)

---

## How to resume

1. Read this file.
2. Run `<SKILL>/scripts/discover-cli.sh <TARGET>` to confirm the binary exists.
3. Run `<SKILL>/scripts/validate_pass.sh <SIBLING>` to confirm artifact integrity.
4. Pick a mode for Pass <N+1> from `references/methodology/OPERATING-MODES.md`.
5. Send the matching kickoff prompt from `references/methodology/KICKOFF-PROMPTS.md § Resumed-pass kickoff`.
