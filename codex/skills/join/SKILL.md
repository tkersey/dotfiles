---
name: join
description: "PR autopilot via `gh` only: create/manage PRs, keep branches current, enforce required CI gates, apply surgical code patches, and publish merge-ready handoff without merging. Use when asked to run or monitor PR automation, fix failing required checks, keep local/remote branch state clean, or prepare branch/PR cleanup for human merge."
---

# Join

## Intent
Run a continuous PR operator using `gh` commands only. Keep PRs created, green, and merge-ready with minimal-incision fixes. Do not approve or merge PRs unless explicitly instructed by the user.

## Command boundary (hard rule)
- Use only `gh` CLI commands (`gh pr`, `gh run`, `gh api`, `gh repo`).
- Do not run `git` or any non-`gh` command.
- If a required action cannot be completed with `gh` alone, apply `auto:hold` and leave a blocking comment.

## Quick start
1. Ensure `gh auth status` succeeds.
2. Ensure labels exist: `auto:manage`, `auto:hold`.
3. Start the monitor loop.

## Auth preflight (required)
- Run these checks before any PR routing or mutation:
  - `gh auth status`
  - `gh repo view <owner>/<repo> --json nameWithOwner --jq .nameWithOwner`
- If either check fails:
  - Fail fast for the current run.
  - Apply `auto:hold` on affected PRs (or emit hold outcome in cloud loop when no PR is selected yet).
  - Record reason as `auth_unavailable`.

## Label contract
- `auto:manage`: opt-in to automation.
- `auto:hold`: pause automation.

Contributor guidance:
- Add `auto:manage` to opt in.
- Add `auto:hold` to stop the operator.

## PR creation policy (gh-only)
- For every non-default branch discoverable via `gh api` without an open PR, create a PR.
- Use the repo PR template if present; else use `assets/pr-template.md`.
- Prefer `gh pr create --fill` and apply `auto:manage`.
- Default to ready-for-review (no drafts unless configured).

## Operating mode
Use one mode only:
- `gh`-only remote mode: no local checkout assumptions and no local workspace mutations.

## Cloud Join operator (`$puff` + `seq -> join`)
Use this when running Join as a cloud subagent loop:
1. Launch with `$puff` `join-operator`.
2. For each patch artifact, route by weighted manifest-first scoring (include PR file-path hydration via `gh pr view <num> --json files`): `target_pr_hint` (+5.0), `touched_entities` overlap (+0..4.5), `changed_paths` overlap (+0..3.0), base-branch match (+1.5), and `issue_refs` (+0.5 each, max +1.0). Compute confidence as `min(0.99, (raw_score / 12.0) * risk_multiplier)` where `risk_multiplier={low:1.00, medium:0.95, high:0.80, critical:0.65}`.
3. If routing gates fail, run `$seq` first to recover intent/context. Routing gates are: confidence below effective threshold (`threshold * risk_threshold_multiplier` where `risk_threshold_multiplier={low:0.95, medium:1.00, high:1.15, critical:1.25}`), top-two score margin `< 0.75`, no entity/path/hint signal, manifest entities exist but no entity match, or `risk_level` is `high|critical`.
4. Then run `$join` for gh-only PR operations and CI/handoff behavior.

Launch recipe:
- `"$PUFF_SCRIPT" join-operator --env <env-id-or-label> --repo <owner/repo> --patch-inbox <locator>`
- Canary recipe (one bounded cycle):
  - `"$PUFF_SCRIPT" join-operator --env <env-id-or-label> --repo <owner/repo> --patch-inbox <locator> --canary`

Cloud auth note:
- In cloud environments, provide `GH_TOKEN` (or `GITHUB_TOKEN`) with repo-scoped permissions needed for join operations.

## Patch manifest contract
Patch producers should emit a manifest that validates against:
- `assets/cloud-join-manifest.schema.json`
- `assets/cloud-join-manifest.example.minimal.json` (copy-ready minimal example)
- `assets/cloud-join-manifest.example.full.json` (copy-ready full example)

Required fields:
- `patch_id`
- `producer`
- `repo` (`owner/repo`)
- `base_branch`
- `changed_paths` (non-empty)
- `intent_summary`

Optional routing hints:
- `target_pr_hint`
- `issue_refs`
- `touched_entities` (array of objects with `entity`; optional `file` and `kind`)
- `risk_level` (`low|medium|high|critical`)
- `confidence`
- `patch_file`

## Monitor loop
Process PRs sequentially (blocking per PR on CI):
1. List open PRs: `gh pr list --state open --json number,title,headRefName,labels,isDraft`.
2. For each PR:
   - Skip if `auto:hold`.
   - Skip if not `auto:manage` and not agent-created.
   - If draft, mark ready: `gh pr ready <num>`.
   - Keep the branch current with `gh pr update-branch <num> --rebase` when available.
   - Enforce CI gate (required checks only; see below).
   - If failing, run the surgical fix loop.
   - When green, publish merge-ready handoff status.
   - Do not approve or merge.

## CI gate (required checks only)
- Gate on required checks only (`gh pr checks --required`). Optional checks do not block handoff.
- Detect “ungated” repos/PRs (no required checks):
  - If `gh pr checks <num> --required --json name` returns an empty list, treat CI as green and proceed to handoff.
- Wait for required checks (blocking):
  - `gh pr checks <num> --required --watch --fail-fast`
  - This blocks until all required checks pass or the first required check fails.
- Stalled CI (10 minutes with no observable progress):
  - Define “progress” as any change in the required-check snapshot (`name`, `bucket`, `startedAt`, `completedAt`).
  - While waiting, periodically sample: `gh pr checks <num> --required --json name,bucket,startedAt,completedAt`.
  - If the snapshot does not change for 10 minutes while not all checks are `bucket=pass`, apply `auto:hold` and leave a summary comment with links to the stuck checks.
  - Treat `bucket=pending`, `bucket=skipping`, and `bucket=cancel` as “not green” (blocked) until resolved; do not mark as handoff-ready through them.
- Drill into GitHub Actions when needed:
  - Identify check links: `gh pr checks <num> --required --json name,bucket,link,workflow`
  - Find likely runs: `gh run list --branch <headRefName> --limit 10`
  - Watch a run live: `gh run watch <run-id> --compact --exit-status`
  - Fetch failing step logs: `gh run view <run-id> --log-failed`

## Surgical fix loop (gh-only)
Smallest change that makes CI green using `gh` only:
1. Read the failure from CI logs.
2. Apply the minimal fix through GitHub APIs via `gh api` on the PR head branch.
3. Re-run checks and re-evaluate.
4. Apply a hard regression floor before each new attempt:
   - Snapshot required checks before and after each attempt (`gh pr checks <num> --required --json name,bucket`).
   - If required checks get worse (for example: more failing checks, fewer passing checks, or a new blocked required check), stop immediately, apply `auto:hold`, and publish `hold_reason=regression_floor_worsened`.
   - If two consecutive attempts show no reduction in failing required checks, stop, apply `auto:hold`, and publish `hold_reason=regression_floor_no_improvement`.
5. Limit attempts (default 3). On exhaustion, permission issues, or hard conflicts:
   - Leave a summary comment.
   - Request changes as last resort.
   - Apply `auto:hold`.

## Handoff (no merge)
- When required checks are green (or no required checks exist) and no hold:
  - Update status/comment to indicate: ready for human review/merge.
  - Keep the PR open.
- Policy:
  - Never run `gh pr merge` (any flags).
  - Never run `gh pr review --approve` unless explicitly instructed by the user.
- Confirm handoff state:
  - `gh pr view <num> --json state,mergeStateStatus,reviewDecision`

## Adaptive polling
- Poll under 60s unless CI is slow.
- Use recent CI duration to back off (cap at 120s).
- Exponential backoff on API errors.

## Status reporting
- Maintain a single PR comment/check-run named `Join Operator`.
- Update in place (avoid comment spam).
- Include machine-checkable fields in each status update:
  - `raw_score`
  - `score_breakdown` (`target_pr_hint`, `entity_overlap`, `entity_hits`, `path_overlap`, `base_branch_match`, `issue_refs`, `risk_multiplier`)
  - `threshold_decision` (`confidence_threshold`, `effective_confidence_threshold`, `risk_threshold_multiplier`, `score_margin`, `needs_seq_reasons`)
  - `conflict_kind` (`none|routing|merge|policy|permission|ci`)
  - `complexity` (`low|medium|high`)
  - `confidence` (`0.00-1.00`)
  - `resolution_hint` (actionable next step; `none` only when resolved)
  - `action_taken`
  - `status` (`applied|hold|failed|no_match`)
  - `hold_reason`

## Gh-only block comment template
```
Join Operator: gh-only automation block

This PR needs an action outside the gh-only boundary (for example, manual conflict resolution or a local-only edit path).
Apply the needed commit manually, then remove `auto:hold`.
```

## Stalled CI comment template
```
Join Operator: required checks stalled

Required checks showed no progress for 10 minutes.
Investigate the linked runs, unblock CI, then remove `auto:hold`.
```

## Recipes (gh-only)
- Default branch: `gh repo view --json defaultBranchRef --jq .defaultBranchRef.name`
- Branch discovery: `gh api repos/<owner>/<repo>/branches --paginate --jq '.[].name'`
- Create: `gh pr create --fill --head <branch> --label auto:manage`
- Open PRs: `gh pr list --state open --json number,title,headRefName,labels,isDraft`
- Mark ready: `gh pr ready <num>`
- Update branch: `gh pr update-branch <num> --rebase`
- PR head OID: `gh pr view <num> --json headRefOid --jq .headRefOid`
- Required checks (summary): `gh pr checks <num> --required`
- Required checks (watch): `gh pr checks <num> --required --watch --fail-fast`
- Required checks (links/JSON): `gh pr checks <num> --required --json name,bucket,link,workflow`
- Actions runs (by branch): `gh run list --branch <branch> --limit 10`
- Actions run logs: `gh run view <run-id> --log-failed`
- Request changes: `gh pr review <num> --request-changes --body "<reason>"`
- Handoff state: `gh pr view <num> --json state,mergeStateStatus,reviewDecision`
- Handoff note (example): `gh pr comment <num> --body "Join Operator: required checks are green; ready for human merge."`

## Assets
- `assets/pr-template.md`
- `assets/cloud-join-manifest.schema.json`
- `assets/cloud-join-manifest.example.minimal.json`
- `assets/cloud-join-manifest.example.full.json`
- `assets/cloud-join-operator-prompt.md`
- `scripts/build_cloud_join_prompt.py`
- `scripts/manifest_router.py`
