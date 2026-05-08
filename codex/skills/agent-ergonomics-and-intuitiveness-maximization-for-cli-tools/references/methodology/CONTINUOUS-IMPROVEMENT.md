# CONTINUOUS-IMPROVEMENT — Periodic re-audits beyond Pass-N

A single audit pass produces strong uplift, but tools drift. New verbs appear; new flags get added; CI behavior subtly shifts. Continuous improvement turns the audit workspace into a long-lived, low-maintenance backstop.

This file gives the playbook for ongoing re-audits.

---

## Cadence

| Cadence | When |
|---------|------|
| **PR-time** (every PR) | Run `audit/regression_tests/*.test.sh` via CI (see `CI-INTEGRATION.md`) |
| **Weekly** | Run `re-score-only` against current HEAD; flag regressions; auto-open issues |
| **Monthly** | Run `simulate-only` with fresh-context agent; capture canonical-task transcripts; compare to baseline |
| **Quarterly** | Full Pass-N+1 audit with idea-wizard outputs; expect 1-3 new recommendations per quarter |
| **Annually** | Refresh the rubric (rubric_version bump if needed); re-validate canonical tasks; review CASS findings |

---

## Weekly: scheduled re-score

Add a GitHub Action (or equivalent):

```yaml
name: Weekly Agent-Ergo Re-Score

on:
  schedule:
    - cron: '0 12 * * 0'    # Sunday noon UTC
  workflow_dispatch:        # manual trigger

jobs:
  rescore:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }     # for SHA comparisons

      - name: Build binary
        run: cargo build --release

      - name: Re-score current HEAD
        id: rescore
        run: |
          export TOOL_BIN=$(pwd)/target/release/mytool

          # `date -d` is GNU-specific; on BSD/macOS the runner uses `date -v`.
          last_week=$(date +%Y%m%d --date='7 days ago' 2>/dev/null || date -v-7d +%Y%m%d)
          today=$(date +%Y%m%d)

          for surface_id in $(jq -r '.surface_id' audit/agent_surfaces.jsonl | sort -u); do
            bash audit/scripts/rescore_surface.sh "$surface_id" >> "audit/agent_surfaces_pass_${today}.jsonl"
          done

          # diff_scorecards exits 3 on hard-stop regression (drop > 50 pts)
          set +e
          bash audit/scripts/diff_scorecards.sh \
            "audit/agent_surfaces_pass_${last_week}.jsonl" \
            "audit/agent_surfaces_pass_${today}.jsonl" \
            > audit/uplift_diff_weekly.md
          diff_exit=$?
          set -e

          # Surface the result for the next step.
          # `[ -eq 3 ] && X` would fail under set -e when diff_exit != 3; use if/then.
          hard_stop=0
          if [ "$diff_exit" -eq 3 ]; then
            hard_stop=1
          fi
          echo "hard_stop=$hard_stop" >> "$GITHUB_OUTPUT"

      - name: Open issue on regression
        if: steps.rescore.outputs.hard_stop == '1'
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const body = fs.readFileSync('audit/uplift_diff_weekly.md', 'utf8');
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: `[agent-ergo] Weekly re-audit found regressions`,
              body: body,
              labels: ['agent-ergonomics', 'regression']
            });
```

If no regressions, no issue is opened. Quiet weeks are good.

---

## Monthly: fresh-context simulation

Once a month, spawn the fresh-context simulator (per `subagents/canonical-task-simulator.md`) on the current binary:

```bash
# audit/scripts/monthly-simulation.sh
SIB="$(pwd)"
PASS=$(jq -r '.current_pass' audit/manifest.json)
SIM_DIR="audit/agent_simulations/post_pass_${PASS}_$(date +%Y%m)"
mkdir -p "$SIM_DIR"

# Spawn the simulator (via Claude Code Agent or scheduled remote agent)
# capture transcripts
```

Compare the new month's transcripts to the prior baseline:

- Did first-try success rate change?
- Did median round-trips change?
- Did any task become "stuck"?

If anything regressed, file an issue. If everything is stable, log "monthly simulation: no change" in `audit/HANDOFF.md`.

---

## Quarterly: full Pass-N+1

Once a quarter, run the full audit pipeline:

```
Phase 0 (resumed) → Phase 1 (incremental) → Phase 2 (full re-score)
                  → Phase 3 (refresh corpus)
                  → Phase 4 (synthesize new recs)
                  → Phase 5 (apply top-N if mode=full)
                  → Phase 6 (uplift)
                  → Phase 7 (fresh-eyes)
                  → Phase 8 (self-doc hardening)
                  → Phase 9 (simulation)
                  → Phase 10 (handoff)
```

Quarterly cadence balances signal with cost. Tools that change rapidly may need monthly Pass-N+1; stable tools can stretch to semi-annual.

---

## Annually: rubric refresh

Once a year, review the rubric:

1. Are the 11 dimensions still the right ones? (CASS findings may suggest a 12th — e.g. "telemetry transparency.")
2. Are the anchor levels (0/250/500/750/1000) still calibrated against current canonical exemplars?
3. Have any new exemplars emerged that should anchor 750+ levels?
4. Have any anti-patterns become obsolete?
5. Is the priority formula still appropriate? (Maybe `effort` should be a fourth factor.)

The rubric is a **living artifact** ([Q-1003]). Annual refresh keeps it relevant.

When refreshing:

```bash
# 1. Edit references/rubric/SCORING-RUBRIC.md
# 2. Bump rubric_version in audit/manifest.json
# 3. Re-score everything against the new rubric (Pass-N+1)
# 4. Document the change in audit/HANDOFF.md
```

Don't refresh the rubric mid-pass — that breaks comparisons.

---

## Trigger-based re-audit

In addition to cadence, run a re-audit when:

- **A new exemplar is identified.** If the user finds a CLI that does something better than any current exemplar, add it to `CANONICAL-EXEMPLARS.md` and check if any current scores need refresh.
- **A regression is reported.** A user / agent reports that a feature regressed; run `single-surface-rescore` to confirm and triage.
- **A new framework version drops.** Major clap / cobra / argparse releases sometimes change defaults; re-audit the affected dim.
- **A breaking change ships.** After landing any deprecation stage, re-audit the affected verbs.
- **CASS surfaces a new failure pattern.** If quarterly CASS mining finds a new theme not previously seen, refresh CASS-FINDINGS.md and re-prioritize.

---

## Maintenance discipline

The audit workspace lives across passes. To keep it sustainable:

1. **Keep `audit/regression_tests/` green at all times.** A red test in CI = a real regression.
2. **Don't accumulate stale artifacts.** Old `agent_surfaces_pass_<old>.jsonl` files can stay for history but should be compressed or moved to `audit/.archive/` after 4+ passes.
3. **Capabilities golden file is sacred.** Update only when `contract_version` is bumped.
4. **HANDOFF.md is the front door.** Keep it current; future agents (and humans) read it first.

---

## Multi-tool families: ongoing alignment

For families (per `MULTI-TOOL-FAMILY-AUDIT.md`):

- Per-binary cadence (weekly re-score, etc.) PLUS
- Family cross-cut cadence (monthly): re-validate exit-code consistency, envelope consistency, capabilities cross-references

If one binary in the family ships a breaking change without the others, the family cross-cut score regresses. Catch it monthly.

---

## Continuous improvement metrics

Track over time in `audit/metrics_timeseries.md`:

```markdown
# Continuous Improvement Metrics

## Median weighted score over time

| Date       | Pass | Median weighted | Surfaces above bar | Notes |
|------------|------|------------------|---------------------|-------|
| 2026-04-01 | 1    | 750              | 28/50 (56%)         | initial pass |
| 2026-05-06 | 2    | 820              | 35/50 (70%)         | applied U-1..U-6 |
| 2026-06-01 | 2 (re-score) | 815          | 35/50 (70%)         | weekly check; -5 on flag__verbose; investigated; no action |
| 2026-07-01 | 3    | 850              | 41/50 (82%)         | quarterly Pass-N+1; added I-2, I-3 from idea-wizard |
| 2026-08-01 | 3 (re-score) | 850          | 41/50 (82%)         | stable |
| ...        |      |                  |                     |       |
```

Use this as the basis for engineering reviews / OKRs / "is the tool getting better for agents?" questions.

---

## Sunset criteria

When to stop continuous improvement:

- The tool is being deprecated
- All surfaces score 1000 (rare; usually not a stable target)
- The user has migrated to a different tool

For deprecated tools: do one final pass marking everything as "frozen"; update HANDOFF.md to note the freeze; stop weekly re-scores.

---

## Compounding effect

The accumulated value from continuous improvement compounds:

- Pass 1 → +70 median pts
- Pass 2 → +30 (applying deferred recs)
- Pass 3 → +15
- Pass 4 → +10
- Pass 5+ → +5 each

After 5 passes (~1.25 years quarterly cadence), the median score sits 130+ points above pre-audit baseline. The tool feels qualitatively different to agents.

---

## Related

- `CI-INTEGRATION.md` — PR-time guards (the foundation)
- `HOOKS-INTEGRATION.md` — pre-commit guards
- `OPERATING-MODES.md` — modes for re-audit (`re-score-only`, `simulate-only`)
- `CASS-MINING-RECIPES-DEEP.md` — periodic CASS refresh
