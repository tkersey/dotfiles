# FAILURE-MODE-CATALOG — Comprehensive failure modes for ergonomic audits

Modeled on `saas-billing-patterns-for-stripe-and-paypal/references/patterns/145-EXTENDED-FAILURE-CATALOG.md`. This catalogue gives the comprehensive list of failure modes that have been observed in real audits — not just "the audit failed" but the specific shape of failure.

Use as a debugging reference when something goes wrong, AND as a rubric anchor when scoring (knowing the failure modes makes it easier to spot them).

---

## Themes

Failure modes group into 8 themes:

1. **Methodology drift** — rubric anchor mismatch, scorer inconsistency
2. **Workflow drift** — phase ordering wrong, artifacts inconsistent
3. **Verification gap** — claim relied on but never verified
4. **Apply failure** — Phase 5 broke something
5. **Subagent confusion** — wrong subagent invoked, prompt drift
6. **Cross-pass coherence** — pass N+1 broke pass N's contracts
7. **External skill drift** — referenced skill changed shape
8. **AGENTS.md violation** — file deletion, destructive op, etc.

---

## Theme 1: Methodology drift

### FM-001: Two scorers hit the tiebreaker/escalation bands
**Symptom.** scorer-A gives 850 and scorer-B gives 500 on the same dim for the same surface, or any pair reaches a ≥ 500-point spread.
**Root cause.** Scorers reading the rubric anchors differently OR one scorer didn't invoke the binary.
**Fix.** For 300-499 point spreads, run scorer-tiebreaker (third independent scorer) without exposing raw A/B scores; use median; record `score_confidence` < 1.0. For ≥ 500 point spreads, halt and repair the rubric anchors.
**Prevention.** Better rubric anchors with concrete examples; per-scorer evidence requirements.

### FM-002: Rubric anchor cited but no longer accurate
**Symptom.** Pattern N from CANONICAL-EXEMPLARS cited in a rec, but the cited tool no longer matches.
**Root cause.** Tool drift since rubric was written.
**Fix.** Per VERIFICATION-FIRST.md, re-verify anchors quarterly. Update or replace.
**Prevention.** Quarterly rubric refresh; verification log per pass.

### FM-003: rubric_version bumped mid-pass
**Symptom.** Some surfaces scored on rubric_version A; others on B; uplift comparison invalid.
**Root cause.** Refining rubric mid-pass.
**Fix.** Pin rubric_version at start of pass; refinements deferred to next pass.
**Prevention.** Manifest_update.sh writes rubric_version at Phase 0.

---

## Theme 2: Workflow drift

### FM-010: Phase 5 applies before Phase 4 ranks
**Symptom.** Recs applied in arbitrary order; high-priority recs deferred.
**Root cause.** Skipping synthesis step.
**Fix.** Re-run synthesizer; re-prioritize; un-apply if order matters.
**Prevention.** validate_pass.sh checks recommendations.jsonl is fully ranked before allowing Phase 5.

### FM-011: applied_changes.jsonl lacks regression_test path
**Symptom.** Pass terminates "successfully" but no regression tests added.
**Root cause.** Applier subagent skipped Pattern N.
**Fix.** Add the missing regression test; verify it pins the rec; commit.
**Prevention.** validate_pass.sh enforces; in full mode, applier subagent's exit summary names the test path.

### FM-012: HANDOFF.md missing at end of pass
**Symptom.** Future passes can't pick up where this left off.
**Root cause.** handoff-writer not invoked in Phase 10.
**Fix.** Invoke handoff-writer; write HANDOFF.md.
**Prevention.** validate_pass.sh enforces.

### FM-013: Pass-N+1 starts before Pass-N is complete
**Symptom.** scorecard_pass_N never written; pass_N+1's diff_scorecards has no baseline.
**Root cause.** User invoked re-score-only without confirming Pass-N completion.
**Fix.** Run terminal phases of Pass-N; THEN run Pass-N+1.

---

## Theme 3: Verification gap

### FM-020: Score > 700 lacks evidence
**Symptom.** validate_scorecard.sh fails on a row.
**Root cause.** Scorer didn't populate `evidence.<dim>`.
**Fix.** Score row; add evidence.
**Prevention.** Scorer prompt explicitly requires evidence for > 700.

### FM-021: Recommendation cites missing pattern
**Symptom.** Rec mentions "Pattern N" but Pattern N doesn't exist OR has different content than expected.
**Root cause.** Recommender misremembered the pattern OR pattern was renumbered.
**Fix.** Look up actual pattern; update rec; or refresh CANONICAL-EXEMPLARS.

### FM-022: Live tool behavior diverged from cited evidence
**Symptom.** "Tool X has flag Y" claim no longer true.
**Root cause.** Tool released a new version that removed the flag.
**Fix.** Per VERIFICATION-FIRST.md, re-verify; update evidence; re-score.

### FM-023: Tool requires network for verification but offline
**Symptom.** Can't verify tool's runtime behavior.
**Root cause.** Sandboxed environment.
**Fix.** Document `verification_status: best_effort` for affected scores; flag for next online verification.

---

## Theme 4: Apply failure

### FM-030: Phase 6 detected regression > 50 pts (HARD STOP)
**Symptom.** A surface dropped > 50 pts after applying a rec.
**Root cause.** Rec broke unrelated surface (cross-cutting effect).
**Fix.** Revert the offending rec via `git revert`. Add deprecation path. Re-apply over multiple stages.
**Prevention.** Phase 5 applier should consider blast radius; multi-model triangulation in Phase 4 catches more.

### FM-031: Pre-commit hook failed
**Symptom.** git commit refused; tests/linters complain.
**Root cause.** Code change introduced a typecheck error / lint error / test failure.
**Fix.** Fix the issue; commit again. NEVER `--amend`; new commit.
**Prevention.** Phase 5 applier should run tests + linters before committing.

### FM-032: Applier reverted other pending changes
**Symptom.** A coworker agent's uncommitted work was lost.
**Root cause.** Applier ran `git checkout -- .` or similar destructive op without permission.
**Fix.** Recover from reflog if possible. NEVER do this again.
**Prevention.** Per AGENTS.md "trust other agents' uncommitted changes." Applier prompt explicitly forbids destructive ops.

### FM-033: Branch conflict from parallel appliers
**Symptom.** Two appliers committed to same file simultaneously.
**Root cause.** No file reservation; orchestration tier was Pair when it should have been Squad+.
**Fix.** Manually resolve conflict (NOT `git checkout --theirs/--ours`). Update reservation policy for next pass.
**Prevention.** Mandatory Agent Mail file reservations on shared files for Squad+.

---

## Theme 5: Subagent confusion

### FM-040: Wrong subagent invoked
**Symptom.** synthesizer invoked when applier was needed; output is wrong shape.
**Root cause.** Main agent confused phase / role.
**Fix.** Discard output; invoke correct subagent.
**Prevention.** Subagents print phase + role at start ("Phase 4 synthesizer running...").

### FM-041: Subagent prompt drifted
**Symptom.** Output doesn't match documented schema.
**Root cause.** AGENT-PROMPTS.md prompt was paraphrased instead of used verbatim.
**Fix.** Re-spawn with verbatim prompt.
**Prevention.** Use AGENT-PROMPTS.md prompts as-is. They're calibrated.

### FM-042: Subagent ran on wrong target
**Symptom.** Surface IDs reference wrong tool.
**Root cause.** Subagent was given wrong $TARGET / $SIBLING.
**Fix.** Discard output; re-spawn with correct paths.
**Prevention.** Subagent prompt includes manifest path; subagent verifies before working.

### FM-043: Subagent stuck in TUI / blocked on prompt
**Symptom.** Subagent timed out without producing output.
**Root cause.** Subagent invoked a tool that launched a TUI in non-TTY (and got stuck).
**Fix.** Per Operator 🚫 — note the tool's TUI-in-non-TTY as a finding; use --robot-* mode going forward.
**Prevention.** intent-runner uses `</dev/null` and `timeout 5`.

---

## Theme 6: Cross-pass coherence

### FM-050: Pass N+1 contradicts Pass N's contract pin
**Symptom.** capabilities-golden.json was updated without bumping contract_version.
**Root cause.** Pass N+1 applier didn't realize the schema-pin was load-bearing.
**Fix.** Either revert the schema change OR bump contract_version + add deprecation path.
**Prevention.** Schema-pin tests fail in Pass N+1's CI (which catches this before merge).

### FM-051: Surface_id changed across passes
**Symptom.** Same surface has different surface_ids in pass N vs N+1.
**Root cause.** compute_surface_id.sh algorithm changed OR descriptor changed.
**Fix.** Investigate; restore prior algorithm; re-score.
**Prevention.** compute_surface_id.sh is pinned; algorithm changes are explicit AND require re-score from scratch.

### FM-052: applied:false rec from Pass N abandoned by Pass N+1
**Symptom.** Pass N's deferred recs not picked up by Pass N+1.
**Root cause.** Synthesizer in Pass N+1 didn't load Pass N's recommendations.jsonl.
**Fix.** Carry forward; re-prioritize; address.
**Prevention.** Phase 4 reads prior pass's recommendations.jsonl AND HANDOFF.md.

### FM-053: Manifest's pass_N+1_ready was false but agent proceeded
**Symptom.** Pass N+1 starts on inconsistent state.
**Root cause.** Manifest signal ignored.
**Fix.** Roll back to consistent state; resume Pass N first.

---

## Theme 7: External skill drift

### FM-060: cass capabilities --json schema changed
**Symptom.** Skill's CASS-mining recipes break.
**Root cause.** Cass version update.
**Fix.** Update CASS-MINING-RECIPES-DEEP.md; re-run audit.
**Prevention.** Quarterly verification of external skill schemas.

### FM-061: Beads (br) renamed verbs
**Symptom.** Subagents that file beads error out.
**Root cause.** br CLI surface changed.
**Fix.** Update applier subagent prompts; check `bd-to-br-migration` skill.

### FM-062: Agent Mail tool catalog changed
**Symptom.** macro_start_session signature different.
**Root cause.** am updated.
**Fix.** Update am-related subagent prompts.

---

## Theme 8: AGENTS.md violation

### FM-070: File deleted without permission
**Symptom.** A file is gone after a pass; user notices.
**Root cause.** Applier or fresh-eyes subagent removed a file thinking it was unused.
**Fix.** Restore from git. NEVER recur. Per AGENTS.md Rule 1.
**Prevention.** Subagent prompts explicitly forbid deletion; validate_pass.sh checks no deletions in `git diff --diff-filter=D --name-only main..HEAD`.

### FM-071: Destructive git command run
**Symptom.** Branch / files lost; reflog shows `git reset --hard` or similar.
**Root cause.** Subagent attempted "cleanup."
**Fix.** Recover from reflog. Document.
**Prevention.** dcg hook AND prompt-level instruction to follow the local AGENTS.md safe-remediation path. In shared worktrees, do not stash, revert, or otherwise disturb peer work unless the user explicitly approves the exact operation.

### FM-072: New _v2 / _improved file created
**Symptom.** Multiple files solving same problem.
**Root cause.** Subagent didn't revise in place.
**Fix.** Merge into the canonical file; remove the variant.
**Prevention.** Per AGENTS.md "no file proliferation."

### FM-073: --no-verify used to bypass hooks
**Symptom.** Pre-commit hook failed but commit landed anyway.
**Root cause.** Applier bypassed.
**Fix.** Revert; address the underlying issue; re-commit.
**Prevention.** Subagent prompts explicitly forbid `--no-verify`.

### FM-074: Comments added "explaining what code does"
**Symptom.** Code is now noisier.
**Root cause.** Applier wrote comments per common practice.
**Fix.** Remove comments unless WHY is non-obvious.
**Prevention.** Per AGENTS.md "no comments unless WHY is non-obvious."

---

## How to use this catalog

When debugging an audit issue:

1. Identify the theme (1-8) from the symptom
2. Find the closest FM-NNN entry
3. Apply the documented fix
4. Update prevention measures if recurring
5. Document the failure in `<SIBLING>/audit/violations.md` — create the file if it doesn't exist yet (ANTI-PATTERNS.md § "Recovery from a violation" prescribes the same file for the same purpose)

---

## Adding to the catalog

When a new failure mode is observed:

1. Pick a theme; assign next FM-NNN
2. Document: Symptom / Root cause / Fix / Prevention
3. Add to this catalog
4. If preventable mechanically, add a check to validate_pass.sh

The catalog grows from real experience.

---

## Cross-references

- `methodology/TROUBLESHOOTING.md` — phase-by-phase failure mode + recovery
- `methodology/ANTI-PATTERNS.md` — what NOT to do
- `methodology/VERIFICATION-FIRST.md` — discipline that prevents many of the FM-020-series
- `methodology/DEPRECATION-PATTERNS.md` — discipline that prevents FM-030 (regression)
