# ANTI-PATTERNS — Things this skill must never do

These are violations that would invalidate the methodology. Anything here is a hard stop; the offending agent must back out.

---

## Methodology-violating

### Score a surface > 700 without evidence

The rubric is meaningless if anchored to vibes. `tools/validate_scorecard.sh` rejects scorecards with high scores lacking evidence. Always cite file:line OR runtime invocation transcript.

### Apply a change that breaks an existing working surface

Regression > 50 points on a surface is the hard-stop trigger. If a recommendation, when applied, drops a working surface from 800 → 600, revert and add a deprecation path: keep old flag, emit warning, ship new flag.

Exception: only when the existing behavior is *itself* a bug or a security issue (e.g. a deprecated `eval`-style flag). Document the exception in `applied_changes.jsonl`'s `risk` field.

### Write a recommendation without a minimal diff sketch

A vague "improve error messages" recommendation can't be applied. Phase 5 implementer needs a concrete diff sketch. Synthesizer rejects vague recs and asks the recommender to refine.

### Bundle feature work into an ergonomics pass

Conflates uplift measurement with feature scope. New features go to beads for follow-up, never silently bundled into pass-N. The skill's mandate is *surface*, not *substance*.

### Score the same surface twice with different `surface_id`

`surface_id` is content-derived (kind + subtree + name); `tools/compute_surface_id.sh` is the reference implementation. If two records have the same descriptor but different `surface_id`s, cumulative scoring across passes breaks. Validator rejects.

### Generate the heatmap before scoring is done

Mid-Phase-2 heatmaps mislead Phase 4 prioritization. The heatmap is a Phase-2-end artifact. Don't emit it until every surface has been scored.

### Land Phase 5 changes without a regression test

Each applied recommendation must have `audit/regression_tests/R-NNN__*.test.{sh,rs,py,ts}`. Without one, the next pass can't tell "fixed" from "regressed-back." `scripts/validate_pass.sh` rejects.

### Run Phase 9 against a simulator agent that has the audit's context

Defeats "fresh eyes." Spawn the simulator via the Agent tool with `subagent_type: general-purpose` and **no shared context**. The Phase 9 prompt explicitly forbids reading `audit/` artifacts.

### Land changes on `main` of the target repo

Per AGENTS.md and basic git hygiene: always feature branch `agent-ergonomics-pass-<N>`. Merge to main only with explicit user approval — and never by this skill autonomously.

### Modify `audit/` files as part of Phase 5 (in the target repo)

The audit workspace is the *measurement*; should be untouched by code changes in the target. `audit/` lives in the sibling, never in the target. The target only gains code on the feature branch.

### Treat "no `--robot-*` mode" as a feature gap rather than a finding

The methodology *finds* these gaps. If `--robot-*` is missing, that's a P0 finding scored under self_documentation + output_parseability. File it as a recommendation, don't mark it as "out of scope."

---

## AGENTS.md-violating

### Delete a file without explicit user permission

NEVER. Even your own newly-created files. This is rule #1 of AGENTS.md.

If a regression test is wrong, fix it in place. If a recommendation is duplicated, mark one `applied:false; deferred_reason: "duplicate of R-NNN"` rather than deleting the line.

### Run `git reset --hard` / `git clean -fd` / `rm -rf`

NEVER, unless user explicitly authorizes the exact command in the same message and states they understand the irreversible consequences.

If a Phase 5 commit is bad, use `git revert` (creates a new commit) rather than `git reset --hard`. If files need to be restored, copy from `git show HEAD:<path>` to a backup, then edit.

### Run a script that processes/changes code files

Brittle regex-based transformations create more problems than they solve. Always make code changes manually:

- For many simple changes: spawn parallel subagents (Phase 5 is designed for this).
- For subtle/complex changes: do them methodically yourself.

### Create `_v2` / `_improved` / `_enhanced` files

Revise existing files in place. New files only for genuinely new functionality that makes zero sense in any existing file. The bar is incredibly high.

### Add backwards-compatibility shims

We're in early development with no users (per AGENTS.md). No "compat shims" or wrapper functions for deprecated APIs.

EXCEPTION: when a recommendation explicitly requires a deprecation path (e.g. "rename `--colour` to `--color` with warning during transition"), that's not a shim — it's a planned migration. Document it in the applied_changes.jsonl `risk` field as "deprecation_path: keep old flag with warning until pass N+M".

### Skip hooks (--no-verify) or bypass signing

Per AGENTS.md: never `--no-verify`, `--no-gpg-sign`, etc. If a pre-commit hook fails, fix the issue and re-commit (NEW commit, don't `--amend`).

### Force-push without explicit user approval

The feature branch may be pushed and re-pushed (additive) but never `--force` without authorization.

---

## Subagent-spawn violations

### Spawn a fresh-context simulator with prior audit context

Phase 9's whole point is that the simulator agent has fresh eyes. Spawning one with prior context (e.g. by passing the audit dir as input) defeats it.

Use `Agent(prompt=…, subagent_type="general-purpose")` and explicitly state in the prompt: "do NOT read any audit artifacts; do NOT read AGENTS.md; you are meeting this tool for the first time."

### Spawn appliers in parallel without file reservations

Two appliers editing the same `src/cli.rs` will race. Always reserve via Agent Mail (Squad+) or serialize (Solo/Pair).

### Spawn a scorer that already saw the other scorer's output

Phase 2 scoring requires independence between paired scorers. Don't pass scorer-A's output to scorer-B as context. They must read the rubric and the binary independently.

### Spawn a triangulator that's the same model as the synthesizer

Triangulation is *multi-model*. If both your synthesizer and your triangulator are Claude, you're getting peer-Claude (still useful, but not multi-model). Set expectations accordingly.

---

## Output-format violations

### Print to stdout AND stderr for the same data

Stdout is data-only. Stderr is diagnostics-only. The skill's own scripts must obey this rule — that's the bar we hold the audited tools to.

If a script needs to emit progress, write to stderr. If a script emits its result, write to stdout.

### Mix JSON and free-text on stdout

A `--json` flag should produce only valid JSON on stdout. If the script also wants to print a banner, that goes to stderr.

### Use exit 1 for "ran fine, no results"

Empty result is exit 0. Errors are exit ≥1. The empty-result case must produce stdout that distinguishes itself from "didn't run" (e.g. `{"items": [], "ok": true}`).

### Embed timestamps in non-JSON output

Determinism breaks if every run differs by a wall-clock field. Timestamps belong in known JSON fields (`meta.ts`), never in prose / free-text stdout.

### Hardcode `/data/projects/<user>` paths in scripts

Scripts must read paths from `$1`, `$TARGET`, `$SIBLING`, or `audit/manifest.json`. Hardcoded paths break reuse across users / hosts.

---

## Deferred-rec violations

### Defer a rec without a `deferred_reason`

In Phase 10 HANDOFF.md, every `applied:false` rec must have a `deferred_reason` populated in `recommendations.jsonl`. Vague "didn't have time" is OK if the user accepts; "applied:false" with empty reason is rejected by `scripts/validate_pass.sh`.

### Mark a rec `applied:true` when only the test was added

Test without the code change is a regression test that will fail. The rec is only applied when the implementation lands AND the test passes against the post-apply binary.

---

## Rubric drift

### Refine the rubric mid-pass

Rubric_version is captured in the manifest at Phase 0. Refining mid-pass means scoring against a moving target. Always: bump rubric_version, re-score from scratch, document the change in HANDOFF.md.

EXCEPTION: spelling/typo fixes in the rubric without semantic change. Those don't bump rubric_version.

### Pick scores by gut-feel because the rubric "doesn't quite fit"

If the rubric is wrong for a tool, refine the rubric (between passes). Within a pass, follow the rubric exactly; gut-feel scoring is unreproducible.

---

## Hard-to-spot mistakes

### Score `safety_with_recovery` low for a read-side verb

Read-side verbs don't mutate state; they're inherently safe. Score 1000 (n/a-as-perfect) and put `n/a: true` in `notes`. Don't score low because "there's no --dry-run" — there's no need for one.

### Score `regression_resistance` high before any tests are added

Before Pass 1, no regression tests exist. Score 0 across the board. After Phase 5, only the surfaces with tests get high scores. This is a real signal of pass quality.

### Score `intent_inference` based on what the source *could* do, not what it *does*

Score on observed behavior (run the binary against a typo). The source might have a typo-correction module; if it's not wired up, the score is low.

### Treat "tool launches a TUI in non-TTY context" as a feature

It's a finding. Score `agent_intuitiveness` and `composability` 0.

---

## Recovery from a violation

If you discover you've committed one of these anti-patterns:

1. **Stop**. Don't compound the violation.
2. **Document**. Add a row to `<SIBLING>/audit/violations.md` with what happened, when, why.
3. **Recover**. Use the safe alternatives:
   - File deletion → didn't happen; recover from git or backups; if neither exists, stop and ask.
   - Destructive git → use `git reflog` to find the prior state; cherry-pick or branch from the reflog SHA.
   - Bad recommendation → revert the commit, file as a follow-up bead.
4. **Update**. If the violation was a methodology error (rubric drift, parallel scoring without independence), bump rubric_version or restart the affected phase.
