# Continuous Refactor — operationalizing the skill as a monthly habit

> One-shot refactor passes fix the present. Continuous refactor keeps code healthy through every future feature. This file wires the skill into the team's regular cadence — pre-commit hooks, CI gates, weekly backlog, monthly deep pass.

## Contents

1. [The four layers of continuous refactor](#the-four-layers-of-continuous-refactor)
2. [Layer 1 — pre-commit hooks](#layer-1--pre-commit-hooks)
3. [Layer 2 — CI gates](#layer-2--ci-gates)
4. [Layer 3 — the weekly 1-hour pass](#layer-3--the-weekly-1-hour-pass)
5. [Layer 4 — the monthly deep pass](#layer-4--the-monthly-deep-pass)
6. [Backlog management via beads + bv](#backlog-management-via-beads--bv)
7. [Metrics trend dashboard](#metrics-trend-dashboard)
8. [Anti-pattern: the "big cleanup sprint"](#anti-pattern-the-big-cleanup-sprint)

---

## The four layers of continuous refactor

```
┌────────────────────────────────────────────────────────────────┐
│                  CONTINUOUS REFACTOR LAYERS                    │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│ 1. PRE-COMMIT HOOKS     (cost: seconds, catches: additions)    │
│    - block new any / unwrap / console.log / defensive code     │
│    - block sed/codemod (no-script enforcement)                 │
│    - block deletions without marker                            │
│                             │                                  │
│                             ▼                                  │
│ 2. CI GATES             (cost: minutes, catches: drift)        │
│    - warning count ≤ ceiling                                   │
│    - duplication index ≤ ceiling                               │
│    - LOC growth within envelope                                │
│    - slop_detector findings ≤ ceiling                          │
│                             │                                  │
│                             ▼                                  │
│ 3. WEEKLY 1-HOUR PASS   (cost: 1h/week, catches: accumulation) │
│    - pick 1-2 top beads from rescue/refactor labels            │
│    - score + prove + collapse + verify                         │
│    - ship as normal PRs                                        │
│                             │                                  │
│                             ▼                                  │
│ 4. MONTHLY DEEP PASS    (cost: half-day, catches: patterns)    │
│    - run full skill loop on one module/crate/feature           │
│    - multi-agent swarm if ≥5 candidates                        │
│    - update metrics trend dashboard                            │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

Each layer catches what the layer below misses.

---

## Layer 1 — pre-commit hooks

Configure via [cc-hooks](../../cc-hooks/SKILL.md) or standard `pre-commit` framework. Each hook is fast (<1 second) and blocks the commit.

### Example `.git/hooks/pre-commit` (or via `pre-commit.com`)

```bash
#!/usr/bin/env bash
# block additions of known pathologies

set -euo pipefail

# New `any` type additions in TS?
added_any=$(git diff --cached --unified=0 -- '*.ts' '*.tsx' \
  | grep -E '^\+' | grep -v '^\+\+\+' \
  | grep -cE ':\s*any\b|<any>|\bas any\b' || true)
if (( added_any > 0 )); then
  echo "❌ commit adds $added_any new \`any\` type sites"
  exit 1
fi

# New `.unwrap()` in Rust?
added_unwrap=$(git diff --cached --unified=0 -- '*.rs' \
  | grep -E '^\+' | grep -v '^\+\+\+' \
  | grep -cE '\.unwrap\(\)' || true)
if (( added_unwrap > 0 )); then
  echo "❌ commit adds $added_unwrap new \`.unwrap()\` sites"
  echo "   use \`.expect(\"reason\")\` or return Result"
  exit 1
fi

# New console.log / println! / dbg!?
added_debug=$(git diff --cached --unified=0 \
  | grep -E '^\+' | grep -v '^\+\+\+' \
  | grep -cE 'console\.(log|debug)|dbg!|eprintln!' || true)
if (( added_debug > 0 )); then
  echo "❌ commit adds $added_debug debug-print statements"
  exit 1
fi

# File deletion without refactor/_to_delete/ marker?
deleted=$(git diff --cached --name-only --diff-filter=D | grep -v '^refactor/_to_delete/' || true)
if [[ -n "$deleted" ]]; then
  echo "❌ commit deletes files without staging via refactor/_to_delete/"
  echo "   see references/DEAD-CODE-SAFETY.md"
  echo "   deleted: $deleted"
  exit 1
fi

# New defensive coding reflex comment?
if git diff --cached | grep -q 'defensive coding'; then
  echo "⚠️  commit contains the phrase 'defensive coding' — review per VIBE-CODED-PATHOLOGIES.md"
  # warn, don't block
fi

exit 0
```

### Pre-commit philosophy

- **Block additions of known pathologies** — it's always easier to prevent than to remove.
- **Never block on count of existing pathologies** — that's CI's job (layer 2).
- **Warnings for judgment calls, blocks for rules** — the "defensive coding" phrase warns; `.unwrap()` and deletion block.

### Via the skills ecosystem

See [cc-hooks](../../cc-hooks/SKILL.md) for full hook configuration including PreToolUse (for intercepting Edit/Write/Bash during agent sessions) and PostToolUse (for auditing).

---

## Layer 2 — CI gates

Runs on every PR. Uses `metrics_snapshot.sh` + `ai_slop_detector.sh` to compare PR against main.

### GitHub Actions example

```yaml
# .github/workflows/refactor-gates.yml
name: Refactor Gates
on: [pull_request]

jobs:
  metrics:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }

      - name: Checkout main for baseline
        run: |
          git worktree add /tmp/main main
          cd /tmp/main
          ./.claude/skills/simplify-and-refactor-code-isomorphically/scripts/metrics_snapshot.sh main-baseline > /tmp/main_metrics.json

      - name: Metrics on PR
        run: ./.claude/skills/simplify-and-refactor-code-isomorphically/scripts/metrics_snapshot.sh pr-head > /tmp/pr_metrics.json

      - name: Compare and gate
        run: |
          python3 <<'PY'
          import json
          base = json.load(open('/tmp/main_metrics.json'))
          head = json.load(open('/tmp/pr_metrics.json'))
          failures = []

          if head.get('warnings', 0) > base.get('warnings', 0):
              failures.append(f"warnings grew: {base['warnings']} -> {head['warnings']}")
          if head.get('dup_pct', 0) > base.get('dup_pct', 0) + 0.5:
              failures.append(f"duplication grew: {base['dup_pct']}% -> {head['dup_pct']}%")
          bloc = base.get('loc') or 0
          hloc = head.get('loc') or 0
          if bloc and hloc > bloc * 1.15:
              failures.append(f"LOC grew >15%: {bloc} -> {hloc}")

          if failures:
              print("\n".join(failures))
              exit(1)
          PY

      - name: AI-slop regression check
        run: |
          ./.claude/skills/simplify-and-refactor-code-isomorphically/scripts/ai_slop_detector.sh src pr-slop
          # count pathology lines; compare to main
          pr_slop=$(wc -l < refactor/artifacts/pr-slop/slop_scan.md)
          cd /tmp/main
          ./.claude/skills/simplify-and-refactor-code-isomorphically/scripts/ai_slop_detector.sh src main-slop
          main_slop=$(wc -l < refactor/artifacts/main-slop/slop_scan.md)
          (( pr_slop <= main_slop + 10 )) || { echo "slop grew by more than 10 lines"; exit 1; }
```

### Gate philosophy

| Gate | Hard fail | Soft warning |
|------|-----------|--------------|
| warning count grew | yes | — |
| `any` count grew | yes | — |
| duplication % grew > 0.5pp | yes | — |
| LOC grew > 15% | — | yes (might be a legit feature PR) |
| bundle grew > 5% | yes (frontend only) | — |
| slop_scan grew > 10 findings | — | yes |
| a file was deleted not via `_to_delete/` | yes | — |

Hard fails block merge. Soft warnings show in the PR comment but don't block.

---

## Layer 3 — the weekly 1-hour pass

Cadence: once per week, any developer.

### The 1-hour recipe

```
0:00  — bv --robot-triage | jq '.recommendations[0:2]'
        Pick 1-2 top refactor-labeled beads.

0:05  — Open the first bead. Read the isomorphism card if it's already been scored.
        If not scored, score it: ./scripts/score_candidates.py

0:10  — Fill isomorphism card: ./scripts/isomorphism_card.sh <bead>
        Every row. No N/A without thought.

0:20  — Make the edit. Edit tool only. One lever.

0:40  — ./scripts/verify_isomorphism.sh <run>
        If any gate fails: roll back, file a reason into the bead, move to the next.

0:50  — Commit. Ledger row. PR.

0:55  — If time, do the second bead.
1:00  — Done.
```

### What counts as a good weekly bead?

- **Score ≥ 2.0** per the Opportunity Matrix.
- **Scope fits in 30 min** of actual work.
- **Rung 1-2** on the abstraction ladder (mechanical or parameterize).
- **Not cross-cutting** — one module, one concern.

Tier-3 architectural refactors don't fit in a weekly pass. They need the monthly deep pass + a planning doc.

### Anti-pattern: weekly passes growing into hours

If you find yourself at 0:40 and not done, **stop and ship a partial fix or revert**. The weekly pass is a habit; if it's painful, the habit dies. Small wins compound.

---

## Layer 4 — the monthly deep pass

Cadence: one afternoon per month, or per module when it needs attention.

### The deep pass recipe

```
1. Phase 0 (bootstrap): ./scripts/check_skills.sh → ./scripts/install_missing_skills.sh
2. Phase A (baseline): full test + goldens + LOC + metrics snapshot
3. Phase B (map): ./scripts/dup_scan.sh + ./scripts/ai_slop_detector.sh
4. Phase C (score): ./scripts/score_candidates.py
5. Phase D (prove): isomorphism card per accepted candidate
6. Phase E (collapse): one lever per commit, optionally multi-agent swarm
7. Phase F (verify): ./scripts/verify_isomorphism.sh every gate
8. Phase G (ledger + dashboard)
9. Hand off: file follow-up beads for rejected candidates
```

See [METHODOLOGY.md](METHODOLOGY.md) for the full per-phase detail. [AGENT-COORDINATION.md](AGENT-COORDINATION.md) if running multi-agent.

### Deep pass targets

| Pass | Scope | Typical outcomes |
|------|-------|------------------|
| January | auth/session module | 300 LOC removed, 2 Tier-3 candidates filed |
| February | UI component library | 800 LOC removed (Button variant collapse etc.) |
| March | error-handling / logging | 200 LOC removed, `thiserror` adopted across 3 crates |
| April | data model unification | 500 LOC removed, 1 schema migration |
| ... | | |

One module per month keeps the surface focused. Over a year, the whole codebase gets attention.

---

## Backlog management via beads + bv

### Label taxonomy

```bash
# rescue-era beads
br create --title "..." --label rescue --label <phase-id>

# continuous-refactor-era beads
br create --title "..." --label refactor --label <pathology-id>   # e.g., P5, P19
br create --title "..." --label refactor --label <tier>           # tier-1 / tier-2 / tier-3

# follow-up from deep passes
br create --title "..." --label refactor --label followup --label <run-id>

# graduated: became blocking for a feature
br update <id> --label feature-blocker
```

### Triage via bv

```bash
bv --robot-triage --label refactor
# returns top-N candidates scored by (PageRank × priority × freshness) / complexity
```

bv understands the graph of dependencies between beads, so:
- `refactor/D1` blocks `refactor/D4` → D1 surfaces before D4.
- `refactor/D7` blocks 3 feature beads → D7 is graduated to feature-blocker and surfaces high.

### Weekly reviewer

One person (rotating) runs `bv --robot-triage --label refactor` each Monday, picks the top 2 beads, and either works them or assigns them.

---

## Metrics trend dashboard

Over months, the metrics series in `refactor/history/series.jsonl` (see [METRICS-DASHBOARD.md §Historical series](METRICS-DASHBOARD.md#historical-series)) tells the story.

### What a healthy trend looks like

```
Month    LOC      Dup%   Warnings   Bundle   Prop-tests
Jan      28,413   6.2    47         142      14
Feb      28,062   3.8    28         138      22
Mar      27,891   3.2    18         137      35
Apr      27,502   2.9    12         135      48
May      27,245   2.8    8          134      61
Jun      26,980   2.6    5          133      79
```

Monotone-decreasing LOC / duplication / warnings. Monotone-increasing property tests. The absolute numbers matter less than the trend direction.

### What an unhealthy trend looks like

```
Month    LOC      Dup%   Warnings   Bundle   Prop-tests
Jan      28,413   6.2    47         142      14
Feb      30,015   6.5    52         148      14
Mar      32,800   6.8    61         155      13
Apr      35,190   7.4    78         163      12
```

Feature work is outpacing cleanup. Property tests falling means the safety net is eroding. This is the signal to **increase** the deep-pass cadence, not skip it.

### Visualize

```bash
# Simple gnuplot
cat refactor/history/series.jsonl \
  | jq -r '[.ts, .loc, .dup_pct, .warnings] | @tsv' \
  | gnuplot -p -e "set title 'Refactor trend'; plot '-' u 1:2 w l t 'LOC'"
```

Or use [interactive-visualization-creator](../../interactive-visualization-creator/SKILL.md) for an HTML dashboard.

---

## Anti-pattern: the "big cleanup sprint"

A team's CTO declares "we're going to spend next sprint cleaning tech debt!" Everyone rubs their hands, then:

- 30 simultaneous refactors land in one week.
- Every developer's open PR hits merge conflicts.
- Regressions slip through because each PR individually passes but collectively breaks.
- The next sprint's feature work is blocked while everything restabilizes.
- "Cleanup" becomes a dirty word for 6 months.

**The continuous approach avoids this entirely.** Each of the four layers is small, cheap, and steady. No sprint required. No emergency.

If you inherit a codebase that needs a "big cleanup sprint" — run the rescue missions playbook ([RESCUE-MISSIONS.md](RESCUE-MISSIONS.md)) instead. Shorter, focused, stays non-hostile.

---

## Bootstrap: adopting continuous refactor from day 1

If this is a new project or you're bolting continuous refactor onto an existing one:

### Week 1
- Install pre-commit hooks (layer 1)
- Run `metrics_snapshot.sh` and commit the baseline
- Add CI gates (layer 2) that enforce "no worse than baseline"

### Week 2
- Run one 1-hour weekly pass (layer 3)
- File a few beads for what you notice

### Week 3
- Continue weekly
- Ensure the trend line is going the right direction

### Month 2
- Schedule the first monthly deep pass (layer 4)
- Pick the module with the highest pathology density per `ai_slop_detector.sh`

### Month 3+
- Cadence is established. Trend should be visible.

If after 3 months the trend isn't visible, the problem isn't cadence — it's that feature velocity is masking the cleanup. Increase the deep-pass frequency or the per-pass scope.
