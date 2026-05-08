# PHASES — Per-Phase Playbook with Exit Criteria

This is the canonical playbook. Each phase has: **inputs**, **work**, **output artifacts**, **exit criteria**, and **what blocks promotion to the next phase**.

The phase loop is idempotent. Re-entering Phase 2 against an unchanged target SHA produces a byte-identical `agent_surfaces.jsonl` (same `surface_id`s, same evidence). Re-entering after changes computes uplift relative to the prior pass.

> **Path convention.** Every `audit/...` path below is shorthand for `<SIBLING>/audit/...` — the audit workspace root is the sibling directory the main agent passes to each subagent. Bare `audit/...` reads as workspace-relative throughout this file (and inside the JSONL records the phases produce, where relative paths keep records portable across machines). When you spawn a subagent that touches one of these files, hand it the absolute `<SIBLING>` value so it can resolve every reference unambiguously. See `IO-CONTRACTS.md § Path convention` for the full rule.

---

## Phase 0 — Input + Bootstrap

**Inputs.** Target CLI path, mode choice, triangulation appetite, CASS appetite, scope guardrails, branch name (full mode only).

**Work.**
1. Run `scripts/preflight.sh <target>` → verifies required local tools, target readability, build metadata, and a basic help path where available.
2. Run `scripts/scaffold-workspace.sh <sibling> <target>` → creates `audit/` tree (regression_tests, agent_simulations, partial, triangulation, .archive), `tools/`, `.gitignore`, README.md; `git init` the sibling; **and writes a populated `audit/manifest.json`** seeded with `tool_name`, `tool_repo`, `audit_workspace`, `current_pass: 1`, and a pass-1 entry containing `started_at`, `target_sha` (from `git rev-parse HEAD` in the target), and the artifacts/summary skeleton. (Round 17 made this idempotent — re-running on an already-scaffolded sibling exits 0 without overwriting.)
3. Run `scripts/discover-cli.sh <target>` → redirect to `<SIBLING>/audit/phase0_cli.json` (language, build system, binaries, completion-script paths, embedded man pages, env-var prefix conventions)
4. Run `scripts/check-skills.sh <SIBLING>/audit` → writes `phase0_skill_inventory.json`; run this after discovery so it can correlate helper-skill inventory with `phase0_cli.json`.
5. Use `scripts/manifest_update.sh <sibling> '.passes[-1].mode = "<MODE>" | .passes[-1].feature_branch = "<BRANCH>"'` to record the mode + branch name in the seeded manifest. Don't recreate the manifest from the template — the scaffold already produced a real, schema-valid one.
6. Write `<SIBLING>/audit/phase0_scope_decision.md` (mode, "must not touch" list, branch name, deprecation policies, scope guardrails). See `IO-CONTRACTS.md § audit/phase0_scope_decision.md`.
7. **In `full` mode**: create + checkout `agent-ergonomics-pass-<N>` branch in the target repo:
   ```bash
   ( cd "<TARGET>" && git switch -c "agent-ergonomics-pass-<N>" )
   ```

**Output artifacts.**
- `audit/manifest.json`
- `audit/phase0_skill_inventory.json`
- `audit/phase0_cli.json`
- `audit/phase0_scope_decision.md`

**Exit criteria.**
- [ ] Manifest exists and is valid JSON.
- [ ] CLI binary path(s) verified (binary exists and `--help` does not crash).
- [ ] Scope decision confirmed by the user (or auto-approved on resumed runs).
- [ ] Feature branch exists in target repo (full mode only).

---

## Phase 1 — Surface Inventory & Archaeology

**Inputs.** `phase0_cli.json` (binary paths), the source code at the recorded SHA.

**Work.** Crawl the CLI exhaustively. Two parallel tracks:

1. **Source-defined surfaces** (file:line cited):
   - Use `/codebase-archaeology` and `/codebase-report` for source structure
   - For Rust: `cargo run -- --help`; recursively walk `clap` definitions; extract every command, subcommand, arg, flag, env var. Look for `#[arg(env = ...)]` and `Command::new(...).arg(...)`.
   - For Go: `cobra` cmd tree; `pflag` definitions; env-var lookups via `os.Getenv` / `viper`
   - For Python: `argparse` / `click` / `typer` decorators; `os.environ.get`
   - For TypeScript: `commander` / `yargs` / `oclif`; `process.env.X`
   - For Bash: parse `case "$1" in ...` and `getopts` invocations
2. **Runtime-discovered surfaces** (`--help <path>` cited):
   - `<binary> --help`, `<binary> help`, `<binary> -h` outputs
   - Recursively for every subcommand: `<binary> <sub> --help`, `<binary> <sub> <subsub> --help`, …
   - Completion scripts: `<binary> completions bash|zsh|fish` if available
   - Embedded man pages: search for `.man` / `roff` files in repo
   - Capture `<binary> --version` output, `<binary> capabilities` if it exists, `<binary> robot-docs` if it exists

**Subagents** (parallel, see `subagents/surface-inventorist.md`):
- One per top-level subcommand
- One for env vars across the whole binary
- One for exit codes (search source for `exit(N)`, `process.exit(N)`, `os.Exit(N)`, `std::process::exit(N)`, returns from `main` / `run`)
- One for error-message corpus (every panic message, every `Err(...)` literal, every printed error)
- One for config-file schemas (TOML / YAML / JSON config formats the tool reads)
- One for signal handlers (SIGINT, SIGTERM, SIGUSR1 handling)

Each emits one JSONL line per surface to a partial file; main agent concatenates.

**Output artifacts.**
- `audit/surface_inventory.jsonl` — see schema in `IO-CONTRACTS.md § surface_inventory`

**Exit criteria.**
- [ ] Every subcommand reachable from `<binary> --help` has at least one record.
- [ ] Every env var named in source has a record.
- [ ] Every exit code site has a record (with `exit_code: <N>` and `condition: "..."`).
- [ ] Spot check: pick 3 random surface records, verify `surface_id` deterministically reproduces via `tools/compute_surface_id.sh`.
- [ ] `wc -l audit/surface_inventory.jsonl` ≥ ~ (subcommand count × 5) for any non-trivial CLI.

**Blockers.** If `<binary> --help` crashes, that's a finding (intuitiveness=0); record it, file as P0 bead, **continue Phase 1** by reading source directly. Don't fail Phase 1.

---

## Phase 2 — Rubric-Driven Scoring

**Inputs.** `surface_inventory.jsonl`, `references/rubric/SCORING-RUBRIC.md`, the binary itself for live invocation.

**Work.** Each surface gets scored across all 11 dimensions by a **scorer subagent**. To control bias and inter-rater drift:

- **Two independent scorers per surface** (different agent IDs, no shared context).
- If spread is 200-299 points on any dimension, accept with warning. If spread is 300-499, a **third tiebreaker scorer** runs and the final score is the median. If spread is ≥ 500, halt and escalate the rubric anchors instead of tiebreaking. The spread is recorded as `score_confidence`.
- Each score > 700 requires **evidence** (file:line, or `--help` excerpt, or invocation transcript). The scorer fills `evidence` field; `tools/validate_scorecard.sh` rejects high scores without evidence.

The scorer reads the rubric anchors at 0/250/500/750/1000 (see `SCORING-RUBRIC.md`), invokes the binary against the surface, and emits one JSONL line per scorer to `<SIBLING>/audit/partial/scores_pass<N>_<SURFACE_ID>_scorer<X>.jsonl` (the **per-scorer partial** schema, which omits `pass`, `score_confidence`, `scored_at` — those are added during aggregation). The `pass<N>` discriminator is mandatory so Phase 2 and Phase 6 partials cannot be mixed.

**Aggregation (main agent).** After both scorers (and optionally the tiebreaker) finish for a given `surface_id`, the main agent runs `scripts/aggregate_scores.sh <SIBLING> [<surface_id>]` which automates the 5-step process below. Run with no `<surface_id>` argument to aggregate every surface that has ≥ 2 partials in `<SIBLING>/audit/partial/`. The script:

1. Reads all partial files for the target surface(s).
2. Computes per-dim **median** across the 2 (or 3) scorers' values → goes in the final `scores` block.
3. Computes per-dim **spread** (max − min); records max-spread as `score_confidence.spread_max`; sets `tiebroken: true` if any partial has `scorer_id == "tiebreaker"`.
4. Adds `pass` (from `manifest.current_pass`), `scored_at` (current ISO-8601 timestamp), and copies through `rubric_version`, `evidence`, `notes`. Recomputes `weighted_score` as the integer mean of present median scores.
5. Replaces any prior row for the same `(surface_id, pass)`, then writes one final row to `<SIBLING>/audit/agent_surfaces.jsonl` per the IO-CONTRACTS schema.

The partial files remain on disk for audit/debug; they are not promoted to the durable artifact. Re-runs against the same target SHA produce a byte-identical aggregated row (modulo `scored_at`). Run `tools/validate_scorecard.sh <SIBLING>/audit/agent_surfaces.jsonl` afterward to confirm every row passes the schema.

**Output artifacts.**
- `audit/agent_surfaces.jsonl` — one line per surface, with median + spread per dimension, evidence, and computed weighted score
- `audit/scorecard.md` — rendered via `scripts/render_scorecard.sh`
- `audit/heatmap.svg` — rendered via `scripts/render_heatmap.sh`

**Exit criteria.**
- [ ] Every surface in `surface_inventory.jsonl` has a corresponding line in `agent_surfaces.jsonl` (matching `surface_id`).
- [ ] No score > 700 lacks evidence (`tools/validate_scorecard.sh` exits 0).
- [ ] Median spread across all dims is < 80 points (rubric is well-calibrated).
- [ ] `rubric_version` in manifest matches the file's git SHA (so re-scoring is reproducible).

**Blockers.** If the rubric is being challenged ("this dim doesn't fit our tool"), pause Phase 2 and update `references/rubric/SCORING-RUBRIC.md` with the project-specific anchor; bump `rubric_version`. Re-score from scratch.

---

## Phase 3 — Intent-Inference Stress Test

**Inputs.** Surface inventory, the binary, source access for the savvy agent.

**Work.** Generate a corpus of plausibly-wrong invocations and score each on the four-class outcome:

- `silent_fail` (worst): tool exits 0, prints nothing, did nothing
- `useless_error` (bad): tool errored, but the message is unhelpful (e.g. "syntax error", no flag suggested)
- `useful_hint` (acceptable): tool errored, named the exact flag/command the agent should have used
- `inferred_and_acted` (best): tool inferred intent and proceeded (with or without a warning)

Two corpus generators:
1. **Naive agent** (`subagents/intent-stresser-naive.md`): only has access to `--help`, no source. Generates "what would I try if I'd never seen this tool?" — typos (`--jsno`, `--jason`), wrong subcommand order (`<tool> <sub> --flag arg` vs `<tool> <sub> arg --flag`), spelling variants (`--colour`/`--color`), tool-family confusion (`<tool> ls` vs `<tool> list`), missing required args, common mis-orderings.
2. **Savvy agent** (`subagents/intent-stresser-savvy.md`): has source access; targets the *boundaries* of intent-inference logic — flags that almost-but-don't-quite match an existing flag, environment variables that look like another tool's, deprecated spellings the source still mentions in comments.

Each generated invocation is run by `subagents/intent-runner.md` and its outcome is captured (stdout/stderr/exit-code) and classified.

**Output artifacts.**
- `audit/intent_inference_corpus.jsonl` — one record per attempted invocation, with `corpus_id`, `generator: naive|savvy`, full invocation, stdout, stderr, exit_code, classification, `surface_id` of the surface this stresses

**Exit criteria.**
- [ ] At least 50 entries for any non-trivial CLI (and ≥ 20 for tiny ones).
- [ ] Every entry has all four fields populated (stdout/stderr/exit_code/classification).
- [ ] Each surface that scored < 700 on `intent_inference` has at least 3 corpus entries.
- [ ] Pre-pass simulation transcripts for canonical tasks captured in `agent_simulations/pre_pass_<N>/`.

**Blockers.** None. This phase is read-only against the binary.

---

## Phase 4 — Recommendation Synthesis & Prioritization

**Inputs.** `agent_surfaces.jsonl`, `intent_inference_corpus.jsonl`, the cluster of below-quartile surfaces.

**Work.**
1. **Per-surface recommendations** (`subagents/recommender.md`, parallel): for each surface in the bottom quartile (weighted score < 25th percentile), produce a `recommended_fix` block with:
   - Minimal diff sketch (Rust/Go/Py/TS/Bash code-equivalent of the change)
   - Expected per-dimension score uplift after fix
   - Risk notes (what existing usage breaks; deprecation path needed?)
   - Test additions required (golden / snapshot / round-trip)
2. **Barrier — wait for all parallel recommenders to finish.** Before spawning the synthesizer, the main agent MUST verify:
   - Every below-quartile surface has a corresponding `<SIBLING>/audit/partial/recommendations_<SURFACE_ID>.jsonl` file present and non-empty.
   - Every recommender subagent that was spawned has reported "completed" (not "in flight").
   Without this barrier, `synthesize_recommendations.mjs` reads the `partial/` directory while parallel recommenders may still be writing — `readdirSync` may miss late-finishing partials and the synthesized set is silently under-merged. If a recommender died without producing a partial, re-spawn it before continuing (per `subagents/recommender.md`'s write-not-append rule, the re-spawn replaces the prior crashed output).
3. **Synthesis** (`subagents/synthesizer.md`, single-agent): merge overlapping recommendations (e.g. three flags all need `--json`-mode; bundle as one rec); resolve contradictions (rec A wants `<flag>`, rec B wants `--<flag>` — pick by Polish-Bar guidance); rank by `priority = frequency × score_gap × blast_radius`.
4. **Triangulation** (`subagents/triangulator.md`, optional): if `multi-model` triangulation is requested AND `/multi-model-triangulation` skill is available, send the top 10 recommendations to Codex + Gemini and reconcile differences. See `TRIANGULATION.md`.

**Output artifacts.**
- `audit/recommendations.jsonl` — one line per recommendation (`R-NNN` ID, surface_id, priority, diff sketch, expected uplift, risk, test plan, applied:false)
- `audit/playbook.md` — narrative for top-10 recommendations: rationale, sequencing, dependencies between recs, risk-aware ordering

**Exit criteria.**
- [ ] At least one recommendation per below-quartile surface.
- [ ] Top 10 recommendations have diff sketches concrete enough for a Phase 5 implementer to apply without guessing.
- [ ] No two recommendations contradict each other (synthesis caught it).
- [ ] If triangulation was requested: triangulation result attached to each top-10 rec.

**Blockers.** If two top-priority recommendations contradict and the synthesis can't resolve them, escalate to user with a one-paragraph explanation and proposed split (e.g. "merge rec A and rec B into rec C with deprecation path"). Don't move to Phase 5 until contradictions are resolved.

---

## Phase 5 — Apply Changes (full mode)

**Inputs.** Top-N ranked recommendations, the target's feature branch.

**Work.**
1. **Bead per recommendation.** For each top-N rec, create `br create --title "[R-NNN] <short>" --type=task --priority=<N> --labels="agent-ergonomics,pass-<N>"`.
2. **File reservations.** Before editing a shared file (any file mentioned by ≥ 2 recs), use Agent Mail `file_reservation_paths` with `reason="R-NNN"` and `thread_id="agent-ergo-pass<N>-R-NNN"`.
3. **Implement** (`subagents/applier.md`): the smallest change that closes the surface's failing dimensions. Preserve all existing functionality. Never break a working surface to "improve ergonomics" without a deprecation path.
4. **Regression test author** (`subagents/regression-test-author.md`): for each applied rec, write a test in `audit/regression_tests/R-NNN__<short>.test.sh` (or `.test.rs` / `.test.py` / `.test.ts` matching the project) that pins the new behavior. Tests are runnable in CI; exit 0 = pass.
5. **Append** to `<SIBLING>/audit/applied_changes.jsonl`: before/after evidence (file:line + diff), test ID, surface_ids touched.
6. **Flip** `applied:true` in `recommendations.jsonl` for the rec.

**Discipline (re-read before each commit).**

From AGENTS.md (must NOT violate):
- **Never delete a file without explicit user permission.** Even your own newly-created files.
- **Never run a script that processes/changes code files in this repo.** Brittle regex transformations create more problems than they solve.
- **Never create _v2 / _improved / _enhanced files.** Revise existing files in place.
- **No backwards-compat shims.** Just fix the code (UNLESS the rec explicitly requires a deprecation path; that's not a shim).
- **Never `git reset --hard`, `git clean -fd`, `rm -rf`** unless user explicitly authorizes.
- **Default to writing no comments.** Only when WHY is non-obvious.
- **Don't add features beyond the rec.** The smallest change that closes the failing dims is the right change.

**Output artifacts.**
- `audit/applied_changes.jsonl`
- One commit per applied rec on the target's `agent-ergonomics-pass-<N>` branch (commit message: `R-NNN: <short> (closes <surface_id>)`)
- One file per applied rec in `audit/regression_tests/R-NNN__*.{sh,rs,py,ts}`

**Exit criteria.**
- [ ] Every top-N rec is either `applied:true` or has a documented deferral reason in `playbook.md`.
- [ ] All regression tests pass against the post-apply binary.
- [ ] `cargo test` / `go test` / `pytest` / `vitest` (project's test suite) is green.
- [ ] `tsc --noEmit` / `cargo clippy` / linters green.
- [ ] No file deletions (verify with `git diff --diff-filter=D --name-only main..HEAD` returning empty).

**Blockers.** If a rec, when applied, breaks an existing surface (regression > 50 pts in Phase 6), revert that rec and file it as a "needs deprecation path" follow-up bead. Do not bypass the regression check.

---

## Phase 6 — Re-Score & Uplift Verification

**Inputs.** Modified target on the feature branch, the pre-pass `agent_surfaces.jsonl`.

**Work.**
1. **Re-build / re-install** the binary (`cargo build --release`, `go build`, `bun install && bun run build`, etc.).
2. **Re-run Phase 2** scoring (`subagents/re-scorer.md`, parallel by surface_id) against the new binary.
3. **Diff scorecards.** Two equivalent forms:
   - **Smart wrapper** (run from any cwd; auto-detects sibling + reads `current_pass` from manifest, diffs `(current_pass - 1)` → `current_pass`):
     ```bash
     bash tools/diff_scorecards.sh "<SIBLING>" > "<SIBLING>/audit/uplift_diff.md"
     ```
   - **Explicit form** (when you need non-adjacent passes, e.g. comparing pass 1 vs pass 3):
     ```bash
     bash scripts/diff_scorecards.sh "<SIBLING>/audit/agent_surfaces.jsonl" <PRIOR_PASS> <NEW_PASS> > "<SIBLING>/audit/uplift_diff.md"
     ```
   Both forms produce the per-surface uplift table, the **Added surfaces** / **Removed surfaces** sections (Round 16 fix — surfaces present in only one pass), and per-dim regression alerts (drops > 25 pts) inline. Exit code 3 = HARD STOP (any surface dropped > 50 pts overall).
4. **Regression alerts** are emitted to the same `<SIBLING>/audit/uplift_diff.md` as a "## Regressions" subsection (and to `<SIBLING>/audit/regression_alerts.md` separately when generated by re-scorer subagents per `re-scorer.md`'s Output section). There is no `--regressions-only` flag — re-running the diff with a different output filter is the way.

**Output artifacts.**
- `audit/scorecard_pass_<N+1>.md`
- `audit/uplift_diff.md`
- `audit/regression_alerts.md`

**Exit criteria.**
- [ ] Median uplift across applied surfaces ≥ 25 points.
- [ ] No surface regressed by > 50 points overall.
- [ ] No applied recommendation showed a surface uplift of 0 (= ineffective; reopen rec).
- [ ] If median uplift < 25 points: loop back to Phase 4 with the unfilled gap as input.

**Blockers.** A regression > 50 points is a **hard stop**. Investigate root cause at the cited file:line; either revert the offending rec or escalate.

---

## Phase 7 — Fresh-Eyes Bug & Ergonomic Review

**Inputs.** All applied changes, all `audit/` artifacts.

**Work.** Run the three calibrated prompts (verbatim — they're calibrated):

1. *"Carefully read over all of the new code you just wrote and other existing code you just modified with 'fresh eyes' looking super carefully for any obvious bugs, errors, problems, issues, confusion, etc. Carefully fix anything you uncover."*
2. *"Sort of randomly explore the code files in this project, choosing code files to deeply investigate and trace their functionality and execution flows through the related code files which they import or which they are imported by. Once you understand the purpose of the code in the larger context of the workflows, do a super careful, methodical, and critical check with 'fresh eyes' to find any obvious bugs, problems, errors, silly mistakes. Comply with ALL rules in AGENTS.md and ensure that any code you write or revise conforms to the best practice guides referenced in AGENTS.md."*
3. *"Turn your attention to reviewing the code written by your fellow agents and checking for any issues, bugs, errors, problems, inefficiencies, security problems, reliability issues. Diagnose underlying root causes using first-principle analysis. Don't restrict yourself to the latest commits — cast a wider net and go super deep."*

Repeat until two consecutive rounds come up clean (only trivial edits — typos, comment polish — count as "trivial"; rephrasing IS a change).

After fresh-eyes is clean twice in a row, run `ubs <changed-files>` (if available) and the project's full test suite. Fix everything.

**Output artifacts.**
- Additional commits on the feature branch addressing fresh-eyes findings
- Fresh-eyes log: `audit/phase7_fresh_eyes_log.md` listing each round and what was found

**Exit criteria.**
- [ ] Two consecutive fresh-eyes rounds report only trivial edits.
- [ ] `ubs` exits 0 (or all reported issues are documented as false-positives in `.ubsignore`).
- [ ] Project test suite + lint + typecheck all green.
- [ ] All `audit/regression_tests/` still green.

---

## Phase 8 — Self-Documentation & Discoverability Hardening

**Inputs.** The post-Phase-7 binary.

**Work.** Verify (and if missing, add) every agent-discoverability surface:

- `<tool> --help` and `<tool> -h` (top-level + every subcommand)
- `<tool> --version` and `<tool> -V`
- `<tool> capabilities --json` (returns version, contract version, feature flags, command list, exit-code dictionary, env-var dictionary)
- `<tool> robot-docs guide` (or `<tool> --robot-help`) — paste-ready agent handbook in-tool
- `<tool> --robot-*` mode for every read-side verb (or `<verb> --json` if `--robot-*` doesn't fit the tool's idioms)
- Exit-code documentation: every non-zero exit cited in `--help` or `capabilities`
- Machine-readable schema export: a way to emit the full output schema (e.g. `<tool> schema --json`)

For each missing surface:
1. File a bead `[R-NNN-supplement] add <surface>` (P1 if it would lift > 200 pts; P2 otherwise)
2. Implement (`subagents/self-doc-hardener.md`)
3. Add a regression test in `audit/regression_tests/`
4. Re-score the affected surfaces (`agent_ease_of_use`, `output_parseability`, `self_documentation`)

**Output artifacts.**
- New `--help` / `--robot-help` / `capabilities` / `robot-docs` surfaces in the target
- Updated `audit/agent_surfaces.jsonl` with re-scored values for the affected surfaces

**Exit criteria.**
- [ ] `<tool> capabilities --json` exists and is valid JSON.
- [ ] `<tool> robot-docs guide` exists and prints something useful in < 50 lines.
- [ ] Every read-side verb has a `--json` or `--robot-*` mode.
- [ ] Exit-code dictionary is exhaustive and matches actual behavior.

---

## Phase 9 — Agent-In-The-Loop Simulated Verification

**Inputs.** The post-Phase-8 binary, a list of canonical tasks the CLI is designed to support (collected at intake; default: top 5–10 from `<tool>'s` README "Examples" section).

**Work.** Spawn a fresh subagent (Agent tool, `subagents/canonical-task-simulator.md`, **no prior context about the audit**) and give it 5–10 canonical tasks. Capture full transcripts (stdin/stdout/stderr/exit-code per call) into `audit/agent_simulations/post_pass_<N>/`.

Score each task on:
- Did the first command tried succeed?
- Round-trips to completion?
- Did any error message leave the agent stuck?

Compare against the pre-pass simulation captured in Phase 3. The diff is the **ground-truth check** on the methodology.

**Output artifacts.**
- `audit/agent_simulations/post_pass_<N>/task-NN-<slug>.transcript.jsonl`
- `audit/agent_simulations/post_pass_<N>/summary.md` — per-task pass/fail/round-trip counts + cross-pass deltas

**Exit criteria.**
- [ ] At least 5 canonical tasks attempted.
- [ ] Each task has a complete transcript (no truncation).
- [ ] Summary shows median round-trip improvement vs pre-pass (if not, a methodology gap; file a bead).

**Blockers.** If a fresh agent gets stuck on a task that "should" work after this pass, that's a real intent-inference gap. File as P0 bead for next pass; don't mark Phase 9 complete.

---

## Phase 10 — Handoff & Iteration-Readiness

**Inputs.** Everything from prior phases.

**Work.**
1. **Generate `audit/HANDOFF.md`** (`subagents/handoff-writer.md`):
   - What was tried this pass
   - What worked (with uplift evidence)
   - What didn't (with diagnosis)
   - What's queued for Pass N+1 (open recs with `applied:false` + new beads)
   - Known false-positives in the rubric (with proposed rubric refinements)
   - Suggestions for rubric / dimension list updates (the rubric is a living artifact too)
2. **Idea wizard** (`subagents/idea-generator.md`, optional): use `/idea-wizard` if available to brainstorm second-order ergonomic improvements that didn't surface from the rubric. File as beads.
3. **Land the plane (per AGENTS.md):**
   - In sibling: `git add -A && git commit -m "agent-ergonomics pass <N>: ..." && git push` (if remote configured)
   - In target: `git push origin agent-ergonomics-pass-<N>`
   - **Do NOT merge to main** without explicit user approval.
   - Run `br sync --flush-only` if beads were created in the target.
4. **Update manifest.** `pass_N+1_ready: true` if the median uplift is satisfying; otherwise `pass_N+1_ready: false` and `next_pass_focus: <area>`.

**Output artifacts.**
- `audit/HANDOFF.md`
- Updated `audit/manifest.json`
- Pushed branches + commits

**Exit criteria.**
- [ ] HANDOFF.md exists and ends with a "Pass N+1 focus" section.
- [ ] All beads filed for queued work.
- [ ] Sibling and target branches are pushed.
- [ ] Manifest is consistent with all artifacts (use `scripts/validate_pass.sh`).
