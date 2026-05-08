# PIPELINE-RECOVERY.md — Recovering the audit pipeline from mid-run failures

This doc covers recovery of the **audit pipeline itself** (the 10-phase orchestration the skill drives). For recovery design of the *audited tool*, see `CRASH-RECOVERY-AND-RESUMABILITY.md`.

The audit pipeline runs 10 phases, most of which spawn parallel LLM subagents that may die mid-run from rate limits, context overflow, network errors, or user interrupt. This doc enumerates the recovery story for each phase. The phase artifacts on disk are the source of truth — there's no in-memory state that needs to survive the killed agent.

## Recovery primitives

Three patterns recur:

**(P1) Atomic-rewrite output.** Scripts and subagents that produce durable JSONL/JSON write via `tmp + flock + rename`. The reader either sees the old file in full or the new file in full, never a torn write. See `tools/flip_applied.sh`, `scripts/manifest_update.sh`, `scripts/aggregate_scores.sh` (idempotent rewrite), `scripts/synthesize_recommendations.mjs` (tmp+rename), `subagents/applier.md` step 7 (flock-guarded append), `subagents/re-scorer.md` (idempotent (sid, pass) replace).

**(P2) Single-record-per-file partials.** Subagents that write per-surface or per-scorer partials use `>` (overwrite), not `>>` (append). A re-spawned subagent's output replaces the prior one; no per-step deduplication needed. See `subagents/scorer.md`, `subagents/recommender.md`, `subagents/scorer-tiebreaker.md`.

**(P3) Per-step ledgers.** Subagents with multi-step state (notably `subagents/applier.md`'s 9-step ritual) write a ledger after each step. On respawn, they read the ledger and skip completed steps. See `applier.md` step 0.

Together, these mean: a kill -9 between any two steps leaves the workspace in a state from which the next-spawned subagent can resume cleanly without double-applying anything.

## Per-phase recovery

### Phase 0 — Bootstrap

**Killed during scaffold:** `scripts/scaffold-workspace.sh` is idempotent (per round-17 fix): re-running on an already-scaffolded sibling exits 0 without overwriting. Manifest seed write happens before `git add .`, so a re-run sees the manifest and short-circuits. Safe to re-run.

**Killed during discover-cli:** `phase0_cli.json` is overwritten on each invocation. Re-run produces a clean replacement. Safe to re-run.

### Phase 1 — Surface inventory

**Killed during inventory walk (`scripts/inventory_surfaces.sh`):** the script writes to stdout; the user redirects to `audit/surface_inventory.jsonl`. A killed run produces a partial JSONL on stdout that's NOT written to the destination if the user did `> audit/surface_inventory.jsonl` and the kill happened mid-write — bash's stdout buffer flushes incrementally, so the partial file is plausible-but-truncated. **Recovery**: re-run the entire inventory; it overwrites cleanly.

**Killed during parallel surface-inventorist subagents:** each subagent writes its own file (e.g. `partial/inventory_<subtree>.jsonl`). Per (P2), a re-spawn overwrites. Recovery: identify which subtrees are missing from the partial dir, re-spawn those subagents.

### Phase 2 — Rubric scoring

**Killed during a scorer subagent:** scorer writes `partial/scores_pass<N>_<SID>_scorer<X>.jsonl` via `>` (per P2 + scorer.md). Re-spawn overwrites. Aggregator hasn't run yet; nothing else to clean up.

**Killed during the aggregator:** `aggregate_scores.sh` is idempotent (per F4-RB1 fix in round F): re-running detects existing `(sid, pass)` rows in `agent_surfaces.jsonl` and replaces them rather than appending duplicates. Validation rejects malformed partials before promoting (per H1 fix in round H). Safe to re-run.

**Pre-pass partial collisions (Phase 6 vs Phase 2):** filenames now include `pass<N>` (per H3 fix in round H), so Phase 6 re-scorer partials don't collide with Phase 2 partials. No archiving step needed.

### Phase 3 — Intent-inference corpus

**Killed during stresser subagents:** naive and savvy stressers each write distinct files (`partial/intent_naive.jsonl` / `partial/intent_savvy.jsonl`). Per (P2), re-spawn overwrites. Generator scripts (`generate_intent_corpus.sh`) are idempotent — they truncate the output and rewrite from inventory.

**Killed during the runner (`run_intent_corpus.sh`):** the runner truncates `intent_inference_corpus.jsonl` at start and appends per-row. A killed run produces a partial JSONL with possibly-truncated final line. The runner now (per round F+G) holds an `flock -n` on `intent_inference_corpus.jsonl.lock` — a second concurrent invocation refuses to start. A killed run releases the flock when its fd closes. Recovery: re-run; the truncate-and-rewrite produces a clean output.

**Two parents accidentally launching concurrent corpus runs:** the second invocation fails fast with "another run_intent_corpus.sh is already running" (per round-G fix). Safe.

### Phase 4 — Recommendation synthesis

**Killed during a recommender subagent:** writes `partial/recommendations_<SID>.jsonl` via `>` (per P2 + recommender.md fix in round G). Re-spawn overwrites; no duplicates leak into the synthesizer.

**Synthesizer barrier (per round H H6):** before spawning `subagents/synthesizer.md` or running `scripts/synthesize_recommendations.mjs`, the main agent MUST verify every below-quartile surface has a non-empty partial file. If any are missing, re-spawn the recommender for that surface BEFORE starting synthesis. Otherwise the synthesizer's `readdirSync` may miss late-finishing partials and the merged set is silently under-merged.

**Killed during the synthesizer script:** `synthesize_recommendations.mjs` writes via tmp+rename (per round-G fix), so a killed run leaves the prior `recommendations.jsonl` intact. Re-run the script to retry. The script is fully deterministic (modulo `created_at`) given the same partials, so re-runs produce byte-identical output.

### Phase 5 — Apply changes

**Killed mid-applier:** `subagents/applier.md` writes a per-step ledger to `partial/applier_<RID>.state.json` (per round-H H5). The ledger has booleans for: `bead_created`, `files_reserved`, `edited`, `test_added`, `tests_pass`, `commit_sha`, `applied_changes_appended`, `applied_flipped`, `reservation_released`. On re-spawn, the applier reads the ledger and skips completed steps:
- After step 5 (commit) but before step 7 (append): the ledger has `commit_sha` set; the re-spawn picks up at step 7 using that SHA — does NOT re-edit, re-test, or re-commit.
- After step 7 (append) but before step 8 (flip): similar; re-spawn calls `flip_applied.sh` only.
- Between step 2 (reserve) and any later step: the prior reservation is force-released at start of every applier (per round-H H7), so the new reservation succeeds immediately.

**Two appliers picking the same R-NNN:** `flip_applied.sh` is flock-guarded (concurrent flips of the same `recommendation_id` serialize). Two appliers commits-on-different-files for the same R-NNN is a methodology violation that ledger-aware resume prevents (the second applier sees `commit_sha` already set and skips).

### Phase 6 — Re-score

**Killed during a re-scorer subagent:** re-scorer writes directly to `agent_surfaces.jsonl` using the flock-guarded tmp+filter+append pattern (per round-H H4). Re-spawn replaces any existing `(sid, pass<N+1>)` row before appending. Idempotent.

**Killed during diff_scorecards:** the script reads `agent_surfaces.jsonl` and writes `uplift_diff.md` to stdout. A killed run leaves the previous `uplift_diff.md` intact (since the user redirects with `> uplift_diff.md` which truncates first; if killed mid-write, the file is truncated but stale-content). Recovery: re-run the script.

### Phase 7 — Fresh-eyes

**Killed during fresh-eyes round N:** fresh-eyes is conversation-state, not artifact-state. The output is the round's conclusion (CLEAN / NOT_CLEAN) which the parent records. A killed fresh-eyes can simply be re-spawned for the same round. Round numbering cycles (R1-R2-R3-R1-R2-R3...) per round-H H8 fix.

### Phase 8 — Self-doc hardening

Same recovery as Phase 5 (each rec applied via the applier subagent with the per-step ledger).

### Phase 9 — Simulation

**Killed during the canonical-task-simulator:** simulator writes per-task transcripts to `audit/agent_simulations/<stage>_pass_<N>/task-NN-<slug>.transcript.jsonl`. A killed run mid-task leaves a partial transcript file. **Recovery**: re-spawn the simulator with the same `<TASK_LIST>`; for each task, check whether the transcript exists and is well-formed (closing `]` of the JSONL stream). Re-do incomplete tasks; skip completed ones. This is one of the few phases that requires explicit per-task progress tracking — the simulator subagent should add a `started: <ISO>, completed: <ISO|null>` marker at the top of each transcript file as it begins each task.

### Phase 10 — Handoff

**Killed during handoff-writer:** `audit/HANDOFF.md` is written via `>` (overwrite). Re-spawn produces a clean rewrite. Manifest update via `scripts/manifest_update.sh` is flock-guarded (per P1).

## What to do if the workspace is in an unknown state

1. Run `scripts/validate_pass.sh <SIBLING>` — reports any obvious schema violations (missing artifacts, broken cross-references between recommendations.jsonl and applied_changes.jsonl).
2. Run `tools/validate_scorecard.sh <SIBLING>/audit/agent_surfaces.jsonl` — reports any malformed score rows.
3. Look at `audit/manifest.json` `.passes[-1]`: which fields are set? `started_at` only → still in Phase 0–4. `applied_changes` count > 0 → in or past Phase 5. `completed_at` set → pass complete.
4. Check `audit/partial/` for stale per-step ledgers (`applier_R-*.state.json`). Each represents an applier in progress; resume those before starting new appliers.
5. If unsure, archive the current `audit/` to `audit/.archive/<timestamp>/` and start the pass over.

## What this doc explicitly DOESN'T cover

- **Distributed-agent failures** (multiple panes, multiple machines): Agent Mail handles inter-agent state via the `mcp-agent-mail` server, not via files in `audit/`. See `NTM-AND-AGENT-MAIL-INTEGRATION.md`.
- **Audited-tool resumability:** `CRASH-RECOVERY-AND-RESUMABILITY.md` covers how the *target CLI* should support resume/idempotency. That's a target-tool design concern, not a pipeline concern.
- **Catastrophic disk loss:** if `audit/` is gone, the audit is gone. Git-commit the workspace at the end of each phase to preserve a recoverable history.
