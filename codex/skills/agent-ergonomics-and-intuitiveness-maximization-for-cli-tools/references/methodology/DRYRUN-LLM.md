# Dry-Run LLM Harness

The `scripts/dryrun-llm.sh` harness is the bridge between "we built this skill" and "we know it works." It runs a small, budgeted subset of the Phase 2 scorer pipeline so you can validate the prompt, rubric, and output format before committing to a full pass.

## Why a dry-run

Every prior round added infrastructure assuming the LLM scorer path works. None of those rounds actually invoked Claude. The dry-run is the first time the rubric, the scorer prompt, and the aggregator meet a real CLI under real API conditions. Expect surprises:

- Prompts that produced nice output on synthetic input may fail real one.
- Scorers may anchor on the wrong sentence and produce systematically biased scores.
- Token counts may exceed estimates (prompt + tool material + history can be 3-5x larger than naive estimates).
- Inter-rater agreement may be much lower than expected, requiring tiebreaker.

A $5 dry-run on 10 surfaces surfaces these issues at 1/100th the cost of finding them in a $500 full pass.

## Two modes

### `--mode stub`

Uses `scripts/stub-scorer.sh` to produce deterministic synthetic scores. NO API CALLS. Use this to:

- Verify the harness itself runs end-to-end.
- Confirm aggregation, schema validation, and inter-rater spread calculation work.
- Test the verifier on known-good and known-bad inputs.

The stub seeds scores from `sha256(surface_id, scorer_id) % 1001` so re-runs are reproducible. Stub output is clearly marked in transcripts via `mode: stub` and rubric_version `stub-1.0.0`.

### `--mode claude`

Spawns the real `agent-ergo-scorer` subagent (defined in `subagents/scorer.md`) via the parent agent's `Task` tool. This script CANNOT spawn subagents itself — the parent agent (Claude Code or equivalent) must do it. The script emits the exact kickoff arguments the parent should pass.

The flow:

1. Run `scripts/dryrun-llm.sh <sibling> --surfaces 10 --mode claude` once with `--budget-usd` set.
2. The script samples surfaces and prints `PARENT-AGENT-MUST-RUN` blocks listing each (surface_id, scorer_id) pair to spawn.
3. The parent agent spawns each scorer subagent via `Task` with those inputs, ensuring outputs land at `<workdir>/partial/scores_pass1_<sid>_scorer<X>.jsonl`.
4. Once all are complete, re-run `scripts/dryrun-llm.sh <sibling> --workdir <same-workdir> --skip-spawn` (NOT YET IMPLEMENTED — currently re-running re-samples surfaces).
5. Or invoke `scripts/aggregate_scores.sh <workdir>` and `scripts/dryrun-verify.sh <workdir>` separately.

## Budget gating

The script projects cost as `n_surfaces × 2 scorers × $0.50/scorer` (claude mode; tune as you measure real costs). If projected exceeds `--budget-usd`, the script halts before any work. To raise: pass `--budget-usd 20`. To lower the projection: pass `--surfaces 5`.

The $0.50/scorer projection is a starting estimate. AFTER the first claude-mode run, replace it with the measured value from `audit/telemetry.jsonl` (subagent=scorer aggregate). Round-M includes a follow-up to auto-calibrate this.

## Post-conditions verified

`scripts/dryrun-verify.sh` checks:

1. **JSONL well-formedness:** every partial file parses.
2. **Score range:** all values in [0, 1000].
3. **Evidence discipline:** every dim score > 700 has corresponding `evidence.<dim>`.
4. **Inter-rater spread:** max per-dim (max − min) per surface; WARN ≥ 200, FAIL ≥ 350.
5. **Schema conformance:** aggregated `agent_surfaces.dryrun.jsonl` validates against `assets/schemas/agent_surfaces.schema.json`.

If any FAIL, the script exits 1 and the report is written to `<workdir>/dryrun-report.md`.

## Recommended workflow

1. **Validate the harness offline.** `dryrun-llm.sh <sibling> --mode stub --surfaces 10`. Should produce a PASS verdict in < 5 seconds.

2. **Run a tiny real test.** `dryrun-llm.sh <sibling> --mode claude --surfaces 4 --budget-usd 2`. Spawn the printed scorer prompts via the parent agent. Inspect the output.

3. **Inspect inter-rater spread.** If multiple surfaces show spread > 200, the rubric anchors are too vague — open `references/rubric/SCORING-RUBRIC.md` and tighten the language before scaling up.

4. **Inspect evidence quality.** Open 3-5 transcripts; do the cited evidence excerpts actually justify the scores? If not, the prompt needs to insist on better citations.

5. **Scale up.** Once a 4-surface dry-run shows good spread and good evidence, run a 10-surface dry-run. If still good, you're ready for a full pass.

6. **Calibrate cost projection.** Look at `<workdir>/transcripts/`; total tokens across all calls divided by 2 × n_surfaces gives real $/scorer. Update `dryrun-llm.sh`'s `per_surface_usd` constant.

## What dry-run does NOT validate

- Phase 4 (recommendation generation) — separate dry-run needed.
- Phase 5 (applier) — separate dry-run needed.
- Long-context behavior — small surfaces don't stress 200K windows.
- Cross-tool generalization — calibrating on bv doesn't tell you about gh.

But Phase 2 is the foundation. If Phase 2 is broken, nothing downstream is meaningful. Get Phase 2 right first.
