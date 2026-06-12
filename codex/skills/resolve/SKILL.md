---
name: resolve
description: "Resolve the current branch through a CAS-first, receipt-backed review loop with native review as recorded fallback only. Use for `$resolve`, branch resolution, review/fix/validate/commit/push loops, PR comment sweep, three consecutive clean reviews, CAS review lanes, deterministic base/HEAD pinning, full review-adjudication route consumption, review-closure abstraction ladder, surface-budgeted fixed-point fixes, and final pushed readiness. Do not use for one-shot review, PR creation only, merging/landing, isolated adjudication, or final closure proof without branch mutation."
---

# resolve

## Purpose

Resolve the current branch to a pinned-review-clean, validated, committed, pushed, and PR-comment-swept state.

`$resolve` is a root-owned state machine. It does not merely review the branch. It keeps reviewing, adjudicating, selecting the right abstraction route, fixing only when warranted, validating, committing, pushing, and sweeping visible PR comments until the branch reaches the completion bar or a precise blocker stops the run.

## Activation Kernel

Use `$resolve` when the user wants the current branch driven to completion through review/fix/validate/push and PR-sweep closure.

Do not use `$resolve` when:

- the user wants a one-shot review only; use the relevant review skill or command directly.
- the user wants PR creation or proof publication only; use `$ship`.
- the user wants merge, checks-watch, branch cleanup, or final PR landing; use `$land`.
- the user wants to decide whether comments are actionable but not run the branch loop; use `$review-adjudication`.
- the user wants final readiness/closure proof after material work; use `$verification-closure`.
- the user wants implementation of a known warrant only; use `$fixed-point-driver` / `$accretive-implementer` as appropriate.

Default mode: **full branch resolution, CAS-first**.

Mutation authority: root-owned only. Specialist workers and sidecars may gather evidence but must not mutate, stage, commit, push, resolve threads, own the review streak, or declare completion.

Completion bar:

```text
3 consecutive clean reviews
+ pinned backend/base/head/fingerprint
+ full validation pass
+ intended commit/push
+ complete post-push PR sweep
+ no unprocessed in-scope PR comments
+ no actionable PR comments remaining
```

## Entry guard

Before any review command runs, prove this run has loaded enough of this skill to include:

- `## Backend selection`
- `## Review adjudication route consumption`
- `## Review-Closure Abstraction Ladder`
- `## Fixed-point and implementation handoff`
- `## Non-negotiables`

A partial read of only the top of this file is not enough to operate `$resolve`.

Record one of these facts before the first review attempt:

- CAS preflight/review was attempted through the review driver and produced a receipt or a concrete failure.
- The user explicitly requested native review for the current run.

The following facts are not native fallback conditions:

- the hosted PR has no actionable review threads;
- the hosted PR has no checks or an empty `statusCheckRollup`;
- the hosted PR only has a Codex usage-limit notice;
- a local de novo review signal would be useful;
- `gh pr view` reports a clean merge state or no requested changes.

If native review has already run before a CAS preflight/fallback fact was recorded, treat that review as invalid for `$resolve` streak accounting. Do not count it as clean, do not use it to justify backend choice, and restart from the CAS-first guard. If the invalidly ordered native run found a real issue, adjudicate and fix the issue on its merits, then restart the CAS-first loop.

## Completion criteria

Do not consider the branch resolved until all of the following are true, in this order:

1. The selected Codex review backend has produced three consecutive clean review runs against the current branch through the review driver.
2. A clean review means no findings, no comments, no requested changes, and no unresolved review output.
3. Any review run with one or more findings/comments resets the clean-review streak, even when every item is later adjudicated as `do-not-address`, `resolve-thread-only`, `validate-only`, or `blocked`.
4. The review base is discovered by the review driver, pinned for the streak, and recorded.
5. The backend class, target fingerprint when available, base SHA, and `HEAD` SHA remain pinned for the streak.
6. After the third clean review, all required builds, lints, tests, type checks, and repository-native validation commands pass.
7. If validation requires any code, config, dependency, lockfile, generated-artifact, behavior-doc, or test change, reset the clean-review streak and restart the selected review loop.
8. Only after the final clean-review streak and final validation pass may the branch be committed and pushed.
9. After each push, find the associated PR and perform the complete post-push PR sweep.
10. Every in-scope Codex review item and PR item must be consumed through `$review-adjudication` unless it is clearly irrelevant system noise, already resolved, authored by this agent as a status/reply, or previously adjudicated with the same content and current artifact context.
11. Every mutation-capable adjudication route must pass the Review-Closure Abstraction Ladder before any production mutation.
12. Every mutation-capable route that survives the ladder must go through `$fixed-point-driver` with a surface-budgeted handoff unless the selected ladder rung blocks, validates only, or explicitly returns no-change.
13. If PR-comment resolution causes any code/config/dependency/generated/test/doc change, repeat the Codex review loop until three consecutive clean reviews, rerun full validation, commit, push, and sweep again.
14. The skill is complete only after the latest pushed commit has the final clean review streak, final validation pass, complete post-push sweep, and zero unresolved actionable PR comments.

## Definitions

- `native Codex review`: the Codex CLI/repository-native review command, normally `codex review`, not a separate invented LLM review.
- `review backend`: the review execution class used for streak accounting: `cas-lane` by default, `native-cli` or `cas-native-fallback` only after recorded fallback.
- `review driver`: the deterministic wrapper that discovers base, invokes the selected backend, captures receipts, normalizes findings, and classifies whether a review was clean.
- `clean review`: a completed review result from the selected backend with zero findings/comments/requested changes, no unresolved review notes, and matching pinned state.
- `review item`: any substantive review item, inline comment, requested change, warning, issue, or note that asks for or implies a code, test, behavior, safety, reliability, performance, accessibility, maintainability, API, release, or documentation change.
- `mutation-capable route`: an adjudication route that could change production code, validation code, fixtures, generated artifacts, config, behavior docs, dependencies, or lockfiles.
- `HEAD changed`: the current commit SHA changed because of a fix, generated update, validation fix, rebase, merge, amend, cherry-pick, or branch synchronization.
- `base changed`: the resolved base ref or merge-base SHA changed since the current clean streak began.

## State to maintain

Maintain this state during the run:

```yaml
resolve_state:
  resolve_run_id: "<timestamp/branch/short-head>"
  clean_review_streak: 0
  streak_review_backend: null
  streak_target_fingerprint: null
  streak_base_ref: null
  streak_base_sha: null
  streak_head_sha: null
  last_review_invocations: []
  adjudication_ledger: {}
  abstraction_route_ledger: []
  implementation_handoff_ledger: []
  validation_commands: []
  pr_comment_ledger: {}
  pr_sweep_inventory_status: unknown
  language_skill_packet: {}
  parallel_task_ledger: []
  durable_run_dir: null
```

Reset `clean_review_streak = 0` whenever:

- review returns any finding/comment;
- the Review-Closure Abstraction Ladder selects a mutation route and the branch changes;
- `$fixed-point-driver` or downstream implementation changes code, config, dependencies, lockfiles, generated artifacts, behavior docs, or tests;
- validation requires any fix or generated update;
- `HEAD` changes;
- backend class changes;
- the review driver resolves a different base ref or base SHA;
- PR comment handling changes the branch;
- rebase, merge, amend, cherry-pick, or branch synchronization changes the comparison.

Do not reset the streak merely because another clean review was run. Increment only for completed clean reviews from the pinned backend class against the pinned base and current `HEAD`.

## Durable run ledger

For long or mutating runs, create or maintain a local operational ledger outside committed source, for example:

```text
~/.codex/resolve/runs/<repo-name>/<timestamp-or-branch>/
  resolve-state.json
  review-*.json
  adjudication-ledger.jsonl
  abstraction-route-ledger.jsonl
  implementation-handoff-ledger.jsonl
  pr-comment-ledger.jsonl
  validation-ledger.jsonl
  parallel-task-ledger.jsonl
```

Do not commit this ledger. Use it to survive context loss, CAS waits, retries, and PR sweep restarts. If no durable ledger is used, state why in the final report.

## Language-specific skill routing

`$resolve` owns discovery and routing, not language-specific proof mechanics.

Before the first review run, and again whenever the changed file set materially changes, inspect repository and diff signals:

- changed file extensions and manifests such as `build.zig`, `Cargo.toml`, `package.json`, `pyproject.toml`, `go.mod`, `mix.exs`, `lakefile.lean`, or equivalent project roots;
- validation commands from CI, task runners, package scripts, project docs, or prior successful runs;
- explicit user-mentioned skills;
- review failures that identify a language tool, cache, compiler, package manager, formatter, linter, or test runner.

For every applicable language/tool skill available, load that skill before selecting proof commands or invoking review. Keep a concise `language_skill_packet`:

```yaml
language_skill_packet:
  skill_name:
  trigger_evidence:
  loaded: true|false
  review_guidance_summary:
  validation_guidance_summary:
```

Pass relevant guidance into review context and validation planning. For Zig projects, `$resolve` should route to `$zig`; `$zig` owns writable cache paths, Zig version/proof lanes, lint/test command shape, and cache-environment failure classification. `$resolve` must not hardcode Zig-specific environment variables or cache paths except as a direct quote from loaded `$zig` guidance.

If a clearly applicable skill cannot be loaded, record that as a limitation and proceed only when repository-native proof commands are already reliable enough. Block when missing guidance is required to distinguish tool transport failure from code failure.

## Backend selection

`$resolve` is CAS-first.

After base discovery and language-skill routing, attempt the persistent CAS lane preflight before any native `codex review` invocation.

Use native Codex review only when one of these fallback conditions is true:

- CAS preflight fails or proves the installed `cas` / `cas review_session` surface is too old or incompatible.
- CAS lane startup, status, review, timeout recovery, or receipt normalization fails in a way that prevents a reliable verdict.
- CAS reports a blocking transport/runtime failure and native fallback is the only available review path.
- The user explicitly requests native review for the current run.

Do not choose native review merely because it is simpler, faster to type, historically common, or the run seems one-shot. `$resolve` is a multi-cycle remediation workflow; its normal review primitive is CAS lane review with fallback disabled unless explicitly degraded.

Load `$cas` review backend guidance before CAS preflight. `$resolve` owns review streak state; `$cas` owns lane command shape, version gates, receipt field meanings, timeout recovery semantics, and fallback classification.

See `references/cas-review-backend.md`.

## Native fallback review driver

All native review invocations must go through the fallback driver. Do not nakedly call `codex review --base main` except as a documented last-resort fallback when no remote default branch, PR base, or usable remote ref can be discovered.

The driver must:

1. Inspect current branch and working tree.
2. Fetch remote refs before selecting base.
3. Discover the associated PR when one exists.
4. Prefer the associated PR base branch.
5. Otherwise use remote default branch from `origin/HEAD`.
6. Otherwise use `origin/main` or `origin/master` if present.
7. Use local `main` or `master` only as last resort.
8. Resolve selected base to merge-base SHA with `HEAD`.
9. Pin base ref and merge-base SHA for the clean streak.
10. Attach applicable `language_skill_packet` guidance.
11. Invoke native review only after CAS-first fallback condition has been recorded.
12. Capture exact command, sandbox mode, base ref, base SHA, `HEAD` SHA, language packet, raw output, exit status, and parsed findings/comments.
13. Return clean only when the review completed successfully and produced zero findings/comments.

See `references/native-review-driver.md`.

## Review result normalization

Normalize every review run into:

```yaml
review_result:
  clean: true|false
  backend_class: cas-lane | native-cli | cas-native-fallback
  target_fingerprint: string|null
  tool_completed: true|false
  exit_status: integer|null
  base_ref: string
  base_sha: string
  head_sha: string
  invocation: string
  sandbox_mode: string|null
  raw_output_ref: string
  findings: []
```

A review run is clean only when all are true:

- tool completed successfully;
- output explicitly indicates no findings/comments, or the parsed finding list is empty under the documented format;
- there are no inline comments, requested changes, warnings, or substantive review notes;
- backend class matches the pinned streak state, or this is the first clean review in a new streak;
- target fingerprint matches when supplied, or this is the first clean review in a new streak;
- base ref, base SHA, and `HEAD` SHA match the pinned streak state, or this is the first clean review in a new streak.

Treat CLI failure, missing/ambiguous output, partial output, transport failure, parser failure, unexpected base, or wrong `HEAD` as not clean.

See `references/review-result-contract.md`.

## Specialist worker and parallelism policy

`$resolve` owns the state machine. Do not delegate the full review/fix/validate/commit/push/PR-sweep loop to a specialist worker.

Workers or sidecars may be used only for bounded, side-effect-light tasks that return structured evidence:

- review-output normalization;
- duplicate comment detection;
- PR thread context summarization;
- obsolete-comment checks against current code;
- read-only evidence gathering for `$review-adjudication`;
- read-only evidence gathering for Review-Closure Abstraction Ladder rungs;
- PR inventory fetching;
- receipt summarization after the root captures `.reviewVerdict`.

Workers and sidecars must not:

- mutate the working tree, index, dependencies, lockfiles, generated artifacts, or repo config;
- own `clean_review_streak`;
- choose or change review base;
- start duplicate review attempts for the same backend/base/head/fingerprint tuple;
- commit, push, resolve PR threads, dismiss comments, or declare completion.

Use parallelism when it reduces wall time without increasing state ambiguity. Do not launch sidecars merely because work is technically independent; each sidecar must have a named decision it can improve.

See `references/parallelism-contract.md`.

## Review loop

Before making changes:

- inspect the current branch and working tree;
- identify build/lint/test/typecheck commands from repository files, CI, docs, or language skills;
- discover and load applicable language/tool skills;
- preserve unrelated user changes;
- determine whether a PR exists for the current branch;
- run a value-gated parallel opportunity pass for read-only discovery, CAS checks, PR metadata/thread fetching, CI/check discovery, and validation command discovery.

Repeat until `clean_review_streak == 3`:

1. Invoke the selected review driver.
2. If no backend can produce a reliable result, stop blocked; do not commit or push.
3. If review ran against a new `HEAD`, base ref, base SHA, backend, or fingerprint, reset/pin streak only after a successful clean review.
4. If review returns zero findings/comments:
   - establish or verify streak pins;
   - increment `clean_review_streak`;
   - if streak < 3, run another review immediately through the selected driver;
   - do not treat one or two clean reviews as sufficient.
5. If review returns findings/comments:
   - reset `clean_review_streak = 0`;
   - process every review item through `$review-adjudication`;
   - consume full adjudication routes and warrants;
   - run the Review-Closure Abstraction Ladder for every mutation-capable route before production mutation;
   - route surviving mutation-capable items through `$fixed-point-driver`;
   - run targeted validation for changed areas;
   - restart the review loop after fixes.
6. If every item is adjudicated as no-change/do-not-address/resolve-thread-only, continue the review loop anyway. That review run is not clean and does not count toward the streak.

Do not use an arbitrary maximum iteration count. Stop early only for an unrecoverable blocker such as unavailable review backend, impossible base discovery, required validation blocked by missing external credentials/services, persistent false-positive review loop that cannot be resolved without making the branch worse, or incomplete PR sweep inventory that prevents a completion claim.

## Review adjudication route consumption

When invoking `$review-adjudication`, provide:

- exact review or PR item text;
- source: native review, CAS review, PR review, PR thread, PR conversation, bot output;
- provider ID, URL, author, timestamp when available;
- file path and line range when available;
- relevant code/diff context;
- selected review base, base SHA, and current `HEAD` SHA;
- project conventions, requirements, prior related comments, tests, CI, and language skill guidance;
- proposed consequence of each route.

Consume the full Claim Decision Kernel and Resolution Warrants. Do not collapse routes to only `address` / `do-not-address`.

Route handling:

- `address` with `mutate-code`: run Review-Closure Abstraction Ladder, then route surviving mutation to `$fixed-point-driver`.
- `delete-collapse-canonicalize` with `mutate-code`: run Review-Closure Abstraction Ladder, with isomorphic simplification or fixed-point ablation preferred.
- `validate-only` with `add-validation-only`: run/add validation-only proof. If files change, reset review streak after proof change.
- `resolve-thread-only` with `resolve-thread`: resolve/reply only when provider policy permits and proof is current.
- `do-not-address` with `draft-reply`, `defer`, or `none`: record rationale; the review run still does not count as clean.
- `blocked` with `none`: stop before commit/push.

See `references/adjudication-route-contract.md`.

## Review-Closure Abstraction Ladder

Before any review-driven production mutation, consume the `$review-adjudication` route and select the earliest applicable abstraction route from this ladder.

The ladder is an anti-accretion spine:

```text
2. complexity-mitigator
3. simplify-and-refactor-code-isomorphically
4. reduce
5. universalist
6. fixed-point-driver
7. accretive-implementer
```

Earliest owner wins. Do not run every rung by default. Select the earliest rung that owns the dominant pathology, and record why later rungs were not selected.

No review-driven production mutation may proceed directly from `address`. `address` only means the review item is potentially actionable. The ladder decides the route.

### 2. complexity-mitigator

Use when the finding touches branchy, nested, flag-heavy, hard-to-follow, cross-file, mutable-state, or specification-risky code.

Expected output: Micro Preflight and smallest clarity cut.

This rung blocks patching code the agent does not understand.

### 3. simplify-and-refactor-code-isomorphically

Use when the proposed fix would add or preserve helper/wrapper/adapter/branch/test-case accumulation, duplicate/pass-through/shadow surface, near-clones, parameter-sprawl, local defensive code, or obvious behavior-preserving collapse opportunities.

Expected output: isomorphic refactor preflight, equivalence proof route, or behavior-preserving collapse route.

This rung blocks adding code when behavior-preserving collapse is available.

### 4. reduce

Use when the finding adds, preserves, or works around layer/tooling/framework/generated/config abstraction tax: adapters, registries, dependency injection, plugin surfaces, generated clients, codegen, ORMs, GraphQL, task runners, workflow engines, queues, infra wrappers, or config indirection.

Expected output: `descend | hold | split | ask-universalist`.

This rung blocks adding another layer to compensate for layer tax.

### 5. universalist

Use when repeated findings indicate a missing boundary artifact, protocol/state-machine artifact, explicit IR, effect signature, context certificate, canonical composition seam, or wrong shape of truth.

Expected output: one-seam boundary/construction call, obstruction report, or proof signal.

This rung blocks local patches when the boundary artifact is missing.

### 6. fixed-point-driver

Use when findings are coupled, repeated, invariant-linked, deletion-sensitive, likely to reopen, or involve duplicate truth owners, additive scaffolds, or unresolved ablation pressure.

Expected output: normal-form route, ablation status, surface budget, and implementation handoff.

This rung blocks repeated local fixes that should become normal-form repair.

### 7. accretive-implementer

Use only after route selection as the single-writer executor.

Expected output: `right_sized_route`, `surface_delta_call`, and proof receipt.

This rung blocks direct mutation before route selection.

## Review-Closure Abstraction Receipt

Every mutation-capable review item must leave this compact receipt in the durable ledger or final report:

```yaml
review_closure_abstraction_receipt:
  review_item_id: "..."
  adjudication_route: "address | delete-collapse-canonicalize | validate-only | resolve-thread-only | do-not-address | blocked"
  primary_smell:
    hard_to_understand_or_spec_risk: yes|no
    duplicate_or_pass_through_surface: yes|no
    layer_or_tooling_tax: yes|no
    missing_boundary_artifact: yes|no
    coupled_or_repeated_findings: yes|no
    implementation_only_after_route_selection: yes|no
  earliest_applicable_rung: "complexity-mitigator | simplify-isomorphic | reduce | universalist | fixed-point-driver | accretive-implementer"
  selected_skill: "..."
  reason_selected: "..."
  rejected_later_rungs:
    - skill: "..."
      reason: "earlier rung owned the pathology"
  selected_route: "no-change | validate-only | delete-collapse-canonicalize | refactor-existing-owner | mutate-existing-owner | add-new-surface | blocked"
  proof_required: []
```

If the receipt cannot be filled for a mutation-capable review item, do not mutate. Route to validation-only, fixed-point blocked, or ask for missing owner/context.

See `references/review-closure-abstraction-ladder.md`.

## Cluster and moratorium rules

Track review items by subsystem, file, protocol, state machine, parser/validator, lifecycle, retry/idempotency path, cache/index, impossible-state family, and truth owner.

If three review findings in the same cluster appear in one `$resolve` run, stop point-fix mutation for that cluster.

Required next artifact:

```yaml
cluster_refactor_moratorium:
  cluster_id:
  review_item_ids:
  suspected_owner:
  invariant_or_protocol:
  local_patches_already_attempted:
  duplicate_or_shadow_surfaces:
  selected_route:
    no-change | validate-only | delete-collapse-canonicalize | refactor-existing-owner | mutate-existing-owner | add-new-surface | blocked
  required_skill:
    complexity-mitigator | simplify-and-refactor-code-isomorphically | reduce | universalist | fixed-point-driver
  proof_required:
```

The moratorium may lift only after the selected skill produces a route and proof plan, or the root records a blocker.

See `references/cluster-refactor-moratorium.md`.

## Fixed-point and implementation handoff

When invoking `$fixed-point-driver`, pass:

- the review/PR item being addressed;
- `$review-adjudication` decision, route, warrant, and rationale;
- Review-Closure Abstraction Receipt;
- relevant code locations and diff context;
- selected review base, base SHA, and current `HEAD` SHA;
- expected behavior after fix;
- validation commands that should pass;
- permitted scope;
- forbidden actions;
- surface budget;
- ablation status;
- proof required;
- stale conditions.

The handoff must be surface-budgeted. Do not simply say "fix minimally."

Minimum handoff shape:

```yaml
implementation_handoff:
  source_skill: resolve
  target_skill: fixed-point-driver
  artifact_state_id: "..."
  review_item_id: "..."
  abstraction_ladder_rung: "complexity-mitigator | simplify-isomorphic | reduce | universalist | fixed-point-driver | accretive-implementer"
  selected_adjudication_route: address | delete-collapse-canonicalize | validate-only | resolve-thread-only | do-not-address | blocked
  selected_route: no-change | validate-only | delete-collapse-canonicalize | refactor-existing-owner | mutate-existing-owner | add-new-surface | blocked
  permitted_action: mutate-code | add-validation-only | resolve-thread | draft-reply | defer | none
  permitted_scope: []
  forbidden_actions: []
  surface_budget:
    production_surface: zero_or_negative | bounded_positive | explicit_expansion
    added_helpers_allowed: yes | no
    added_wrappers_adapters_allowed: yes | no
    added_flags_or_fallbacks_allowed: yes | no
    public_symbols_allowed: yes | no
    compatibility_paths_allowed: yes | no
  ablation_status: not-required | local-preflight | external-clearance-required | blocked
  proof_required: []
  stale_if: []
```

After `$fixed-point-driver` changes the branch:

- inspect the diff;
- run targeted validation;
- preserve unrelated work;
- do not commit yet unless all local review and validation gates have passed;
- reset `clean_review_streak = 0`;
- resume review through the selected driver.

See `references/implementation-handoff.md`.

## Final validation

After `clean_review_streak == 3`, run the full project validation suite.

Prefer repository-native commands from CI, package scripts, Makefiles, task runners, project docs, or applicable language/tool skills.

If a validation command fails:

1. Capture the failure.
2. Invoke `$review-adjudication` only if actionability is contested; otherwise process the validation failure through the Review-Closure Abstraction Ladder when production mutation may result.
3. Route surviving mutation through `$fixed-point-driver`.
4. Run targeted validation for the fix.
5. Reset `clean_review_streak = 0`.
6. Restart the selected review loop.

Do not skip builds, lints, tests, or type checks merely because the branch has three clean reviews.

If no validation command exists, do not silently treat validation as passed. Report validation as blocked, or route a validation-only proof addition/discovery if mutation authority permits. Commit/push is blocked unless the user explicitly accepts manual-only proof for this branch and the final report says validation was manual-only.

See `references/validation-policy.md`.

## Commit and push

Only after the final three-review clean streak and full validation pass:

1. Inspect `git status` and final diff.
2. Stage only intended changes.
3. If intended changes exist, commit with a concise message.
4. Push current branch to upstream remote.
5. Record final commit SHA, branch pushed, review base, merge-base SHA, last three review invocations/receipts, language skill packets, validation commands, abstraction route ledger, implementation handoff ledger, and parallel task ledger.
6. Run the post-push PR sweep before reporting completion.

If there are no intended changes after validation, do not create an empty commit. Push only if the branch needs remote update, then run the PR sweep.

Do not commit or push when:

- unrelated working-tree changes are unresolved;
- validation failed or is blocked;
- fewer than three consecutive clean reviews have completed;
- review base is unknown/ambiguous;
- review output could not be parsed reliably;
- actionable review/PR comment remains unresolved;
- any gate used stale or mismatched sidecar output;
- PR sweep inventory is incomplete and the run is claiming PR-comment-reviewed completion.

## Post-push PR sweep

After each successful push, inspect the PR associated with the current branch.

If no associated PR exists, report `pr_sweep_inventory_status: no_pr` and complete only if local review, validation, commit, and push gates passed.

If multiple PRs are associated and ambiguous, block instead of guessing.

For GitHub repositories, prefer a complete paginated review-thread inventory before claiming PR sweep complete.

Process:

1. Discover PR metadata and verify the checked PR `headRefOid` matches the latest pushed commit.
2. Collect PR conversation comments, review summaries, requested changes, inline comments, unresolved threads, bot comments, and status/check comments.
3. Collect a complete paginated review-thread inventory when provider tooling supports it:
   - `totalCount`;
   - `pageInfo.hasNextPage` / `endCursor`;
   - thread `id`;
   - `isResolved`;
   - `isOutdated`;
   - path/line;
   - latest comment author/body/url;
   - associated commit/head where available.
4. If pagination fails, `totalCount` is missing, or collected thread count is less than `totalCount`, mark sweep incomplete.
5. For every in-scope unprocessed item, invoke `$review-adjudication` and consume full routes.
6. For mutation-capable routes, run the Review-Closure Abstraction Ladder and then invoke `$fixed-point-driver` with surface-budgeted handoff.
7. If PR handling changes the branch, reset review streak and repeat review/validation/commit/push/sweep.

In-scope PR items:

- inline review comments;
- unresolved review threads;
- concrete PR conversation comments;
- requested-changes summaries;
- actionable bot/automation comments about build, lint, test, security, dependency, release, or policy feedback.

Out-of-scope PR items:

- pure status updates, approvals, acknowledgements, emoji-only comments, or automation noise with no actionable content;
- comments authored by this agent as status/reply;
- already resolved/dismissed/obsolete comments unless still describing current defects;
- comments unrelated to the current branch/PR.

See `references/pr-sweep-contract.md`.

## Handling declined comments

When comments are adjudicated as no-change/do-not-address/defer:

- do not make code changes solely to silence them;
- do not pretend the review or PR had no comments;
- record concise rationale;
- reply or resolve only when repository/provider policy permits and the adjudication route authorizes it;
- completion is allowed only if no actionable PR comments remain.

If the same actionable PR comment persists after a fix/push, re-check latest code and adjudicate again. If it is now fixed/obsolete, classify accordingly. If it still identifies a real issue, route again.

## Handling persistent review loops

A persistent loop is not success. Treat these as blockers unless a minimal correct fix can break the loop:

- repeated false-positive review finding where addressing it would make branch worse;
- unstable/contradictory review output preventing three clean reviews;
- base discovery changes every run;
- validation requires unavailable credentials/services/infrastructure;
- PR comments require product decisions, approvals, or external context;
- parallel/worker results repeatedly stale, contradictory, or snapshot-mismatched;
- PR thread inventory cannot be completed but the run is asked to claim PR-comment-reviewed completion;
- abstraction ladder repeatedly selects mutation in the same cluster without reducing or clarifying the owner.

When blocked:

- stop before committing/pushing unless already safely committed/pushed before blocker appeared;
- report exact blocker;
- include review base, `HEAD` SHA, relevant output, unresolved comments/findings, abstraction route ledger, PR inventory status, and parallel ledger entries when relevant;
- do not fabricate completion.

## Final report

When complete or blocked, report:

```text
Resolve:
- status: resolved | blocked | partial
- resolve_run_id:
- branch:
- final_commit:
- pushed_to:
- PR:

Review closure:
- backend_class:
- base_ref:
- base_sha:
- head_sha:
- target_fingerprint:
- clean_review_streak:
- review_receipts:

Validation:
- commands_passed:
- commands_blocked_or_not_available:
- validation_mode: full | partial | manual-only | blocked

Adjudication:
- review_items: address=N, delete-collapse-canonicalize=N, validate-only=N, resolve-thread-only=N, do-not-address=N, blocked=N
- pr_items: address=N, delete-collapse-canonicalize=N, validate-only=N, resolve-thread-only=N, do-not-address=N, blocked=N

Review-Closure Abstraction Ladder:
- rungs_selected: complexity-mitigator=N, simplify-isomorphic=N, reduce=N, universalist=N, fixed-point-driver=N, accretive-implementer=N
- no_direct_address_to_patch: yes|no
- clusters_moratorium_triggered:
- selected_routes:
- blocked_by_route_selector:

Implementation:
- fixed_point_runs:
- implementation_handoffs:
- accretive_implementer_routes:
- surface_delta_calls:
- ablation_statuses:

PR sweep:
- inventory_status: complete | incomplete | no_pr | blocked
- unresolved_actionable_comments:

Parallelism:
- sidecars_used:
- stale_or_rejected_results:

Resolve Bottom Line:
- status:
- strongest proof:
- open blocker:
- exact next action:
```

`Resolve Bottom Line` must be final.

## Non-negotiables

- Three consecutive clean Codex reviews from the pinned backend class are required; one or two clean runs are not enough.
- `$resolve` must attempt CAS lane review first; native review is fallback-only.
- Native review must run through the fallback driver; do not nakedly call `codex review --base main`.
- Prefer the associated PR base branch; otherwise use the remote default branch; local `main` is last resort only.
- The merge-base SHA must be recorded and pinned.
- Comments adjudicated as no-change/do-not-address/resolve-thread-only still reset the review streak.
- Any code, config, dependency, lockfile, generated-artifact, behavior-doc, or test change after the third clean review invalidates the streak and requires restarting review.
- Post-push PR comments use the same `$review-adjudication`, Review-Closure Abstraction Ladder, and `$fixed-point-driver` route/warrant flow as local review comments.
- Any PR-comment-driven change requires another local three-clean-review streak, full validation, commit, push, and PR sweep.
- `$resolve` owns the state machine; workers/sidecars may assist but must not own mutable state or completion.
- `$cas` is the default review backend and must pass preflight before use; failed CAS preflight falls back to native review only when available and recorded.
- Parallel work may assist only as evidence gathering, normalization, context preparation, or safe validation; it must not mutate branch state.
- Do not start duplicate review attempts for the same backend/base/head/target-fingerprint tuple while a process or recoverable review handle is alive.
- Do not count parallel review runs as the required three consecutive clean streak.
- Do not commit or push unless full validation passes or explicit manual-only proof is accepted and reported.
- Do not stage unrelated work.
- Do not collapse `$review-adjudication` routes into `address`/`do-not-address`.
- Do not route mutation directly from `address` to `apply_patch`.
- Do not skip the Review-Closure Abstraction Ladder for mutation-capable routes.
- Do not route mutation to `$fixed-point-driver` without the abstraction receipt, surface budget, ablation status, forbidden actions, and proof required.
- Do not claim PR-comment-reviewed completion with incomplete PR sweep inventory unless the limitation is reported as a blocker or downgrade.
- Do not fabricate validation success, review outcomes, PR state, commit SHAs, push status, abstraction-route safety, or sidecar safety.

## Resources

- [cas-review-backend.md](references/cas-review-backend.md)
- [native-review-driver.md](references/native-review-driver.md)
- [review-result-contract.md](references/review-result-contract.md)
- [adjudication-route-contract.md](references/adjudication-route-contract.md)
- [review-closure-abstraction-ladder.md](references/review-closure-abstraction-ladder.md)
- [cluster-refactor-moratorium.md](references/cluster-refactor-moratorium.md)
- [implementation-handoff.md](references/implementation-handoff.md)
- [pr-sweep-contract.md](references/pr-sweep-contract.md)
- [parallelism-contract.md](references/parallelism-contract.md)
- [validation-policy.md](references/validation-policy.md)
- [durable-run-ledger.md](references/durable-run-ledger.md)
- [final-report-contract.md](references/final-report-contract.md)
