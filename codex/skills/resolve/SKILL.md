---
name: resolve
description: Resolve the current branch by repeatedly running the selected Codex review backend through a deterministic review driver, adjudicating every finding and PR comment, fixing actionable issues, requiring three consecutive clean reviews, validating, committing, pushing, and sweeping PR comments.
---

# resolve

## Purpose

Resolve the current branch to a review-clean, PR-comment-reviewed, validated, committed, and pushed state.

Use this skill when the user wants Codex to keep reviewing and fixing a branch until the selected Codex review backend produces three consecutive review runs with zero findings/comments, then validate, commit, push, and process pull request comments with the same adjudication and fixed-point flow.

This skill must not call `codex review --base main` directly as its normal review primitive. Always run Codex review through the review driver defined below so the review backend, review base, `HEAD`, and result receipts are discovered, pinned, recorded, and reset correctly when branch state changes.

## Completion criteria

Do not consider the branch resolved until all of the following are true, in this order:

1. The selected Codex review backend has produced three consecutive clean review runs against the current branch through the review driver.
2. A clean review run means the review returns no findings, no comments, no requested changes, and no unresolved review output.
3. Any review run with one or more findings/comments resets the clean-review streak to zero, even when every comment is later adjudicated as `do-not-address`.
4. The review base used for the clean-review streak has been discovered by the review driver, pinned for the streak, and recorded.
5. After the third consecutive clean review, all required builds, lints, tests, and type checks pass.
6. If validation requires any code, config, dependency, lockfile, generated-artifact, or test change, reset the clean-review streak to zero and restart the Codex review loop.
7. Only after the final clean-review streak and final validation pass may the branch be committed and pushed.
8. After each push, find the PR associated with the current branch and review all currently available PR comments, inline review comments, unresolved review threads, and requested-change summaries.
9. Every in-scope PR comment must be adjudicated with `$review-adjudication` unless it is clearly irrelevant system noise, already resolved, authored by this agent as a status/reply, or previously adjudicated with the same content and context in the current run.
10. Every actionable Codex review finding and every actionable PR comment must be fixed with `$fixed-point-driver`.
11. If PR comment resolution causes any change, repeat the Codex review loop until three consecutive clean reviews, rerun full validation, commit, push, and check the PR again.
12. The skill is complete only after the latest pushed commit has passed the final validation gate, has three consecutive clean Codex review results from the pinned backend class, and the post-push PR sweep has no unprocessed in-scope comments and no actionable PR comments remaining.

## Definitions

- `native Codex review`: The Codex CLI or repository-native Codex review command, normally `codex review`, not a separate LLM review invented by this skill.
- `review backend`: The review execution class used for streak accounting: CAS lane review by default after strict preflight, or native CLI review only as an explicit fallback when CAS cannot produce a reliable review result.
- `review driver`: The deterministic wrapper in this skill that discovers the correct base, invokes the selected Codex review backend, captures output, parses findings, and reports whether the review was clean.
- `clean review`: A completed Codex review run from the selected backend with zero findings/comments/requested changes. Tool failures, malformed output, partial output, or ambiguous output are not clean reviews.
- `finding/comment`: Any substantive review item, inline comment, requested change, issue, warning, or review note that asks for or implies a code, test, behavior, safety, reliability, performance, accessibility, maintainability, API, release, or documentation change.
- `HEAD changed`: The current commit SHA changed because of a fix, generated file update, validation fix, rebase, merge, amend, or any other branch mutation.
- `base changed`: The resolved base ref or merge-base SHA changed since the current clean-review streak began.

## Overall flow

Use this high-level loop:

```text
repeat:
  run_local_resolution_loop_until_three_clean_reviews_and_validation_pass()
  commit_and_push_if_there_are_intended_changes()
  pr_result = run_post_push_pr_comment_sweep()

  if pr_result.requires_code_or_config_changes:
    continue

  if pr_result.has_unrecoverable_blocker:
    stop_without_claiming_completion

  finish
```

A PR sweep is a point-in-time check of comments available after the push. Do not wait indefinitely for future reviewer activity. If new comments appear during the current run and are visible before completion, process them.

## State to maintain

Maintain this state during the skill run:

```text
clean_review_streak = 0
streak_review_backend = null
streak_target_fingerprint = null
streak_base_ref = null
streak_base_sha = null
streak_head_sha = null
last_review_invocations = []
adjudication_ledger = {}
pr_comment_ledger = {}
validation_commands = []
language_skill_packet = {}
```

Reset `clean_review_streak` to zero whenever:

- Codex review returns any finding/comment;
- `$fixed-point-driver` changes code, config, dependencies, lockfiles, generated artifacts, docs required by behavior, or tests;
- validation requires any fix or generated file update;
- `HEAD` changes;
- the review backend class changes;
- the review driver resolves a different base ref or merge-base SHA;
- PR comment handling changes the branch;
- a rebase, merge, amend, cherry-pick, or branch synchronization changes the comparison.

Do not reset the streak merely because another clean review was run. Increment the streak only for completed clean review runs from the pinned backend class against the pinned base and current `HEAD`.

## Language-specific skill routing

`$resolve` owns language-skill discovery and routing, not language-specific proof mechanics.

Before the first review run, and again whenever the changed file set materially changes, inspect the repository and diff for language/tooling signals:

- changed file extensions and manifests such as `build.zig`, `Cargo.toml`, `package.json`, `pyproject.toml`, `go.mod`, `mix.exs`, `lakefile.lean`, or equivalent project roots;
- validation commands already discovered from CI, task runners, package scripts, or project docs;
- explicit user-mentioned skills;
- review failures that identify a language tool, cache, compiler, package manager, formatter, linter, or test runner.

For every applicable language or tool skill available in the session, load the target skill instructions before selecting proof commands or invoking review. Keep a concise `language_skill_packet` with:

```text
language_skill_packet = {
  skill_name: string,
  trigger_evidence: string,
  loaded: boolean,
  review_guidance_summary: string,
  validation_guidance_summary: string
}
```

Pass the relevant guidance into review context and local validation planning. For Zig projects, `$resolve` should route to `$zig`; `$zig` owns details such as writable Zig cache paths, Zig 0.16 proof lanes, lint/test command shape, and cache-environment failure classification. `$resolve` must not hardcode Zig-specific environment variables or cache paths except as a direct quote from loaded `$zig` guidance.

If a clearly applicable language skill cannot be loaded, record that as a review-driver limitation and either proceed with repository-native commands already proven locally or stop as blocked when the missing guidance is required to distinguish tool transport failure from code failure.

## Backend selection

`$resolve` is CAS-first. After base discovery and language-skill routing, attempt the persistent CAS lane preflight before any native `codex review` invocation. Use native Codex review only when one of these fallback conditions is true:

- CAS preflight fails or proves the installed `cas` / `cas review_session` surface is too old or incompatible.
- CAS lane startup, status, review, or receipt normalization fails in a way that prevents a reliable review verdict.
- CAS reports a blocking transport/runtime failure and explicit native fallback is the only available review path.
- The user explicitly requests native review for the current run.

Do not choose native review merely because it is simpler, faster to type, historically common, or because the run only needs a one-shot verdict. `$resolve` is a multi-cycle remediation workflow, and its normal review primitive is `cas review_session lane review ... --json --fallback none`.

When native fallback is used, record the fallback condition in `last_review_invocations`, reset any CAS-backed clean-review streak, classify the backend as `native-cli` or `cas-native-fallback` as applicable, and keep the same base/HEAD pinning rules.

## Native fallback review driver

All native Codex review invocations must go through this fallback driver. Do not call `codex review --base main` directly except as a documented last-resort fallback when no remote default branch, PR base, or usable remote ref can be discovered.

The driver must:

1. Inspect the current branch and working tree.
2. Fetch remote refs before selecting the base.
3. Discover the associated PR when one exists.
4. Prefer the associated PR base branch.
5. Otherwise use the remote default branch from `origin/HEAD`.
6. Otherwise fall back to an existing remote `origin/main` or `origin/master`.
7. Use a local-only `main` or `master` ref only when no better remote ref is available.
8. Resolve the selected base to a merge-base SHA with `HEAD`.
9. Pin the base ref and merge-base SHA for the current clean-review streak.
10. Attach any applicable `language_skill_packet` guidance to the local review plan before invoking native review.
11. Invoke native Codex review with the pinned base through `codex --yolo review` only after the CAS-first fallback condition has been recorded.
12. Capture the exact command, sandbox mode, base ref, base SHA, `HEAD` SHA, language skill packet, raw output, exit status, and parsed findings/comments.
13. Return `clean = true` only when the review completed successfully and produced zero findings/comments.

### Base discovery order

Use this hierarchy:

```text
1. Fetch remote refs.
2. If the current branch has an associated PR:
   use that PR's base branch.
3. Else:
   use the repository default branch from origin/HEAD.
4. Else:
   use origin/main or origin/master if present.
5. Else:
   use main or master only as a last resort if present locally.
6. Resolve the selected base to a merge-base SHA with HEAD.
7. Pin that merge-base SHA for the current clean-review streak.
```

For GitHub repositories, this shell shape is the preferred base-discovery model. Adapt it to the repository host when needed:

```bash
git fetch --prune origin

branch="$(git branch --show-current)"
head_sha="$(git rev-parse HEAD)"

pr_base="$({
  gh pr view --json baseRefName -q .baseRefName 2>/dev/null || true
} | tr -d '\r')"

if [ -n "$pr_base" ] && git rev-parse --verify --quiet "origin/$pr_base" >/dev/null; then
  base_ref="origin/$pr_base"
else
  default_branch="$({
    git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's#^origin/##' || true
  } | tr -d '\r')"

  if [ -n "$default_branch" ] && git rev-parse --verify --quiet "origin/$default_branch" >/dev/null; then
    base_ref="origin/$default_branch"
  elif git rev-parse --verify --quiet origin/main >/dev/null; then
    base_ref="origin/main"
  elif git rev-parse --verify --quiet origin/master >/dev/null; then
    base_ref="origin/master"
  elif git rev-parse --verify --quiet main >/dev/null; then
    base_ref="main"
  elif git rev-parse --verify --quiet master >/dev/null; then
    base_ref="master"
  else
    echo "Unable to determine review base" >&2
    exit 1
  fi
fi

base_sha="$(git merge-base HEAD "$base_ref")"
```

### Review invocation

Prefer invoking native Codex review with the merge-base SHA:

```bash
codex --yolo review --base "$base_sha"
```

If the installed Codex CLI rejects a SHA as `--base`, invoke it with the selected ref instead:

```bash
codex --yolo review --base "$base_ref"
```

`--yolo` is required for this skill's native review driver because trusted local `$resolve` runs frequently need reviewer subprocesses to execute repository validation probes without sandbox-level cache write failures. Record the sandbox mode as `danger-full-access/yolo` in the invocation ledger for every review run.

When the fallback ref form is used, still record the merge-base SHA and treat that SHA as the pinned comparison base for streak accounting. Do not silently switch from one base to another during a clean-review streak.

### Review output normalization

For each review run, normalize the Codex review result into this structure:

```text
review_result = {
  clean: boolean,
  backend_class: string,
  target_fingerprint: string|null,
  tool_completed: boolean,
  exit_status: integer,
  base_ref: string,
  base_sha: string,
  head_sha: string,
  invocation: string,
  sandbox_mode: string,
  raw_output: string,
  findings: [
    {
      id: string | null,
      file: string | null,
      line_range: string | null,
      severity: string | null,
      body: string,
      suggested_fix: string | null
    }
  ]
}
```

A review run is clean only when all are true:

- the tool completed successfully;
- the output explicitly indicates no findings/comments, or the parsed finding list is empty under the CLI's documented output format;
- there are no inline comments, requested changes, warnings, or substantive review notes;
- the backend class matches the currently pinned streak state, or this is the first review in a new streak;
- the target fingerprint matches the currently pinned streak state when the backend supplies one, or this is the first review in a new streak;
- the base ref, base SHA, and `HEAD` SHA match the currently pinned streak state, or this is the first review in a new streak.

Treat the following as not clean and investigate or block:

- CLI failure;
- missing or ambiguous output;
- partial output;
- transport failure;
- review produced comments but the parser failed to structure them;
- review ran against an unexpected base;
- review ran against a different `HEAD` than the current branch.

### Streak pinning

When `clean_review_streak == 0`, the next successful review driver call may establish a new pinned streak state:

```text
streak_base_ref = review_result.base_ref
streak_base_sha = review_result.base_sha
streak_head_sha = review_result.head_sha
streak_review_backend = review_result.backend_class
streak_target_fingerprint = review_result.target_fingerprint
```

For every subsequent review in the same streak:

- `review_result.backend_class` must match `streak_review_backend`;
- if `streak_target_fingerprint` is non-null, `review_result.target_fingerprint` must match it;
- `review_result.base_ref` must match `streak_base_ref` unless the ref name changed while resolving to the same intended PR/default branch and same `streak_base_sha`;
- `review_result.base_sha` must match `streak_base_sha`;
- `review_result.head_sha` must match `streak_head_sha`;
- otherwise reset `clean_review_streak = 0` and start a new streak.

If a fix changes `HEAD`, start a new streak even when the base is unchanged.

## Subagent policy

The resolve skill owns the state machine. Do not delegate the full review/fix/validate/commit/push/PR-sweep loop to a subagent.

Subagents may be used only for bounded, side-effect-light tasks that return structured results, such as:

- normalizing noisy review output into findings;
- detecting duplicate comments;
- summarizing PR thread context;
- comparing a comment against current code to determine whether it is obsolete;
- assisting `$review-adjudication` with context gathering.

Subagents must not:

- mutate the working tree independently;
- own `clean_review_streak`;
- choose or change the review base without returning control to the review driver;
- commit, push, resolve PR threads, or dismiss review comments;
- declare the skill complete.

## CAS-first backend policy

Prefer a persistent CAS lane for every ordinary `$resolve` run. Native Codex review through the local CLI is the fallback backend, not the default.

Use `$cas` when it passes a strict transport preflight. If CAS preflight fails, fall back to native `codex --yolo review` when available. If neither CAS nor native review can produce a reliable review result, stop as blocked and do not commit or push.

Before using `$cas` as a review backend, run a preflight that confirms:

1. `cas --version` and `cas review_session --version` report `0.2.31` or newer.
2. `cas review_session --help` exposes `lane start`, `lane review`, `lane status`, `lane stop`, `--lane-id`, `--json`, `--timeout-ms`, and `--fallback none|native-review`.
3. `cas review_session lane start --cwd <repo> --json --hooks off` starts a managed websocket app-server and returns a `laneId`.
4. `cas review_session lane status --lane-id <laneId> --json` proves the persisted lane process is alive.
5. The lane can be closed with `cas review_session lane stop --lane-id <laneId> --json`.
6. A `lane review` receipt can be normalized into the same `review_result` shape used by the native review driver.

If any CAS preflight step fails, record the failing step and fall back to native `codex review` when available. Do not skip CAS preflight merely because native review is expected to work.

CAS backend classification:

- `native-cli`: direct `codex --yolo review ...` through this skill's native review driver.
- `cas-lane`: `cas review_session lane review ... --json --fallback none` whose JSON proves `selectedTransport="websocket"`, `fallbackUsed=false`, `reviewResultAvailable=true`, `reviewResultSource="rollout_exited_review_mode"`, `dualParseVerdict="match"`, no blocking `failureCode`, and zero structured findings.
- `cas-native-fallback`: `cas review_session lane review ... --fallback native-review` when `fallbackUsed=true`; this is a degraded native review verdict, not persistent lane proof.

Pin the backend class and target fingerprint for each clean-review streak. A clean result from one backend class must not extend a streak started by another backend class, even when the base SHA and `HEAD` SHA match. Switching between `native-cli`, `cas-lane`, and `cas-native-fallback` resets `clean_review_streak` to zero and starts a new pinned streak only after the next completed clean review. Count `cas-native-fallback` only when its raw native-review output is normalized into the same zero-finding `review_result` shape; otherwise treat it as not clean and fall back or block.

CAS lane lifecycle for `$resolve`:

1. After base discovery and before the first review, start one lane with `cas review_session lane start --cwd <repo> --json --hooks off`.
2. Record `laneId`, `managedServerPid`, `managedServerListenUrl`, resolved `cas` path, and `cas` version in the review ledger.
3. For each review attempt, run `cas review_session lane review --lane-id <laneId> --base <base-ref-or-sha> --timeout-ms 900000 --json --fallback none`.
4. Treat each `lane review` as one review run with a fresh parent/review thread. Reusing the lane app-server must not reuse review context.
5. Keep CAS review attempts on `--fallback none` by default. Use `--fallback native-review` only after a CAS lane failure has been recorded and native fallback is intentionally allowed for that review attempt; classify any `fallbackUsed=true` receipt as `cas-native-fallback`.
6. Stop the lane with `cas review_session lane stop --lane-id <laneId> --json` on normal completion, branch mutation that abandons the lane, or abort. If stop fails, report it and continue cleanup checks; do not count stop success as review proof.

CAS same-handle timeout recovery:

1. If `lane review` exits nonzero with `failureCode="wait_timed_out"`, inspect the JSON receipt before falling back.
2. A recoverable timeout receipt must include `reviewThreadId`, `reviewTurnId`, `recordPath`, `eventLogPath`, `target`, `targetFingerprint`, `baseSha`, and `headSha`.
3. Recover with `cas review_session wait --review-thread-id <reviewThreadId> --timeout-ms 900000 --json` and normalize that wait receipt as the same review attempt.
4. Do not start a duplicate `lane review` for the same target while a recoverable timed-out `reviewThreadId` exists.
5. If the timeout receipt lacks the recoverable handle fields, classify it as CAS runtime failure, record the failed CAS step, reset any CAS-backed clean streak, and only then use the native fallback driver if available.

Even when `$cas` is used, the skill must preserve the same invariants:

- three consecutive clean review results are required;
- the backend class must be pinned for the streak;
- the `targetFingerprint`, base SHA, and `HEAD` SHA must be pinned for the streak;
- the base must be discovered and pinned;
- comments reset the streak;
- actionable comments go through `$review-adjudication` and `$fixed-point-driver`;
- validation, commit, push, and PR sweep gates still apply.

CAS receipts required for each CAS-backed review invocation:

- `cas` version and resolved CAS binary path.
- Exact `cas review_session` command and JSON output path or captured JSON.
- `laneId`, `managedServerPid`, `reviewThreadId`, `reviewTurnId`, `recordPath`, `eventLogPath`, `targetFingerprint`, `baseSha`, and `headSha`.
- `selectedTransport`, `fallbackUsed`, `fallbackTransport`, `failureCode`, `failureHint`, `reviewResultAvailable`, `reviewResultSource`, `dualParseVerdict`, and `archiveStatus`.
- Selected review base ref, base SHA, current `HEAD` SHA, normalized finding count, and backend class used for streak accounting.

## Local Codex review loop

Before making changes:

- Inspect the current branch and working tree.
- Identify the project-native build, lint, test, and type-check commands from repository files, lockfiles, package scripts, Makefiles, task runners, CI configuration, or project documentation.
- Discover and load applicable language/tool skills, then record their `language_skill_packet` guidance.
- Preserve unrelated user changes. Do not overwrite, discard, or stage unrelated work.
- Determine whether a PR already exists for the current branch, because that PR's base branch should drive the review base.

Repeat until `clean_review_streak == 3`:

1. Invoke the selected review driver.
2. If the driver cannot determine a valid base, cannot run CAS review, or cannot parse CAS output reliably, try the native fallback driver when available and record the fallback condition. If neither backend can produce a reliable review result, stop as blocked and do not commit or push.
3. If the review ran against a new `HEAD`, new base ref, or new base SHA, reset `clean_review_streak = 0` and pin the new streak state only after a successful review.
4. If the review returns zero findings/comments:
   - If this is the first clean review in a new streak, record `streak_base_ref`, `streak_base_sha`, and `streak_head_sha`.
   - Increment `clean_review_streak` by one.
   - If `clean_review_streak < 3`, run another Codex review immediately through the selected driver.
   - Do not treat one or two clean reviews as sufficient.
5. If the review returns any findings/comments:
   - Set `clean_review_streak = 0`.
   - For every review finding/comment, invoke `$review-adjudication`.
   - Classify each comment as either `address` or `do-not-address`.
   - Use `address` when the comment identifies a real correctness, reliability, security, maintainability, performance, accessibility, API-contract, data-loss, regression, release, or test-coverage issue.
   - Use `do-not-address` only when the comment is demonstrably incorrect, already fixed, a duplicate, unsupported by project conventions, out of scope for this branch, contradicted by requirements, or would make the code worse.
   - For every `address` decision, invoke `$fixed-point-driver` to implement the smallest correct fix.
   - After each fix or batch of related fixes, run targeted validation for the touched area.
   - Continue the review loop after fixes are applied.
6. If every comment is adjudicated as `do-not-address`, continue the review loop anyway. The commented review run is not clean and does not count toward the streak.

Do not use an arbitrary maximum iteration count. The normal stopping condition is exactly three consecutive Codex review runs from the pinned backend class with no comments. Stop early only for an unrecoverable blocker such as the review tool being unavailable, base discovery being impossible, required validation being impossible because of missing external credentials/services, or a persistent false-positive review loop that cannot be resolved without making the branch worse. If stopping early before commit/push, do not commit or push; report the blocker precisely.

## Review adjudication requirements

When invoking `$review-adjudication`, provide enough context for a deterministic decision:

- The exact review or PR comment text.
- Whether the source is native Codex review, CAS-backed review, or PR review.
- File path and line range, when available.
- The relevant code or diff context.
- The selected review base, base SHA, and current `HEAD` SHA.
- Any project conventions, requirements, prior comments, or tests that bear on the decision.
- The proposed consequence of addressing or declining the comment.

Keep a concise adjudication ledger so repeated comments can be recognized, but do not count repeated declined Codex review comments as clean reviews.

## Fixed-point driver requirements

When invoking `$fixed-point-driver`, pass:

- The review or PR comment being addressed.
- The `$review-adjudication` decision and rationale.
- Relevant code locations and diff context.
- The selected review base, base SHA, and current `HEAD` SHA.
- The expected behavior after the fix.
- The validation commands that should pass.

The fix should be minimal, correct, and consistent with repository style. Prefer small local changes over broad rewrites. Add or update tests when the issue is behaviorally meaningful or when tests are needed to prevent regression.

After `$fixed-point-driver` changes the branch:

- Inspect the diff.
- Run targeted validation for the changed area.
- Preserve unrelated work.
- Do not commit yet unless the full local review and validation gates have been satisfied.
- Reset `clean_review_streak = 0` and resume Codex review through the selected review driver.

## Final validation

After `clean_review_streak == 3`, run the full project validation suite. Prefer repository-native commands over generic guesses.

Use the strongest applicable commands available in the repository, such as:

- Build commands from CI, package scripts, Makefiles, task runners, or project docs.
- Lint commands from CI, package scripts, pre-commit configuration, or language tooling.
- Test commands from CI, package scripts, framework config, or project docs.
- Type checks when the project uses typed languages or type-check scripts.

If a validation command fails:

1. Capture the failure.
2. Invoke `$fixed-point-driver` to fix it.
3. Run targeted validation for the fix.
4. Reset `clean_review_streak = 0`.
5. Restart the selected Codex review loop through the review driver.

Do not skip builds, lints, tests, or type checks merely because the branch has three clean reviews.

## Commit and push

Only after the final three-review clean streak and full validation pass:

1. Inspect `git status` and the final diff.
2. Stage only intended changes.
3. If there are intended changes, commit with a concise message that summarizes the fixes.
4. Push the current branch to its upstream remote.
5. Record:
   - The final commit SHA.
   - The branch pushed.
   - The selected review base ref and merge-base SHA.
   - The exact last three Codex review invocations, their backend class, and their recorded sandbox mode or CAS receipts.
   - The language/tool skills loaded for the run, with trigger evidence and any proof-environment guidance used.
   - The validation commands that passed.
   - Confirmation that the last three Codex review runs came from the pinned backend class and had zero findings/comments.
   - Any Codex review comments adjudicated as `do-not-address`, with brief rationale, if relevant.
6. Run the post-push PR comment sweep before reporting completion.

If there are no intended changes after validation, do not create an empty commit. Push only if the branch needs to be updated on the remote, then run the post-push PR comment sweep.

Do not commit or push when:

- the working tree contains unresolved unrelated changes;
- validation failed;
- fewer than three consecutive clean reviews have completed;
- the review base is unknown or ambiguous;
- review output could not be parsed reliably;
- an actionable review or PR comment remains unresolved.

## Post-push PR comment sweep

After each successful push, inspect the pull request associated with the current branch.

### PR discovery

- Prefer repository-native tooling or provider-native tooling for the host. For GitHub repositories, use the GitHub CLI or equivalent API/tooling to locate the open PR for the current branch.
- If there is no associated PR, report that no PR was found and complete only if the local review, validation, commit, and push gates have passed.
- If multiple associated PRs are found and the correct PR is ambiguous, treat that as a blocker and report the candidates instead of guessing.
- Prefer the PR associated with the current branch and current repository over unrelated forks or stale branches.

For GitHub repositories, this command shape is acceptable for discovery:

```bash
gh pr view --json number,url,state,headRefName,baseRefName,headRefOid,baseRefOid,reviewDecision
```

### PR comments in scope

Process these comment types when visible after the push:

- Inline code review comments on the diff.
- Unresolved review threads.
- PR conversation comments that contain concrete code, test, behavior, architecture, product, release, security, accessibility, performance, or maintainability feedback.
- Requested-changes review summaries and review body comments.
- Bot or automation comments only when they contain actionable build, lint, test, security, dependency, release, or policy feedback that is not already covered by validation.

### PR comments out of scope

Do not adjudicate these as actionable comments:

- Pure status updates, acknowledgements, approvals, emoji-only comments, or automated noise with no actionable content.
- Comments authored by this agent solely to explain an adjudication or fix.
- Comments that are already resolved, dismissed, or obsolete against the latest pushed commit, unless they still describe a current defect.
- Comments unrelated to the current branch or PR.

Maintain a concise PR comment ledger keyed by provider comment/thread/review ID when available, otherwise by file path, line range, body, author, and commit SHA. Use the ledger only to avoid reprocessing identical comments in the same run; do not use it to ignore a changed or newly relevant comment.

For every in-scope PR comment that has not already been adjudicated with the same content and context:

1. Invoke `$review-adjudication`.
2. Provide the same quality of context required for Codex review comments:
   - Exact PR comment text.
   - Author, timestamp, URL, and provider ID when available.
   - File path and line range for inline comments when available.
   - Relevant code, diff, commit, and PR context.
   - Current branch state and any related validation results.
   - Selected review base and current `HEAD` SHA.
   - The consequence of addressing or declining the comment.
3. Classify the comment as either `address` or `do-not-address`.
4. Use `address` when the PR comment identifies a real correctness, reliability, security, maintainability, performance, accessibility, API-contract, data-loss, regression, product-requirement, release, or test-coverage issue.
5. Use `do-not-address` only when the PR comment is demonstrably incorrect, already fixed, duplicate, obsolete, unsupported by project conventions, out of scope for this branch, contradicted by requirements, or would make the code worse.
6. For every `address` decision, invoke `$fixed-point-driver` to implement the smallest correct fix.
7. After each PR-driven fix or batch of related fixes, run targeted validation for the touched area.

### When PR comments cause changes

If PR comment handling changes code, config, dependencies, lockfiles, generated artifacts, docs required by behavior, or tests:

- Inspect the diff and preserve unrelated work.
- Reset `clean_review_streak = 0`.
- Restart the local Codex review loop and require three consecutive clean reviews again.
- Run full validation again after the new clean streak.
- Commit only the intended PR-comment fixes.
- Push the branch again.
- Run the post-push PR comment sweep again against the latest pushed commit.

### When PR comments are declined

When PR comments are all adjudicated as `do-not-address`:

- Do not make code changes solely to silence the comments.
- Do not pretend the PR has no comments. Report the declined comments and concise rationales.
- If repository workflow expects replies, leave concise PR replies explaining the adjudication, but do not resolve or dismiss reviewer comments unless they are demonstrably obsolete, duplicate, already fixed, or the repository convention permits the author to resolve them.
- Completion is allowed only if there are no actionable PR comments remaining.

If the same actionable PR comment persists after a fix and push, re-check the latest code and adjudicate it again. If it is now fixed or obsolete, classify it as `do-not-address` with the rationale `already fixed` or `obsolete against latest commit`. If it still identifies a real issue, invoke `$fixed-point-driver` again.

## Handling persistent review loops

A persistent loop is not success. Treat the following as blockers unless a minimal correct fix can break the loop:

- Codex review repeatedly emits the same false-positive finding and addressing it would make the branch worse;
- review output is unstable or contradictory in a way that prevents three consecutive clean reviews;
- base discovery changes every run due to branch or remote churn;
- validation requires credentials, services, or infrastructure that are unavailable;
- PR comments require product decisions, approvals, or external context that the agent does not have.

When blocked:

- stop before committing or pushing unless the branch was already safely committed and pushed before the blocker appeared;
- report the exact blocker;
- include the review base, `HEAD` SHA, relevant command output, and the unresolved comments/findings;
- do not fabricate completion.

## Final report

When the skill completes, report:

- The final commit SHA and branch pushed.
- The PR URL or a statement that no associated PR was found.
- The selected review base ref and merge-base SHA.
- The validation commands that passed.
- Confirmation that the last three Codex review runs came from the pinned backend class and had zero findings/comments.
- Confirmation that the post-push PR sweep was performed.
- PR comments addressed with fixes, if any.
- PR comments adjudicated as `do-not-address`, with brief rationale, if relevant.
- Any blockers or comments that could not be processed, if relevant.

## Non-negotiables

- Three consecutive clean Codex reviews from the pinned backend class are required; one or two clean runs are not enough.
- `$resolve` must attempt CAS lane review first; native Codex review is fallback-only.
- Native Codex review must run through the fallback review driver; do not nakedly call `codex review --base main`.
- Prefer the associated PR base branch; otherwise use the remote default branch; local `main` is a last-resort fallback only.
- The merge-base SHA must be recorded and pinned for the current clean-review streak.
- Comments adjudicated as `do-not-address` still reset the Codex review streak.
- Any code, config, dependency, lockfile, generated-artifact, or test change after the third clean review invalidates the streak and requires restarting Codex review.
- Post-push PR comments use the same `$review-adjudication` and `$fixed-point-driver` flow as local Codex review comments.
- Any PR-comment-driven change requires another local three-clean-review streak, full validation pass, commit, push, and PR sweep.
- The resolve skill owns the state machine; subagents may assist but must not own the loop.
- `$cas` is the default review backend and must pass websocket/app-server preflight before use; failed CAS preflight falls back to native review when available.
- Do not commit or push unless full validation passes.
- Do not stage unrelated work.
- Do not fabricate validation success, review outcomes, PR state, commit SHAs, or push status.
