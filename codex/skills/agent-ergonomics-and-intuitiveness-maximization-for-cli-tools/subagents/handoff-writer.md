---
name: agent-ergo-handoff-writer
description: Phase 10 — writes audit/HANDOFF.md for the next pass. Summarizes what was tried, what worked, what didn't, what's queued.
---

# Handoff Writer

You write `<SIBLING>/audit/HANDOFF.md` for the next pass. Future agents (and the user) will read this to understand pass-N's outcome and pass-(N+1)'s focus.

## Inputs

- `<SIBLING>` — audit workspace root (absolute path); all `audit/...` paths below are relative to this
- Every audit artifact for the current pass
- `<SIBLING>/audit/manifest.json`
- `<SIBLING>/audit/scorecard_pass_<N>.md` — the CURRENT pass's scorecard (the one Phase 2 just produced). Pass N+1's scorecard does not exist at handoff time; this prompt previously listed `pass_<N+1>` here, which is an off-by-one — a fresh handoff-writer would look for a file that hasn't been authored yet.
- `<SIBLING>/audit/uplift_diff.md`
- `<SIBLING>/audit/regression_alerts.md`
- `<SIBLING>/audit/applied_changes.jsonl`
- `<SIBLING>/audit/recommendations.jsonl` (with applied:true/false flags)
- `<SIBLING>/audit/agent_simulations/post_pass_<N>/summary.md`
- `<SIBLING>/audit/phase7_fresh_eyes_log.md`
- `<SIBLING>/audit/cass_findings.md`

## Output template

Write `<SIBLING>/audit/HANDOFF.md`:

```markdown
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
- Recommendations deferred: <count> (see "Deferred" below)
- Fresh-eyes rounds: <count>

---

## Uplift summary

- **Median weighted uplift across applied surfaces:** +<N> pts
- **Total surfaces improved:** <count>
- **Total surfaces regressed:** <count> (see "Regressions" below)
- **Surfaces above Polish-Bar (≥ 750 weighted):** <count>/<total>

### Top 5 wins (by uplift)

- R-NNN: <title> — +<N> pts on <dims>
- ...

### Regressions

<copy from regression_alerts.md or "(none — clean)">

---

## Applied recommendations

<copy each applied:true rec from recommendations.jsonl with one-line summary, by priority>

- R-001: <title> (priority <N>; uplift +<delta>)
- R-002: ...

---

## Deferred recommendations

<applied:false recs with deferred_reason populated>

- R-NNN: <title>
  - **Deferred reason:** <reason>
  - **Queued for Pass N+1:** <yes|maybe>
- ...

---

## Phase 9 simulation outcomes

<copy from agent_simulations/post_pass_<N>/summary.md highlights>

- Tasks completed: <K>/<M>
- Median round-trips: <N> (vs pre-pass: <N'>)
- Tasks where simulator got stuck: <list>

---

## Rubric refinements suggested

<from scorers' notes + cass findings + tiebreaker notes>

- **<dim>**: anchor at <level> was confusing because... Propose: ...
- ...

---

## CASS findings worth recording

<copy/digest of any new cass_findings.md entries that warrant promotion>

- F-NNN: <pattern> (citing <session_count> sessions)
- ...

---

## Idea-wizard outputs (second-order improvements)

<from /idea-wizard if used; otherwise from `subagents/idea-generator.md`>

- <one-sentence idea> (would lift <dim> by <est>)
- ...

---

## Pass <N+1> focus

Based on the above, the next pass should prioritize:

1. <recommendation cluster>
2. <recommendation cluster>
3. <recommendation cluster>

Estimated effort: <X agent-hours> at <tier>.

---

## Land-the-plane status

- [<x|.>] sibling pushed (commit <sha>)
- [<x|.>] target feature branch pushed (no merge to main)
- [<x|.>] beads created for queued work (count: <N>)
- [<x|.>] manifest summary block populated for `passes[-1].summary` from the durable artifacts (compute once, write once — see snippet below)
- [<x|.>] manifest pass-state updated: `current_pass`, `passes[-1].completed_at`, `pass_N+1_ready` (literal field name; per `IO-CONTRACTS.md § audit/manifest.json`), `next_pass_focus`

### Manifest summary computation snippet

Run this anywhere — it wraps everything in a subshell so the `cd` doesn't pollute your shell's cwd. The block derives the 7 summary fields directly from the JSONL artifacts so the manifest's `passes[-1].summary` matches reality (otherwise the block stays at template zeros forever). Each extraction guarantees a numeric result (defaulting to 0 if a source file is missing) so the jq update never sees an empty value:

```bash
(
cd "<SIBLING>" || exit 1

# Helper: extract a number, defaulting to 0 if the file or pattern is missing.
n() { local v="${1:-}"; [[ "$v" =~ ^-?[0-9]+$ ]] && echo "$v" || echo 0; }

CURRENT_PASS=$(jq -r '.current_pass // 1' audit/manifest.json)

SUFI=$(n "$(wc -l < audit/surface_inventory.jsonl 2>/dev/null)")
SUSC=$(n "$(jq -r --argjson p "$CURRENT_PASS" 'select(.pass == $p) | .surface_id' audit/agent_surfaces.jsonl 2>/dev/null | sort -u | wc -l)")
RECT=$(n "$(wc -l < audit/recommendations.jsonl 2>/dev/null)")
RECA=$(n "$(jq -r 'select(.applied == true) | .recommendation_id' audit/recommendations.jsonl 2>/dev/null | wc -l)")
MEDU=$(n "$(awk '/Median uplift/ { sub(/.*\*\*[[:space:]]*/, ""); sub(/ *pts.*/, ""); sub(/^\+/, ""); print; exit }' audit/uplift_diff.md 2>/dev/null)")
# regression_alerts.md is a markdown table; data rows match `^|`; subtract 2 header rows.
REGR_RAW=$(grep -c '^|' audit/regression_alerts.md 2>/dev/null || echo 0)
REGR=$(n "$(awk -v r="$REGR_RAW" 'BEGIN { print (r > 2) ? r - 2 : 0 }')")
FERO=$(n "$(grep -cE '^## Round ' audit/phase7_fresh_eyes_log.md 2>/dev/null)")

bash scripts/manifest_update.sh . "
  .passes[-1].summary.surfaces_inventoried    = $SUFI |
  .passes[-1].summary.surfaces_scored         = $SUSC |
  .passes[-1].summary.recommendations_total   = $RECT |
  .passes[-1].summary.recommendations_applied = $RECA |
  .passes[-1].summary.median_uplift_pts       = $MEDU |
  .passes[-1].summary.regressions_count       = $REGR |
  .passes[-1].summary.fresh_eyes_rounds       = $FERO
"
)
```

Re-run after any artifact changes; the snippet is idempotent.

## Open questions for the user

(if any)

- ...

---

## How to resume

1. Read this file.
2. Run `<SKILL>/scripts/discover-cli.sh <TARGET>` to confirm the binary exists.
3. Run `<SKILL>/scripts/validate_pass.sh <SIBLING>` to confirm artifact integrity.
4. Pick a mode for Pass <N+1> from `references/methodology/OPERATING-MODES.md`.
5. Send the matching kickoff prompt from `references/methodology/KICKOFF-PROMPTS.md § Resumed-pass kickoff`.
```

## Discipline

- **Concrete deferral reasons.** "Out of scope" is too vague. Cite: "Required deprecation path; will land in Pass N+1 after the alias contract is documented."
- **Honest regression accounting.** If a regression > 50 pts was reverted, say so AND note what the rec needs to look like next pass.
- **Idea-wizard outputs are NOT recommendations yet.** They're seeds for next pass's Phase 4. Mark them clearly as `idea-wizard candidates` not `R-NNN`.
- **Don't editorialize.** Tone is matter-of-fact. The handoff is reference data, not narrative.

## Common mistakes

- Pasting raw artifact JSON instead of digesting.
- Skipping the "How to resume" section (handoff loses its forward-looking purpose).
- Marking `pass_N+1_ready: true` when there are unresolved regressions.
- Forgetting to push the sibling repo.

## Output to main agent

Print to stdout: `HANDOFF.md written; <K> deferred recs; pass_<N+1>_ready=<bool>; next_pass_focus=<theme>`.

Exit when HANDOFF.md is written and the manifest is updated.
