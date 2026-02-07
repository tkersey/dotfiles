---
name: join
description: "PR autopilot for open PRs and agent-supplied unified diff patch batches: route/split changes for parallel mergeability, enforce CI gates, apply surgical fixes, and squash-merge via `gh`."
---

# Join

## Intent
Run a PR operator that can do both:
- Open-PR autopilot: keep PRs created, green, reviewed, and squash-merged (via `gh`) with minimal-incision fixes.
- Patch-batch intake: consume agent-supplied unified diffs, place them into review-friendly PRs, then merge quickly and safely.

## Quick start
1. Ensure `gh auth status` succeeds.
2. Ensure labels exist: `auto:manage`, `auto:hold`.
3. (Optional) Add `.github/auto-merge.yml` from `assets/auto-merge.yml`.
4. (Optional) Add `.github/workflows/join-routing-harness.yml` from `assets/routing-harness.yml`.
5. Pick a mode per invocation:
   - Open-PR autopilot: run the monitor loop.
   - Patch-batch intake: pass one or more fenced unified diff blocks and run the patch-batch workflow.

## Scope
- Single repository per run.
- Patch intake is invocation-based (batch in, process, exit). External agents handle re-invocation cadence.

## Label contract
- `auto:manage`: opt-in to automation.
- `auto:hold`: pause automation.

Contributor guidance:
- Add `auto:manage` to opt in.
- Add `auto:hold` to stop the operator.

## Patch intake contract (batch mode)
- Input is provided directly to `$join` by a coding agent.
- Each patch is a fenced unified diff block containing file headers and `@@ ... @@` hunks.
- Support full diff semantics when present: text hunks, renames, deletions, mode changes, and binary patch payloads.
- A batch is complete when every supplied patch has been placed into an existing or newly created PR (or explicitly held).

## Batch input payload example
Use plain text invocation content with one or more fenced `diff` blocks:

````text
Patch-Context: api retry backoff and docs sync
Base-Hint: main

```diff
diff --git a/src/retry.ts b/src/retry.ts
index 1111111..2222222 100644
--- a/src/retry.ts
+++ b/src/retry.ts
@@ -10,7 +10,12 @@ export function nextDelay(attempt: number) {
-  return 100 * attempt;
+  const capped = Math.min(attempt, 6);
+  return 100 * (2 ** capped);
 }
```

Patch-Context: follow-up docs for retry behavior

```diff
diff --git a/README.md b/README.md
index aaaaaaa..bbbbbbb 100644
--- a/README.md
+++ b/README.md
@@ -45,6 +45,7 @@ Reliability
 - retry behavior is linear
+ retry behavior is exponential with cap
```
````

Rules:
- Parse every fenced `diff` block as an independent patch candidate.
- Treat any text outside fenced blocks as optional routing context hints.
- Infer titles automatically from diff content; do not require explicit titles.

## Canonical patch identity
Use `Patch-Id` for idempotency and deduplication across runs:
1. Normalize the unified diff:
   - Strip surrounding fences/metadata outside the diff payload.
   - Normalize line endings to `\n`.
   - Trim trailing whitespace on diff metadata lines.
2. Compute `sha256(normalized_diff)`; this is `Patch-Id`.
3. Persist identity on GitHub artifacts:
   - Commit trailer: `Patch-Id: <sha256>`
   - PR body marker line: `Patch-Id: <sha256>` (one per included patch)
4. Before processing, skip any patch whose `Patch-Id` already appears on an open PR head commit or PR body marker.

## PR creation policy
- For every non-default branch without an open PR, create a PR.
- Use the repo PR template if present; else use `assets/pr-template.md`.
- Prefer `gh pr create --fill` and apply `auto:manage`.
- Default to ready-for-review (no drafts unless configured).

## Patch routing and PR shaping policy
- Optimize for parallel mergeability first.
- Prefer independent PRs over broad combined PRs when dependency edges are absent.
- Allow stacking with no fixed depth cap when dependency edges exist.
- Match incoming patches to existing open PRs using any available signal:
  - Explicit branch/title/context hints from the invocation.
  - File overlap with the PR branch diff.
  - Semantic overlap in touched paths/symbols/messages.
- If a patch overlaps multiple PRs, choose the best target PR and split residual independent hunks into additional PRs when feasible.
- If a new patch supersedes existing open PRs, route to replacement PRs and close superseded PRs only after replacements are green.
- Keep each generated/updated PR as a single commit (force-push with lease allowed when required).

## Routing heuristic (tuned)
Score each incoming patch against each open PR, then choose the highest-scoring PR when confidence is high.

Scoring signals:
- `+90` explicit PR number hint in invocation context.
- `+40` explicit branch hint matches `headRefName`.
- `+40` explicit title/context hint semantically matches PR title/body.
- `+0..50` file overlap ratio with PR diff (`overlap_ratio * 50`).
- `+0..20` symbol/token overlap in changed lines.
- `+10` PR recently updated (last 48h).
- `-40` conflicting hunk overlap likely requiring semantic inversion.

Decision thresholds:
- Best score `>= 70` and margin `>= 15` over second-best: update that PR.
- Best score `40..69`: update PR only if dependency edge exists; otherwise create new PR for parallelism.
- Best score `< 40`: create new PR from inferred base (fallback default branch).
- Ties: prefer branch with highest file overlap, then most recent update.

Splitting and stacking:
- Split patch units when independent hunks can be merged in parallel without dependency edges.
- Stack only where dependency edges force order.
- Unlimited stack depth is allowed; minimize depth whenever equivalent.

Supersession detection:
- Mark PR `A` as superseded by PR `B` when `B` fully contains `A` semantic delta or resolves the same failing CI intent with strictly newer patch units.
- Close `A` only after `B` required checks are green.

## Synthetic calibration scenarios (pre-live)
Run these scenarios against the heuristic before live operation.

| Scenario | Signal profile | Expected routing |
| --- | --- | --- |
| 1. Direct PR continuation | Same files as open PR `#42`, strong overlap, no conflicts | Update `#42`, force-push single commit |
| 2. Independent docs follow-up | No overlap with code PR, docs-only files | New parallel docs PR |
| 3. Shared file, separate hunks | Same file as open PR but disjoint hunks and no dependency | Prefer separate PR for parallel mergeability |
| 4. Hard dependency chain | Patch B requires symbols introduced by patch A | Create/keep stacked PRs A -> B |
| 5. Multi-PR overlap | Overlaps PRs `#31` and `#37`; higher score on `#37` | Route to `#37`, split residual for new PR if independent |
| 6. Superseding fix | New patch fully replaces stale failing PR intent | Create/update replacement PR, close stale PR only after green |

## Calibration harness execution
Use the bundled harness before enabling large-scale automation:
- Run all scenarios: `python3 scripts/routing_harness.py`
- Run specific scenario(s): `python3 scripts/routing_harness.py --scenario-id scenario-4`
- Emit machine output: `python3 scripts/routing_harness.py --json`
- Fail the run on any scenario mismatch.

Use the Patch-Id helper for payload verification:
- From batch payload file: `python3 scripts/patch_id.py --input /tmp/patch-batch.txt`
- From stdin: `cat /tmp/patch-batch.txt | python3 scripts/patch_id.py`
- Raw single diff mode: `python3 scripts/patch_id.py --raw-diff --input /tmp/one.diff`

## Patch-batch workflow (agent-invoked)
Process the supplied batch of patches to completion:
1. Parse all fenced unified diff blocks from the invocation payload.
2. Compute `Patch-Id` for each patch and drop already-processed identities found in open PR metadata.
3. Infer base context from patch hints; fallback to repo default branch when ambiguous.
4. Build a dependency graph for candidate patch units:
   - Same-file/same-hunk overlaps imply an edge.
   - Required ordering constraints imply an edge.
   - No edge implies independent and parallelizable.
5. Select target PR strategy per unit:
   - Update an existing PR when it is the strongest semantic match.
   - Create a new PR branch when independence improves merge parallelism.
   - Create stacked PRs when dependencies block direct parallelization.
6. Apply patch content on the chosen branch:
   - First attempt: `git apply --index --3way --recount`.
   - Repair attempt: rebase/refresh branch, re-attempt with adjusted context or direct file edit for minimal semantic equivalent.
   - On unresolved apply failure: add `auto:hold`, leave diagnostics, continue with other patches.
7. Re-shape branch history to one commit:
   - Squash local branch to a single commit containing the complete PR delta.
   - Include `Patch-Id: <sha256>` trailer(s) in commit message.
   - Push with `--force-with-lease` when updating an existing PR.
8. Create or update PR:
   - Auto-infer title.
   - Keep body minimal; include `Patch-Id` marker lines only.
   - Apply `auto:manage`; preserve existing draft/ready behavior.
9. Run CI gate on affected PRs (required checks only).
10. For superseded PRs:
   - Wait until the replacement PR required checks pass.
   - Then close superseded PR(s).
11. Run hold-recovery pass:
   - Re-check held PRs touched this run.
   - Remove `auto:hold` automatically when the blocking condition has cleared.
12. Exit when all input patches are placed into PRs or explicitly held.

## Operating modes
Mode is per-PR and determined by the current checkout:
- Local checkout (VCS): the PR `headRefName` matches the currently checked-out branch. Name match is sufficient; no upstream requirement.
- Remote-only (`gh` only): no clean local checkout/branch is available. Keep operations `gh`-only. Post-merge cleanup may still run if a local worktree is clean (see below).

Local is preferred when available or when a local branch exists and the worktree is clean enough to switch. If local mode is selected and the PR branch is checked out, dirty changes are committed and pushed into the PR before CI. If the PR branch is not checked out and the worktree is dirty, apply `auto:hold` (cannot switch safely); do not fall back to remote-only for that PR.

Mode detection (git):
- Current checkout: `git branch --show-current` (empty means detached).
- Dirty state: `git status --porcelain` (non-empty means dirty).
- Local branch exists: `git show-ref --verify --quiet refs/heads/<headRefName>`.
- Local if `git branch --show-current` equals `headRefName`.
- If not on the PR branch but a local branch exists and the worktree is clean, checkout `headRefName` and treat as local.
- If a local branch exists but the worktree is dirty, apply `auto:hold` (cannot switch safely).
- If detached in git, treat as remote-only for operations; still eligible for safe local cleanup when the worktree is clean.

## Monitor loop (open-PR autopilot mode)
Process PRs sequentially (blocking per PR on CI):
1. List open PRs: `gh pr list --state open --json number,title,headRefName,labels,isDraft`.
2. For each PR:
   - Skip if `auto:hold`.
   - Skip if not `auto:manage` and not agent-created.
   - If draft, mark ready: `gh pr ready <num>`.
   - Select mode for this PR (local if current checkout matches `headRefName` or a clean local branch exists; otherwise remote-only).
   - If local and not on `headRefName`, checkout the branch (requires a clean worktree). If dirty, apply `auto:hold`, leave a comment (template below), and skip.
   - If local, run the local sync gate (below) before CI.
   - Ensure branch is up to date.
   - Enforce CI gate (required checks only; see below).
   - If failing, run the surgical fix loop.
   - When green, auto-approve and squash-merge.
   - After a successful merge, run post-merge cleanup (mode-dependent).

## Local sync gate (required before CI)
If operating locally, ensure all local changes are in the PR:
1. Commit and push dirty changes on the PR branch:
   - `git add -A`
   - `git commit -m "chore: sync local changes"`
   - `git push`
   - If there is nothing to commit, continue.
2. Ensure OID parity with the PR head:
   - `pr_head=$(gh pr view <num> --json headRefOid --jq .headRefOid)`
   - `local_head=$(git rev-parse HEAD)`
   - If equal, continue.
   - If `git merge-base --is-ancestor "$local_head" "$pr_head"` (local behind): `git fetch origin` then `git rebase origin/<headRefName>`.
   - If `git merge-base --is-ancestor "$pr_head" "$local_head"` (local ahead): `git push`.
   - Else (diverged): apply `auto:hold` and comment (template below).

## CI gate (required checks only)
- Gate on required checks only (`gh pr checks --required`). Optional checks do not block merges.
- Do not run local pre-checks in `$join`; local validation happens outside this skill.
- Detect “ungated” repos/PRs (no required checks):
  - If `gh pr checks <num> --required --json name` returns an empty list, treat CI as green and proceed to merge.
- Wait for required checks (blocking):
  - `gh pr checks <num> --required --watch --fail-fast`
  - This blocks until all required checks pass or the first required check fails.
- Stalled CI (10 minutes with no observable progress):
  - Define “progress” as any change in the required-check snapshot (`name`, `bucket`, `startedAt`, `completedAt`).
  - While waiting, periodically sample: `gh pr checks <num> --required --json name,bucket,startedAt,completedAt`.
  - If the snapshot does not change for 10 minutes while not all checks are `bucket=pass`, apply `auto:hold` and leave a summary comment with links to the stuck checks.
  - Treat `bucket=pending`, `bucket=skipping`, and `bucket=cancel` as “not green” (blocked) until resolved; do not merge through them.
- Drill into GitHub Actions when needed:
  - Identify check links: `gh pr checks <num> --required --json name,bucket,link,workflow`
  - Find likely runs: `gh run list --branch <headRefName> --limit 10`
  - Watch a run live: `gh run watch <run-id> --compact --exit-status`
  - Fetch failing step logs: `gh run view <run-id> --log-failed`

## Surgical fix loop
Smallest change that makes CI green:
1. Read the failure from CI logs.
2. Apply the minimal fix on the PR branch.
3. Commit with a terse message (e.g., `fix(ci): <cause>`).
4. Push and re-check.
5. Limit attempts (default 3). On exhaustion or hard conflicts:
   - Leave a summary comment.
   - Request changes as last resort.
   - Apply `auto:hold`.

## Branch updates (local VCS)
- Use the repository’s active VCS; avoid tooling switches mid-fix.
- Rebase onto the default branch; force-push only when required.
- If you need a concrete example, use git equivalents (e.g., `git fetch`, `git rebase`, `git push --force-with-lease`).

## Merge
- When required checks are green (or no required checks exist) and no hold:
  - Approve: `gh pr review <num> --approve`
  - Squash-merge: `gh pr merge <num> --squash`
- Policy:
  - Do not use `gh pr merge --admin` (not approved).
  - Do not use `--delete-branch` (leave remote branches intact).
- Confirm merge completion (merge queue friendly):
  - `gh pr view <num> --json state,mergedAt,mergeStateStatus`

## Post-merge cleanup (mode-dependent)
- Remote-only (`gh` only):
  - Always confirm merge: `gh pr view <num> --json state,mergedAt`.
  - If no local git worktree is present, stop after confirmation.
  - If a local worktree is present and clean, perform the local cleanup steps below (safe cleanup even when the PR was operated remotely).
- Local checkout (VCS):
  - Goal: leave the workspace on the default branch, synced to origin, with no PR branch checked out and no lingering local refs. Avoid destructive cleaning unless the default branch diverged; if it did, create a safety branch before resetting.
  - Example (git):
    - Ensure clean working tree: `git status --porcelain` (if dirty, stop; apply `auto:hold`).
    - Switch to default branch: `git checkout <default-branch>`
    - Fetch/prune: `git fetch --prune origin`
    - Sync default branch to origin (prevents ahead/behind after merge):
      - `local_default=$(git rev-parse <default-branch>)`
      - `remote_default=$(git rev-parse origin/<default-branch>)`
      - If equal, continue.
      - If `git merge-base --is-ancestor "$local_default" "$remote_default"` (local behind): `git merge --ff-only origin/<default-branch>`.
      - If `git merge-base --is-ancestor "$remote_default" "$local_default"` (local ahead): create a safety branch, then reset:
        - `git branch "backup/<default-branch>-$(date +%Y%m%d-%H%M%S)"`
        - `git reset --hard origin/<default-branch>`
      - Else (diverged): create a safety branch, then reset:
        - `git branch "backup/<default-branch>-$(date +%Y%m%d-%H%M%S)"`
        - `git reset --hard origin/<default-branch>`
    - If the local PR branch does not exist, skip deletion.
    - Delete the local PR branch only if it matches the PR head (or remote head):
      - `pr_head=$(gh pr view <num> --json headRefOid --jq .headRefOid)`
      - `local_head=$(git rev-parse <headRefName>)`
      - `remote_head=$(git rev-parse origin/<headRefName> 2>/dev/null || true)`
      - Delete only when `local_head == pr_head` or `local_head == remote_head`; otherwise apply `auto:hold` and comment (template below).

## Adaptive polling
- Poll under 60s unless CI is slow.
- Use recent CI duration to back off (cap at 120s).
- Exponential backoff on API errors.

## Idempotency and state
- Use GitHub artifacts as the state store; do not require local operator state files.
- `Patch-Id` in commit trailers and PR marker lines is the canonical dedup source.
- On each run, re-derive routing/supersession decisions from current open PR graph plus supplied patches.
- Idempotent requirement: re-running the same batch must not create duplicate PR deltas.

## Status reporting
- Maintain a single PR comment/check-run named `AutoMerge Operator`.
- Update in place (avoid comment spam).

## Dirty local state comment template
```
AutoMerge Operator: local changes block checkout

PR branch is not checked out; worktree is dirty so checkout is unsafe.
Clean the workspace or move changes to the PR branch, then remove `auto:hold`.

Signal: `git status --porcelain` is empty.
```

## Local divergence comment template
```
AutoMerge Operator: local branch diverged

Local branch and PR head differ.
Push local commits into the PR or reset local to the PR head, then remove `auto:hold`.

Signal: `git rev-parse HEAD` equals PR `headRefOid`.
```

## Recipes
- Default branch: `gh repo view --json defaultBranchRef --jq .defaultBranchRef.name`
- Create: `gh pr create --fill --head <branch> --label auto:manage`
- PR head OID: `gh pr view <num> --json headRefOid --jq .headRefOid`
- Local branch exists: `git show-ref --verify --quiet refs/heads/<headRefName>`
- Patch-Id (sha256): `printf '%s' "$normalized_diff" | shasum -a 256 | awk '{print $1}'`
- Patch-Id helper script: `python3 scripts/patch_id.py --input <batch.txt>`
- Search Patch-Id on open PRs: `gh pr list --state open --json number,body --jq '.[] | select(.body|test("Patch-Id: <sha256>")) | .number'`
- Routing harness: `python3 scripts/routing_harness.py --scenarios assets/routing-scenarios.json`
- Apply patch (first pass): `git apply --index --3way --recount <patch.diff>`
- Push single-commit update: `git push --force-with-lease`
- Required checks (summary): `gh pr checks <num> --required`
- Required checks (watch): `gh pr checks <num> --required --watch --fail-fast`
- Required checks (links/JSON): `gh pr checks <num> --required --json name,bucket,link,workflow`
- Actions runs (by branch): `gh run list --branch <branch> --limit 10`
- Actions run logs: `gh run view <run-id> --log-failed`
- Merge: `gh pr merge <num> --squash`

## Assets
- `assets/auto-merge.yml`
- `assets/pr-template.md`
- `assets/routing-scenarios.json`
- `assets/routing-harness.yml`
