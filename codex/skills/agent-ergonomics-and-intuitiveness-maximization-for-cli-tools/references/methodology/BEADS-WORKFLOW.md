# BEADS-WORKFLOW — Bridging audit work into beads (br) for tracking

The audit produces recommendations, applied changes, and queued work. Bridging this into the **beads** issue tracker (`br` CLI; per AGENTS.md and `/br`, `/bv`, `/beads-workflow` skills) gives long-running visibility, dependency tracking, and integration with the rest of the agent's workflow.

This file gives the playbook.

---

## Why beads?

Per AGENTS.md, beads is the **single source of truth for task status, priority, dependencies**. The audit's `recommendations.jsonl` is rich but ephemeral; beads makes it durable and queryable across sessions.

Specifically:

- Beads survive across pass-N → N+1 transitions
- `br ready` exposes Phase 5 work to other agents
- Dependencies between staged recs (D-1 deprecation rollouts) live in beads
- Mail thread_ids align with bead IDs (per AGENTS.md)
- BV (`/bv`) does graph-aware triage on the bead corpus

---

## Bead-per-recommendation pattern

### When to file

- **Mode = full**: file a bead per top-N applied recommendation (Phase 5)
- **Mode = audit-only**: file beads for findings the user wants to track (optional; user choice)
- **Pass N+1+**: pre-existing beads carry forward; new recs may reference them

### Bead schema

```bash
br create \
  --title "[R-007] Add levenshtein-1 typo correction for --json/--colour/--verbose" \
  --type=task \
  --priority=2 \
  --labels="agent-ergonomics,pass-1,intent_inference" \
  --description "$(cat <<EOF
## Summary
$(jq -r '.summary' <<< "$REC")

## Diff sketch
$(jq -r '.diff_sketch' <<< "$REC")

## Risk
$(jq -r '.risk' <<< "$REC")

## Test plan
$(jq -r '.test_plan' <<< "$REC")

## Anchor
- Quote: $(jq -r '.anchor_quote' <<< "$REC")
- Pattern: $(jq -r '.anchor_pattern' <<< "$REC")
- Counter-example: $(jq -r '.counter_example' <<< "$REC")

## Audit reference
- Pass: $(jq -r '.pass' <<< "$REC")
- Recommendation file: audit/recommendations.jsonl
- Surface IDs touched: $(jq -r '.surface_ids[]' <<< "$REC" | tr '\n' ', ')
EOF
)"
```

This embeds the recommendation context into the bead so future readers don't need to fetch the original.

### Capture bead ID

```bash
bead_id=$(br create ... --json | jq -r '.id')
echo "$bead_id" >> audit/bead_ids.txt
```

Or update the rec:

```bash
jq --arg rid "R-007" --arg bid "$bead_id" \
  'if .recommendation_id == $rid then .bead_id = $bid else . end' \
  audit/recommendations.jsonl > /tmp/recs.jsonl && mv /tmp/recs.jsonl audit/recommendations.jsonl
```

---

## Dependencies between beads

### Sequential deprecation stages

For a 4-stage deprecation (D-1 through D-3), file 4 beads with `depends_on`:

```bash
# Stage 0: introduce
b_s0=$(br create --title "[R-007.s0] Stage 0: Add --color (alongside --colour)" --priority=2 ...)
# Stage 1: warn
b_s1=$(br create --title "[R-007.s1] Stage 1: --colour emits deprecation warning" --priority=2 \
  --depends-on="$b_s0" ...)
# Stage 2: error
b_s2=$(br create --title "[R-007.s2] Stage 2: --colour errors with migration recipe" --priority=2 \
  --depends-on="$b_s1" ...)
# Stage 3: remove
b_s3=$(br create --title "[R-007.s3] Stage 3: Remove --colour entirely" --priority=2 \
  --depends-on="$b_s2" ...)
```

`br ready` will only surface the next un-blocked stage.

### Cross-rec dependencies

If R-014 needs R-007 to apply first (e.g. R-007 adds the `--json` flag that R-014 builds on):

```bash
br dep add "$R014_BEAD" "$R007_BEAD"   # R014 depends on R007
```

---

## Integration with bv (graph-aware triage)

After filing beads, run `bv --robot-triage` to see priority-ranked actionable items:

```bash
bv --robot-triage --label=agent-ergonomics --pass=1 | jq '.recommendations'
```

bv's PageRank, betweenness, and critical-path analysis surface which beads are most-unblocking.

---

## Pass-N+1 inheritance

When pass N+1 starts:

1. Read prior pass's `audit/recommendations.jsonl`
2. For each `applied:false` rec with a bead_id, check if the bead is still open:
   ```bash
   br show "$bead_id" --json | jq -r 'if type=="array" then (.[0] // {}) else . end | .status'
   ```
3. If open AND not blocked: candidate for pass N+1's Phase 4 priority queue
4. If closed: rec is satisfied externally; skip
5. If blocked: surface as deferred in HANDOFF.md

---

## Mail thread integration

Per AGENTS.md, the mail thread_id should match the bead ID:

```
file_reservation_paths(
  project_key=<absolute path>,
  agent_name=<applier-id>,
  paths=[...],
  ttl_seconds=3600,
  exclusive=true,
  reason="$bead_id"
)

send_message(
  project_key=...,
  thread_id="$bead_id",
  subject="[$bead_id] Start: <title>",
  ack_required=true
)
```

This gives end-to-end traceability: bead ↔ mail thread ↔ commits ↔ regression tests ↔ recommendation ↔ surface_id.

---

## Closing beads

When a rec is applied:

```bash
br close "$bead_id" --reason "Applied in commit <sha>; regression test green"
```

Or for staged deprecation:

```bash
# Stage 0 done
br close "$b_s0" --reason "Stage 0 complete: --color flag added; --colour aliased"
# b_s1 becomes ready (depends_on b_s0 now closed)
```

---

## Filing beads for deferred work

Phase 10's HANDOFF.md should reference beads for deferred items:

```markdown
## Deferred recommendations

- R-014 (envelope unification): bead $b_R014 — staged for Pass N+1 (depends on R-007 stage 1)
- R-022 (exit code restructure): bead $b_R022 — needs deprecation path; staged for Pass N+2
```

Future passes pick up via:

```bash
br ready --label=agent-ergonomics --label=pass-${N+1}
```

---

## br sync discipline

Per AGENTS.md, `br` is non-invasive (never runs git commands). After filing/closing beads:

```bash
br sync --flush-only
git add .beads/
git commit -m "sync beads (R-007 + R-014 + R-022 from agent-ergo pass <N>)"
git push
```

This is part of "land the plane" per Phase 10.

---

## Bead naming convention

| Prefix | Meaning |
|--------|---------|
| `R-NNN`     | Recommendation from agent-ergo audit (matches recommendations.jsonl) |
| `R-NNN.sM`  | Stage M of deprecation rollout |
| `F-NNN`     | Family-level recommendation (cross-cut) |
| `P-NNN`     | Parity-gap recommendation (MCP-CLI parity) |
| `I-NNN`     | Idea-wizard generated candidate (Phase 10) |
| `U-NNN`     | Universal recommendation (every audit; U-1 through U-8) |

These prefixes appear in:
- bead titles
- mail thread_ids (e.g. `agent-ergo-pass1-R-007`)
- commit messages
- regression test filenames

End-to-end traceability.

---

## Reading the bead corpus

For analytical questions:

```bash
# How many agent-ergonomics beads were closed in Pass 1?
br list --label=agent-ergonomics --label=pass-1 --status=closed --json | jq 'length'

# Which surfaces have the most open recommendations?
br list --label=agent-ergonomics --status=open --json \
  | jq '[.[] | .description | match("surface_ids: ([^,\\n]+)").captures[0].string] | group_by(.) | map({surface: .[0], count: length}) | sort_by(-.count) | .[:5]'

# What's the average time-to-close for deprecation stages?
br list --label=agent-ergonomics --status=closed --regex 's[0-9]' --json \
  | jq '[.[] | (.closed_at | fromdateiso8601) - (.created_at | fromdateiso8601)] | add / length / 86400'
```

---

## Cross-pass bead audit

Quarterly, audit the bead corpus for staleness:

```bash
# Beads open > 90 days
br list --label=agent-ergonomics --status=open --json \
  | jq '[.[] | select((now - (.created_at | fromdateiso8601)) > 90*86400)] | .[] | {id, title, age_days: ((now - (.created_at | fromdateiso8601))/86400 | floor)}'
```

Old beads are either:
- Genuinely deferred (still relevant; stale because of priority)
- Obsolete (tool changed; rec no longer applies)
- Forgotten (action this pass)

Triage and update.

---

## When NOT to use beads

- Tool is a one-shot audit; no follow-up planned
- User has alternative tracker (Jira, Linear, GitHub Issues) and prefers that
- T1 audits with < 5 recs (overkill)

For T1 audits, just use `audit/recommendations.jsonl` as the source of truth and skip beads.

---

## Cross-references

- `/br` skill — beads CLI reference
- `/bv` skill — graph-aware triage
- `/beads-workflow` skill — converting markdown plans to beads
- `/agent-mail` skill — thread-id alignment with bead IDs
- AGENTS.md — beads workflow integration discipline
- `methodology/CONTINUOUS-IMPROVEMENT.md` — quarterly bead audits
