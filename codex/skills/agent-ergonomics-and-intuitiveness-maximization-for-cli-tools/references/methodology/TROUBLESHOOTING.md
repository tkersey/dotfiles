# TROUBLESHOOTING — Failure modes and recovery

Symptoms you'll see during a pass; their root causes; and the recovery path. Cross-reference with `SKILL.md § Failure Modes`.

---

## Phase 0 / Bootstrap

### Symptom: `scripts/discover-cli.sh` returns "no binary detected"

**Causes.**
- Tool isn't built yet (Rust: `cargo build`; Go: `go build`; etc.)
- Binary is in an unusual location not in `phase0_cli.json`'s search list
- Tool is a library + thin CLI wrapper; the library has no entry point

**Recovery.**
- Build the tool first; re-run discover.
- Pass `--binary <path>` to discover-cli explicitly.
- If the tool is library-only, this skill doesn't apply (no agent surface to score). Tell the user.

### Symptom: `scaffold-workspace.sh` fails because sibling already exists

**Causes.** Resumed pass; or stale debris from an aborted pass.

**Recovery.**
- If `<SIBLING>/audit/manifest.json` exists: this is a resumed pass. Don't re-scaffold; jump to Phase 1 with `pass = manifest.passes[-1].pass + 1`.
- If `<SIBLING>/audit/` exists but no manifest: ask the user. Default: move to `<SIBLING>/audit/.archive/<timestamp>/` and re-scaffold.

### Symptom: feature branch creation fails (already exists)

**Recovery.** Ask the user: continue on the existing branch (resuming applied work), or pick a new pass number?

---

## Phase 1 / Inventory

### Symptom: inventory has < 5 surfaces for a non-trivial CLI

**Causes.** Recursive `--help` walk too shallow; subcommand discovery not following the framework's tree.

**Recovery.**
- Re-run `scripts/inventory_surfaces.sh <tool-binary> --depth=999` (the tool path is required as positional 1; `--depth=N` controls recursion depth).
- Manually spot-check: `<tool> help` vs `<tool> --help` vs `<tool> -h`. Are subcommands hidden behind any of those?
- For Rust clap: ensure `Command::new(...).subcommands(...)` walk hits every nested level.
- For Go cobra: walk `Cmd.Commands()` recursively.

### Symptom: `<tool> --help` crashes

**Recovery.**
- This IS a finding. Record `agent_intuitiveness: 0` for the bare-help surface, with stderr/stack-trace as evidence.
- Continue Phase 1 by reading source directly. Don't fail Phase 1.
- File as a P0 bead.

### Symptom: tool requires network for `--help`

**Recovery.**
- This IS a finding (non-deterministic; agents may have no net). Score `determinism` and `composability` 0.
- File as a P0 bead.
- Note: Phase 1 source-walk doesn't need the binary running; you can still inventory.

### Symptom: same surface gets different `surface_id`s on re-run

**Causes.** `tools/compute_surface_id.sh` is non-deterministic; or you're feeding it different descriptors.

**Recovery.**
- Verify the script: `tools/compute_surface_id.sh verb list` should produce the same string twice in a row.
- Verify descriptors come from the same source (subcommand path + flag name + kind).

---

## Phase 2 / Scoring

### Symptom: reconciliation reports many tiebreakers or any escalations

**Causes.** Scorers using different rubric versions. Or the rubric anchors are unclear for this tool.

**Recovery.**
- Pin `rubric_version` in manifest BEFORE Phase 2 starts.
- If anchors are unclear, refine the rubric (between passes; bump rubric_version) and re-score.
- Follow `RECONCILIATION-POLICY.md`: accept_warn at 200-299, tiebreak at 300-499, and halt for rubric repair at ≥ 500. If tiebreakers are common, fix the anchors instead of spawning more scorers.

### Symptom: `tools/validate_scorecard.sh` rejects scorecards (high scores without evidence)

**Recovery.** The validator's job. Re-spawn the offending scorer with the prompt's evidence requirement underlined.

### Symptom: every dim gets 1000 (n/a-as-perfect) for a surface

**Causes.** Surface kind doesn't engage half the dimensions (e.g. an env var has no `error_pedagogy` dim that meaningfully applies).

**Recovery.** Per-surface-class guidance is in `references/rubric/SURFACE-CLASSES.md`. For env vars, score `error_pedagogy` based on the error message when the env var is malformed; for exit codes, score `error_pedagogy` based on whether the exit-code dictionary explains causes.

---

## Phase 3 / Intent stress test

### Symptom: corpus has only "obvious" typos

**Causes.** Naive-agent prompt was too constrained. Or you didn't run the savvy generator.

**Recovery.**
- Re-run with full `INTENT-CORPUS-GENERATION.md` category list.
- Ensure savvy agent ran (checks boundary cases, flag interactions, deprecated spellings).

### Symptom: every corpus entry classified as `useless_error`

**Causes.** Tool genuinely has weak intent inference. (This is a finding, not a bug in the methodology.)

**Recovery.**
- That's the audit signal. Phase 4 will produce many `intent_inference` recommendations.
- Verify with one canonical case: take a typo in the corpus, run it, confirm classification.

### Symptom: `intent-runner` blocks on a TUI

**Recovery.**
- Add to runner: detect non-TTY launch; if the binary launches an interactive program, kill it after 3s and classify as `silent_fail` with stderr noting the TUI launch.
- File as a critical finding (TUIs in non-TTY are agent-blocking).

---

## Phase 4 / Synthesis

### Symptom: top recommendations contradict each other

**Causes.** No synthesis pass; or the synthesizer is biased.

**Recovery.**
- Run `subagents/synthesizer.md` again.
- If two recs contradict on Polish-Bar grounds (long-flag vs short-flag), the rubric's anchors decide; cite them.
- If two recs contradict on user-contract grounds, propose a deprecation path that satisfies both (rec C bundles A and B with a transition phase).

### Symptom: triangulation never converges (all three models disagree)

**Causes.** The recommendation is genuinely ambiguous OR the rubric anchors are unclear.

**Recovery.**
- Drop the recommendation. File the underlying surface as an exploratory bead for next pass.
- If the rubric anchors are unclear, refine them; bump rubric_version.

### Symptom: synthesis produces no top-10 (all recs tied)

**Causes.** Priority formula's `frequency` factor wasn't computed (CASS mining was skipped).

**Recovery.**
- Re-run with CASS mining `quick` (10 canned queries) to get frequency signal.
- If CASS still unavailable, fall back to score_gap × blast_radius only and note in HANDOFF.md.

---

## Phase 5 / Apply

### Symptom: applied change broke an existing user workflow

**Recovery.**
- Revert the commit (`git revert <sha>`) — DON'T `git reset --hard`.
- File as a "needs deprecation path" follow-up bead.
- Update the recommendation: add a deprecation path; bump expected_uplift; re-prioritize.
- Phase 6 will reflect the rollback (no uplift on that surface; no regression either).

### Symptom: pre-commit hook fails (typecheck / lint / test)

**Recovery.**
- Fix the issue and create a NEW commit (don't `--amend`; the failed commit didn't happen).
- If the hook is wrong (false positive), document in `<SIBLING>/audit/applied_changes.jsonl` with `risk_notes: "hook X has false positive Y; bypass would have been --no-verify but we didn't"`.

### Symptom: regression test passes but the surface didn't actually change

**Causes.** Test pins the OLD behavior, not the new one. Or test was committed before the code change.

**Recovery.**
- Read the test. Verify it asserts the post-apply behavior.
- Run it against the PRE-apply binary (checkout the parent commit) — should fail.
- Run it against the post-apply binary — should pass.
- If both pass, the test isn't actually pinning anything. Rewrite.

### Symptom: two parallel appliers commit conflicting changes

**Causes.** No file reservations; Squad-tier orchestration discipline broken.

**Recovery.**
- Resolve the conflict manually (per AGENTS.md: never destructive ops to "fix" merge conflicts).
- Bump tier OR enforce reservations going forward.
- File as a process bead: "Phase 5 needs file reservations on src/X."

---

## Phase 6 / Re-score

### Symptom: median uplift < 25 pts (loop should exit)

**Recovery.**
- Phase 4/5/6 loop has done its job. Move to Phase 7.
- If the user wants more uplift, queue Phase 4 for next pass with the unfilled gap as input.

### Symptom: regression > 50 pts on a surface

**Recovery (HARD STOP).**
- Investigate the cited file:line in `regression_alerts.md`.
- Identify the recommendation that caused it (cross-ref `applied_changes.jsonl`).
- Revert the recommendation; re-score.
- If the rec is necessary (closes a P0 finding), update it with a deprecation path that doesn't regress the existing surface.

### Symptom: applied rec showed 0 uplift

**Causes.** Implementation didn't actually change behavior; OR the rubric anchors miss the change; OR the rec was misdesigned.

**Recovery.**
- Verify the change is live: invoke the surface and confirm new behavior.
- If new behavior is live but score is unchanged, the rubric isn't sensitive to this dim. Either: refine the rubric (next pass), or accept that this rec was lower-leverage than predicted.
- If new behavior is NOT live, the applier didn't apply correctly. Re-run.

---

## Phase 7 / Fresh-eyes

### Symptom: fresh-eyes never goes quiet (always finds something)

**Causes.** "Trivial change" definition is too loose; cosmetic edits keep counting as substantive.

**Recovery.**
- Tighten: only typo fixes, whitespace, comment polish count as trivial. Rephrasing IS a change. Refactoring IS a change.
- If still hot, the changes have real bugs; fix them. The methodology is working.

### Symptom: `ubs` reports false positives

**Recovery.**
- Add to `.ubsignore`. Document the false positive in commit message.

### Symptom: project test suite fails after Phase 5

**Recovery.**
- Fix the failing tests. They're real regressions OR they pinned the old contract.
- If they pinned the old contract, update them — but ONLY if the change was intended (verify against the recommendation's `risk` and `test_plan`).
- If unintended, revert the rec.

---

## Phase 8 / Self-doc hardening

### Symptom: tool already has `capabilities` with different semantics

**Recovery.**
- Don't break the existing semantics.
- Add `<tool> capabilities --json` flag (the new agent-targeted contract) alongside the existing one. Document both.
- File a deprecation plan for the old form (if it's worth deprecating).

### Symptom: tool framework doesn't support `--robot-*` flags cleanly

**Recovery.**
- For clap: use a `--robot-NAME` style with `arg(global = true)`.
- For cobra: use a top-level persistent flag.
- For argparse: subparsers with shared parent parser.
- For yargs/commander: middleware on every command.

If the framework genuinely can't support it, propose an alternative: `--json` everywhere with stdout-data discipline (functionally equivalent).

---

## Phase 9 / Simulation

### Symptom: fresh-context simulator gets stuck on a task

**Causes.** Real intent-inference gap that the rubric / corpus didn't catch.

**Recovery.**
- File as a P0 bead for next pass.
- DO NOT mark Phase 9 complete.
- Update `INTENT-CORPUS-GENERATION.md` to add this category for future passes.

### Symptom: simulator's transcript is truncated

**Causes.** Model output limit; OR test runner killed the simulator early.

**Recovery.**
- Re-run with a smaller task list (split tasks).
- If the agent genuinely needs > 100 round-trips for a canonical task, that's itself a finding (file as ergonomics bead).

### Symptom: simulator reads `audit/` artifacts despite being told not to

**Causes.** Spawn prompt didn't enforce isolation strongly enough.

**Recovery.**
- Re-spawn with explicit instruction: "do NOT read any file under <SIBLING>; do NOT read AGENTS.md; you are meeting this tool for the first time."
- If the simulator still reads them (model misbehavior), restart from a different agent ID and document the issue.

---

## Phase 10 / Handoff

### Symptom: validate_pass.sh fails on consistency

**Recovery.**
- Read the validator's stderr; address each violation.
- Most common: an `applied:true` rec lacks a corresponding `applied_changes.jsonl` row. Add it.
- Or: a regression test was added but the rec is `applied:false`. Either flip applied or remove the test.

### Symptom: target feature branch can't be pushed (no remote configured)

**Recovery.**
- Document in HANDOFF.md that the target has no remote; the branch is local-only.
- Push the sibling (which is its own repo) so the audit isn't lost.
- Ask the user how they want to share the feature branch (push to a new remote? `git format-patch` it?).

### Symptom: beads aren't syncing (`br sync --flush-only` fails)

**Recovery.**
- Check `br doctor`.
- See `/fixing-beads-problems` skill if available.
- Worst case: document deferred recs in HANDOFF.md only (no beads); accept that future passes won't have the bead trail.

---

## Across-pass

### Symptom: Pass N+1 surface_inventory diverges from Pass N

**Causes.** New subcommands added (legitimate). Or `surface_id` algorithm changed (illegitimate; that's a regression).

**Recovery.**
- If new surfaces appear with new `surface_id`s and old ones unchanged: legitimate; new surfaces get fresh scores.
- If old `surface_id`s are gone but new ones look similar: investigate. The `compute_surface_id.sh` algorithm may have changed; that breaks comparison. Restore the prior algorithm version.

### Symptom: rubric_version changed across passes; uplift_diff is meaningless

**Recovery.**
- This is a known limitation. Document in HANDOFF.md: "Pass N+1 used rubric_version Y; Pass N used X; uplift comparison is approximate."
- For high-stakes work, re-score Pass N's surfaces against rubric Y to get a comparable baseline (one-time cost).
