# REAL-AUDIT-CHECKLIST.md — Running the skill on a real CLI for the first time

The skill is production-shape. This doc is the practical handover: what to do, in order, when running it on a target CLI for the first time. Use it instead of re-reading SKILL.md + PHASES.md + OPERATING-MODES.md.

## Lessons from the 2026-05-07 bv dogfood

Eight LLM agents across two dogfood runs against `bv` v0.16.0 produced these durable lessons. Read them before launching your first real run; each was either (a) a bug invisible to static review or (b) a methodology trap a literal-following scorer will fall into.

1. **n/a dims need evidence stubs.** scorer.md Process step 3.b previously said "score 1000 + add `n/a:true` to notes". The Discipline section now overrides: every score > 700 needs `evidence.<dim>` populated, including n/a-1000 dims. Use `{"reason": "n/a — read-only verb; no irreversible operation"}` or similar. Validators reject scores >700 without evidence regardless of why.

2. **Tiebreakers fire at spread ≥ 300, not > 100.** The canonical threshold is in `references/methodology/RECONCILIATION-POLICY.md`. Stale "spread > 100" references in older docs/code have been corrected; if you see one, it's a doc-rot bug.

3. **Cluster threshold defaults to 3, not 2.** The signature has 4 components (dims, keywords, anchor_pattern, operators). With threshold 2, dims+ops alone is enough to merge — and ops `①` + `🩹` apply to almost every ergonomic fix. Default 3 means at least one of {keywords, anchor_pattern} must also overlap. Pass `--threshold 2` only if you explicitly want loose merging.

4. **Tiebreaker partials use null-fill.** scorer-tiebreaker.md schema requires non-disputed dims to be null. The verifier and aggregator both correctly handle `{null | integer 0-1000}` per the agent_surfaces schema.

5. **Inter-rater disagreement is real.** Two LLM scorers genuinely diverged by 350-400 pts on `agent_ease_of_use` and `determinism_and_reproducibility` for legitimate methodology reasons (one rewards help-text discoverability; the other penalizes wall-clock-timestamp leaks). The tiebreaker process resolves these decisively when given just the evidence (not raw scores).

6. **Recommenders show real judgment.** Don't expect 3 recommenders against 3 surfaces to all default to the same template. In the dogfood, one recommender explicitly chose units-unification over the obvious Levenshtein answer because "the typo path applies to all flags and belongs in a global rec". This is good — the median rec is more thoughtful than any one rec.

7. **Real bugs found by real scoring**: bare `bv` in non-TTY emits "could not open a new TTY" with no fallback hint; no Levenshtein-1 typo correction on any flag; sibling flags use inconsistent units (int 0-100 vs float 0.0-1.0); regression_resistance scored 0 across all 3 surfaces (no ergonomic test suite). These are concrete fixable items.

A real-world calibration fixture from this dogfood lives at `references/calibration-fixtures/bv-dogfood-2026-05-07.jsonl` — use it to detect scorer-prompt drift in future runs.

---

## Pre-flight (before the user's "go")

1. **Pick the target.** Recommended for first-run: a CLI you already own and can fix in-place if the audit recommends changes. `bv` and `br` are good choices (~30 surfaces each, owned, Rust source available).

2. **Locate the source repo.** Need both the binary on PATH AND the source repo absolute path. If only the binary is reachable, the source-driven extractors (`extract-known-flags.sh`, `discover-cli.sh`) will skip.

3. **Run pre-flight.**
   ```bash
   bash scripts/preflight.sh /path/to/target_repo
   ```
   Expect: 9 hard requirements OK; some optional helpers may warn (Beads, Agent Mail, etc.) — those are fine, the skill has fallback paths.

4. **Run preview.**
   ```bash
   bash scripts/preview.sh /path/to/target_repo
   ```
   30-second commitment. Reports: language, binary, surface count, top verbs, archetype guess. Gut-check: does the surface count match expectation? Does the archetype look right?

5. **Run estimate.**
   ```bash
   bash scripts/estimate.sh <binary> --mode mini       # smallest viable
   bash scripts/estimate.sh <binary> --mode audit-only
   bash scripts/estimate.sh <binary> --mode full
   ```
   Decide on a mode based on the projected wall-time and cost. Defaults:
   - `mini` (Phase 1+2): 5–15 min, ~$1–5 on a small CLI
   - `audit-only` (Phase 1+2+3+4): 30–90 min, ~$10–30
   - `full` (all 10 phases): 1–4 hours, ~$30–100
   For first-run on an unfamiliar CLI, **start with `mini`**. Confirm the scorecard looks reasonable before committing to the full pass.

---

## During the audit

6. **Set cost-cap in manifest before Phase 2.**
   ```bash
   bash scripts/manifest_update.sh <sibling> '.cost_cap = {"max_subagents": 500, "max_minutes": 120, "max_usd_estimated": 50}'
   ```
   At every phase boundary, run `bash tools/cost-cap.sh <sibling>`. If it exits 1, stop spawning subagents and prompt the user.

7. **Watch for partials accumulation.** After Phase 2, `<sibling>/audit/partial/` should have `scores_pass1_<SID>_scorerA.jsonl` + `scores_pass1_<SID>_scorerB.jsonl` per surface. If counts mismatch, run `bash tools/audit-doctor.sh <sibling>` to diagnose.

8. **Validate at every transition.**
   - After Phase 1: `wc -l <sibling>/audit/surface_inventory.jsonl` (should be ≥ surface count from preview)
   - After Phase 2: `bash tools/validate_scorecard.sh <sibling>/audit/agent_surfaces.jsonl`
   - After Phase 4: `bash scripts/validate_pass.sh <sibling>` (catches missing-evidence, unapplied-but-no-deferred-reason)
   - After Phase 5: `git -C <target> log --oneline agent-ergonomics-pass-1` (one commit per applied rec)

9. **If a subagent dies:** check `<sibling>/audit/partial/applier_<RID>.state.json` (the per-step ledger from round H). The next-spawned applier with the same `<RECOMMENDATION_ID>` resumes from where the dead one left off; nothing manual needed.

---

## After the audit

10. **Render output.**
    ```bash
    bash scripts/render_scorecard.sh <sibling>/audit/agent_surfaces.jsonl > <sibling>/audit/scorecard.md
    bash scripts/render_scorecard_html.sh <sibling>/audit/agent_surfaces.jsonl > <sibling>/audit/scorecard.html
    bash scripts/render_heatmap.sh <sibling>/audit/agent_surfaces.jsonl > <sibling>/audit/heatmap.svg
    ```

11. **Compare against baseline (Pass 2+).**
    ```bash
    bash tools/diff_scorecards.sh <sibling>          # within-workspace, 1→2
    bash tools/audit-compare.sh <sibling-a> <sibling-b>   # across workspaces
    ```

12. **Inspect a specific score.**
    ```bash
    bash tools/explain-score.sh <sibling> <surface_id>
    ```

13. **Final smoke before declaring done.**
    ```bash
    bash scripts/sw-self-audit.sh <repo>/.claude/skills/agent-ergonomics-and-intuitiveness-maximization-for-cli-tools/
    bash scripts/diff_test.sh <binary>   # idempotency check on deterministic phases
    ```

---

## Things to watch for (lessons from synthetic smokes)

- **gh-style CLIs** (cobra, ALL CAPS COMMANDS sections): inventory should produce 1500+ surfaces at depth 2. If <500, regex coverage may have regressed.
- **git-style CLIs** (prose section headers): inventory should produce 700+ surfaces at depth 1.
- **ffmpeg-style CLIs** (single-dash long flags, column-0 indent): inventory should pick up flags like `-version`, `-muxers`, `-decoders`. If only `-h` shows up, the column-0 fix has regressed.
- **Tools with descriptions containing flag-like text**: `extract-known-flags.sh` was recently tightened (round F: bash extraction now requires `case`-arm shape `--name)`). False-positive flags were a known issue; if you see things like `aaa`, `bar`, `AG` in the extracted list, the extractor regressed.
- **Pre-pass partial collisions**: round H added `pass<N>_` filename prefix on partials. Phase 2 partials live at `partial/scores_pass1_*`; Phase 6 re-scorer at `partial/scores_pass2_*`. They no longer collide.

---

## What the synthetic smokes did NOT cover (what to expect from a real run)

- **LLM scorers producing inconsistent output**: a real scorer subagent might emit `evidence` as a string instead of an object, miss required dims, or write the wrong `surface_id` into the partial filename. The aggregator's round-H validation will reject these, but you'll see WARN messages.
- **Recommendations that don't apply cleanly**: the applier subagent will sometimes commit a change that breaks a pre-existing test; you'll need to either revert or hand-fix.
- **Phase 9 simulator finding tasks the audit didn't anticipate**: the canonical-task-author generates tasks from README + archetype, but real users care about things READMEs don't cover. Treat Phase 9 transcripts as canonical and re-shape Phase 4 priorities accordingly.
- **Cost overruns**: `bash scripts/estimate.sh` is calibrated against jq+gh smokes and assumes 8K tokens/subagent. Real subagent runs vary 4K–20K. If you hit `cost-cap` early, raise the cap or pivot to mini-mode.

---

## If the audit goes wrong

Run `bash tools/audit-doctor.sh <sibling>` first. It diagnoses 7 common failure modes and suggests fixes. With `--apply`, it auto-fixes the safe ones (archive completed ledgers, truncate orphan locks). Duplicate score rows are diagnosed only; rerun `scripts/aggregate_scores.sh` to replace the affected `(surface_id, pass)` row.

If audit-doctor says "workspace clean" but the user still sees wrong output: archive the workspace (`mv <sibling>/audit <sibling>/audit.archive_<timestamp>`), re-scaffold, retry. Per AGENTS.md NEVER delete the original audit/.

For unrecoverable methodology gaps: file a bead and revert to mini-mode. Real runs surface methodology bugs synthetic smokes can't.
