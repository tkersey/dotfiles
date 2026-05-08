---
name: auto
description: Orchestrate evidence-backed autonomous improvements to the local Codex skills ecosystem. Use when asked to auto-update skills, optimize skills from session evidence, bootstrap per-skill AUTO.md policies, scan skills for improvement candidates, create autonomous skill improvement PRs, or inspect auto-update status.
---

# Auto

## Overview

Use `auto` to run closed-loop, evidence-backed skill ecosystem maintenance without replacing the skills that already own the core work:

- `$seq` mines sessions, memories, reports, routing gaps, and usage patterns.
- `$refine` performs the actual skill edit.
- `$ship` creates or updates PRs with validation proof.
- `$fin` handles merge checks, review/CI guardrails, merge, and cleanup.

The helper scripts are deterministic guardrails and status scanners. The agent owns judgment-heavy steps: evidence interpretation, candidate selection, semantic self-checks, `$refine`, `$ship`, and `$fin`.

## Guardrails

- Never create cron automation entries, GitHub issues, `.autoupdate`, durable local state, or durable local report directories.
- Never autonomously modify protected skills: `seq`, `refine`, `cron`, `auto`, `ship`, `fin`, or `.system/*`.
- Use sanitized summaries only. Do not include raw transcript text, raw memory text, secrets, credentials, private personal details, sensitive local paths, or private user-identifying path fragments in PR bodies, commit messages, or generated files.
- Keep post-bootstrap optimization to one ordinary skill, one evidence-backed change set, one PR, and one autonomous optimization PR maximum per scheduled scan.

## Commands

Run scripts from the repo root unless otherwise noted.

```bash
codex/skills/auto/scripts/auto-scan
codex/skills/auto/scripts/auto-bootstrap-policies
codex/skills/auto/scripts/auto-optimize-one prepare --skill <skill> --evidence-class <class> --problem-slug <slug> --evidence-summary "<sanitized summary>"
codex/skills/auto/scripts/auto-optimize-one finalize --skill <skill> --evidence-class <class> --problem-slug <slug> --evidence-summary "<sanitized summary>"
codex/skills/auto/scripts/auto-status
codex/skills/auto/scripts/auto-validate-corpus codex/skills
```

## Workflow: `auto scan`

Use `scripts/auto-scan` as a read-only candidate inventory.

1. Run `auto-scan`.
2. Use the printed `$seq` command templates over the recent 90-day window, including memory evidence when useful.
3. Classify evidence using named classes, not numeric scores.
4. Treat one strong evidence class as sufficient for autonomous optimization eligibility:
   - `repeated_session_evidence`
   - `explicit_user_feedback`
   - `clear_validation_failure`
   - `clear_routing_failure`
5. Show weaker evidence classes but do not optimize autonomously on weak-only evidence:
   - `thin_usage_signal`
   - `stale_metadata_signal`
   - `trigger_overlap_signal`
   - `workflow_ambiguity_signal`
   - `missing_validation_guidance`

The scan output includes candidate skill, protected/ineligible status, evidence class, sanitized evidence summary, suggested next action, `AUTO.md` presence, and optimize-one eligibility.

## Workflow: `auto bootstrap-policies`

Use `scripts/auto-bootstrap-policies` for the one-time policy rollout.

1. Snapshot starting git state with `git status --porcelain`.
2. Create or reuse branch `auto/bootstrap-policies`.
3. Inspect ordinary skill directories under `codex/skills`, excluding protected skills.
4. For each ordinary skill, inspect `SKILL.md`, `agents/openai.yaml`, `scripts/`, `references/`, and `assets/` when present.
5. Use `$seq` dry-run evidence from the recent 90-day window and memories where useful.
6. Generate a conservative `AUTO.md` for every ordinary skill, including low-evidence skills.
7. Add an explicit `AUTO.md` reference to each participating skill's `SKILL.md`.
8. Run full corpus validation:
   - `codex/skills/auto/scripts/auto-validate-corpus codex/skills`
9. Use `$ship` to open one bulk PR. The bootstrap PR must not self-merge and requires human merge.

`AUTO.md` is advisory guidance, not a hard constraint. Read and consider it, but override it when evidence and model judgment justify doing so.

## Workflow: `auto optimize-one`

Use `scripts/auto-optimize-one` for at most one autonomous optimization.

1. Run `auto-scan` and select at most one ordinary skill.
2. Require at least one strong evidence class.
3. Run `auto-optimize-one prepare` with the selected skill, strong evidence class, short problem slug, and sanitized evidence summary.
4. Read the target skill's `SKILL.md`.
5. Read the target skill's `AUTO.md` if present.
6. Use `$refine` to make the smallest useful skill edit.
7. Keep changes under the target skill directory.
8. Run `auto-optimize-one finalize`.
9. If validation fails, attempt one repair pass. If it still fails, revert only changes owned by this run and stop.
10. If validation passes, use `$ship` to create or update a PR.
11. Use `$fin` to finish the PR only when its guardrails pass.

Do not merge if there are unresolved review threads, unresolved requested changes, failing or pending required checks, missing required approvals, merge conflicts, GitHub branch protection blocks, or repository policy blocks. If `$fin` is blocked, leave the PR open and stop.

If GitHub PR creation is unavailable, keep a local branch and passing commit only, do not locally merge, and print the branch name and blocker.

## Workflow: `auto status`

Use `scripts/auto-status` to inspect current auto-update state.

It prints current git branch, dirty worktree state, local and remote `auto/*` branches, open and recently closed `auto/*` PRs, recent `auto` commits, tool availability, quick validator presence, dependent skill directory presence, protected-skill status, and latest validation output when available in the current shell context.

## `AUTO.md` Policy Shape

Each ordinary skill should eventually have:

```text
codex/skills/<skill>/AUTO.md
```

Use this loose prose structure:

```markdown
# AUTO

## Update Intent

## Allowed Changes

## Discouraged Changes

## Evidence Cues

## Validation Expectations

## Examples of Safe Edits
```

Keep policy text conservative, advisory, and specific to the target skill.
