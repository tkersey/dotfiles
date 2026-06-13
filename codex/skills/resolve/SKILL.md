---
name: resolve
description: "Resolve the current branch through a CAS-first, receipt-backed review loop with native review as recorded fallback only. Use for `$resolve`, branch resolution, review/fix/validate/commit/push loops, PR comment sweep, three consecutive clean reviews, CAS review lanes, deterministic base/HEAD pinning, full review-adjudication route consumption, review-compression-compiler integration, clustered counterexample compression, surface-budgeted fixed-point fixes, and final pushed readiness. Do not use for one-shot review, PR creation only, merging/landing, isolated adjudication, or final closure proof without branch mutation."
---

# resolve

## Purpose

Resolve the current branch to a pinned-review-clean, validated, committed, pushed, and PR-comment-swept state without unbounded code accumulation.

`$resolve` is a root-owned branch-resolution state machine. It does not merely review the branch, and it does not treat review comments as work items. It keeps reviewing, adjudicating, compressing review counterexamples into normal forms, fixing only when warranted, validating, committing, pushing, and sweeping PR comments until the branch reaches the completion bar or a precise blocker stops the run.

## Core doctrine

```text
Review findings are counterexamples, not tasks.
Review resolution is a compression problem, not a fix queue.
```

`$resolve` must not implement a review finding directly. It may only:

1. consume `$review-adjudication`;
2. lift mutation-capable findings into route evidence;
3. invoke `$review-compression-compiler` when cluster/surface triggers fire;
4. pass the selected normal form to `$fixed-point-driver`;
5. delegate single-writer implementation only after a proof-carrying normal form exists.

## Activation Kernel

Use `$resolve` when the user wants the current branch driven to completion through review/fix/validate/push and PR-sweep closure.

Do not use `$resolve` when:

- the user wants a one-shot review only;
- the user wants PR creation or proof publication only; use `$ship`;
- the user wants merge, checks-watch, branch cleanup, or final PR landing; use `$land`;
- the user wants adjudication only; use `$review-adjudication`;
- the user wants final readiness/closure proof only; use `$verification-closure`;
- the user wants implementation of a known warrant only; use `$fixed-point-driver` / `$accretive-implementer`.

Default mode: **full branch resolution, CAS-first**.

Mutation authority: root-owned only. Specialist workers and sidecars may gather evidence but must not mutate, stage, commit, push, resolve threads, own the review streak, close compiler packets, or declare completion.

Completion bar:

```text
3 consecutive clean reviews
+ pinned backend/base/head/fingerprint
+ full validation pass
+ intended commit/push
+ complete post-push PR sweep
+ no unprocessed in-scope PR comments
+ no actionable PR comments remaining
+ no missing mutation-capable route receipts
+ no open review compression packet
+ no unpaid abstraction rent
```

## Entry guard

Before any review command runs, prove this run has loaded enough of this skill to include:

- `## Backend selection`
- `## Review adjudication route consumption`
- `## Review Compression Compiler integration`
- `## Fixed-point and implementation handoff`
- `## Non-negotiables`

A partial read of only the top of this file is not enough to operate `$resolve`.

Record one of these facts before the first review attempt:

- CAS preflight/review was attempted through the review driver and produced a receipt or concrete failure.
- The user explicitly requested native review for the current run.

The following facts are not native fallback conditions:

- hosted PR has no actionable threads;
- hosted PR has no checks or empty rollup;
- hosted PR only has a Codex usage-limit notice;
- local de novo review would be useful;
- `gh pr view` reports clean merge state.

If native review already ran before CAS preflight/fallback was recorded, treat it as invalid for `$resolve` streak accounting. Adjudicate any real issue on its merits, then restart the CAS-first loop.

## Completion criteria

Do not consider the branch resolved until all are true:

1. selected review backend produced three consecutive clean review runs through the review driver;
2. clean review means no findings/comments/requested changes/unresolved output;
3. any review with findings/comments resets the streak, even when later adjudicated no-change;
4. base ref, base SHA, backend class, target fingerprint when available, and `HEAD` SHA are pinned for the streak;
5. full validation passes after the third clean review;
6. any code/config/dependency/lockfile/generated/test/behavior-doc change resets review streak;
7. commit/push happens only after final review streak and validation;
8. post-push PR sweep is complete;
9. every in-scope review/PR item is consumed through `$review-adjudication`;
10. every mutation-capable item has structured route evidence;
11. every hot cluster or add-surface route has an accepted `review_compression_packet`;
12. every selected normal form routes through `$fixed-point-driver`;
13. any PR-driven change restarts review/validation/commit/push/sweep;
14. no unpaid abstraction rent remains.

## State to maintain

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
  route_receipt_ledger: []
  review_compression_ledger: []
  implementation_handoff_ledger: []
  validation_commands: []
  pr_comment_ledger: {}
  pr_sweep_inventory_status: unknown
  language_skill_packet: {}
  parallel_task_ledger: []
  durable_run_dir: null
```

Reset `clean_review_streak = 0` whenever review returns comments, `HEAD` changes, backend/base/fingerprint changes, fixed-point/implementation changes branch state, validation changes files, or PR handling changes branch state.

## Durable run ledger

For long or mutating runs, maintain a local non-committed ledger:

```text
~/.codex/resolve/runs/<repo-name>/<timestamp-or-branch>/
  resolve-state.json
  review-*.json
  adjudication-ledger.jsonl
  route-receipt-ledger.jsonl
  review-compression-ledger.jsonl
  implementation-handoff-ledger.jsonl
  pr-comment-ledger.jsonl
  validation-ledger.jsonl
  parallel-task-ledger.jsonl
```

Do not commit this ledger.

## Language/tool routing

Before first review and whenever changed file set materially changes, inspect repo/diff for language/tool signals. Load applicable language/tool skills before selecting proof commands or review context. `$resolve` owns routing, not language proof mechanics.

For Zig projects, route to `$zig`; `$zig` owns Zig cache/version/proof-lane details. `$resolve` must not hardcode Zig-specific proof environment details except by quoting loaded `$zig` guidance.

## Backend selection

`$resolve` is CAS-first.

Attempt CAS lane preflight before native review. Native Codex review is fallback-only when:

- CAS preflight fails or installed CAS surface is incompatible;
- CAS lane startup/status/review/timeout recovery/receipt normalization fails;
- CAS reports blocking transport/runtime failure and native fallback is available;
- user explicitly requests native review for the current run.

Do not choose native review because it is easier, faster, or historically common.

See `references/cas-review-backend.md` and `references/native-review-driver.md`.

## Review result normalization

Every backend normalizes to `review_result`:

```yaml
review_result:
  clean: true|false
  backend_class: cas-lane | native-cli | cas-native-fallback
  target_fingerprint: string|null
  tool_completed: true|false
  base_ref:
  base_sha:
  head_sha:
  invocation:
  sandbox_mode:
  raw_output_ref:
  findings: []
```

Clean requires successful tool completion, reliable parse, zero substantive findings/comments/notes, and matching pinned backend/base/head/fingerprint.

See `references/review-result-contract.md`.

## Review loop

Repeat until `clean_review_streak == 3`:

1. Invoke selected review driver.
2. If backend cannot produce reliable result, stop blocked.
3. If review returns zero findings/comments:
   - establish/verify streak pins;
   - increment streak;
   - run another review if streak < 3.
4. If review returns findings/comments:
   - reset streak;
   - update review item ledger;
   - invoke `$review-adjudication` for every in-scope item;
   - record structured route evidence for mutation-capable items;
   - invoke `$review-compression-compiler` when trigger conditions fire;
   - route accepted normal forms through `$fixed-point-driver`;
   - run targeted validation after changes;
   - restart review loop.
5. If all items are no-change/do-not-address/resolve-thread-only, continue review loop anyway; the commented run is not clean.

Do not use arbitrary max iterations. Stop only for explicit blockers.

## Review adjudication route consumption

Do not collapse routes to only `address` / `do-not-address`.

For each review/PR item provide:

- exact text;
- source;
- provider ID/URL/author/timestamp when available;
- file/line when available;
- relevant code/diff context;
- selected base SHA and current `HEAD`;
- conventions/tests/CI/language guidance;
- current cluster/compression context.

Route handling:

| adjudication route | resolve handling |
|---|---|
| `address` / `mutate-code` | route evidence -> compiler if triggered -> fixed-point |
| `delete-collapse-canonicalize` / `mutate-code` | compiler/fixed-point with ablation preferred |
| `validate-only` | add/run proof only; reset streak if files change |
| `resolve-thread-only` | resolve/reply only if provider policy permits |
| `do-not-address` | record rationale; review still not clean |
| `blocked` | stop before commit/push |

See `references/adjudication-route-contract.md`.

## Structured route receipt

Every mutation-capable review item needs:

```yaml
resolve_route_receipt:
  receipt_version: RR-v1
  review_item_id: "..."
  artifact_state_id: "..."
  adjudication_route: "..."
  mutation_capable: yes
  compression_required: yes | no
  compression_trigger:
    reason: second_same_cluster_finding | adjacent_review_after_fix | surface_growth | add_surface_request | repeated_address_route | same_cluster_reappeared | not-triggered
  bypass_reason: "isolated existing-owner no-new-surface direct proof" # only when compression_required=no
  selected_route: no-change | validate-only | delete-collapse-canonicalize | refactor-existing-owner | mutate-existing-owner | add-new-surface | blocked
  proof_required: []
```

Prose is not a receipt. Missing receipt blocks mutation and completion.

## Review Compression Compiler integration

Invoke `$review-compression-compiler` when any trigger is true:

- `same_cluster_findings >= 2`;
- same cluster reappears after selected normal form;
- route would add production surface;
- route would add helper/wrapper/adapter/fallback/flag/branch/state variant/public symbol/compatibility path;
- review/validation/PR findings are repeatedly selected as `address`;
- surface delta would be `larger-with-warrant` or `larger-without-warrant`;
- fixed-point needs cluster normal form rather than a single comment.

The compiler consumes counterexamples and emits `review_compression_packet`.

`$resolve` must consume:

```yaml
review_compression_packet.selected_normal_form
review_compression_packet.implementation_handoff
review_compression_packet.proof_matrix
review_compression_packet.closure_rule
```

If the packet is `blocked`, stop before mutation.

If packet selects `add-new-surface` with unpaid rent, stop before mutation.

If same cluster reappears after implementation, follow `closure_rule`: reopen compiler, block, or escalate. Do not patch locally again.

See `references/review-compression-compiler-integration.md`.

## Fixed-point and implementation handoff

When invoking `$fixed-point-driver`, pass:

- review/PR item;
- adjudication route/warrant;
- route receipt;
- review compression packet when present;
- selected normal form;
- permitted scope;
- forbidden actions;
- surface budget;
- ablation status;
- proof matrix;
- stale conditions.

Minimum shape:

```yaml
implementation_handoff:
  source_skill: resolve
  target_skill: fixed-point-driver
  artifact_state_id: "..."
  review_item_id: "..."
  review_compression_packet_id: "..."
  selected_normal_form:
    kind: no-change-proof | validate-only | delete-collapse-canonicalize | refactor-existing-owner | mutate-existing-owner | add-new-surface | blocked
    owner: "..."
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
  abstraction_rent_status: paid | unpaid | not-applicable
  proof_required: []
  stale_if: []
```

Do not simply say "fix minimally."

See `references/implementation-handoff.md`.

## Surface delta reporting

For any run that changes files, record:

```yaml
surface_delta_summary:
  production_insertions:
  production_deletions:
  production_net:
  test_insertions:
  test_deletions:
  test_net:
  generated_insertions:
  generated_deletions:
  generated_net:
  helpers_wrappers_adapters_added:
  public_symbols_added:
  flags_fallbacks_compat_paths_added:
  duplicate_or_shadow_surfaces_retired:
  surface_delta_call: smaller | same | larger-with-warrant | larger-without-warrant | unknown
```

`larger-without-warrant` blocks resolved completion unless revised, warranted, or explicitly accepted by the user.

## Validation

After three clean reviews, run full project validation. If validation fails, route failure through adjudication when contested, compiler when clustered/surface-bearing, then fixed-point. Reset review streak after any file change.

If no validation command exists, do not treat validation as passed. Block or require explicit user acceptance of manual-only proof.

See `references/validation-policy.md`.

## Commit and push

Only after final review streak and validation:

1. inspect status/diff;
2. stage only intended changes;
3. commit intended changes;
4. push branch;
5. record commit SHA, review receipts, route/compression/implementation ledgers, validation, surface delta;
6. run PR sweep.

Do not commit/push with unresolved unrelated changes, failed validation, fewer than three clean reviews, unknown base, parse failure, actionable comments, missing route receipts, blocked compression packets, unpaid rent, or incomplete PR sweep when claiming PR-reviewed completion.

## Post-push PR sweep

After each push, inspect associated PR. Prefer complete paginated review-thread inventory.

Every in-scope PR item goes through the same adjudication -> route receipt -> compiler when triggered -> fixed-point flow.

If PR handling changes branch state, restart review/validation/commit/push/sweep.

See `references/pr-sweep-contract.md`.

## Final report

When complete or blocked, report:

```text
Resolve:
- status:
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

Adjudication:
- review_items:
- pr_items:

Review compression:
- route_receipts: structured=N, missing=N
- compiler_packets: accepted=N, blocked=N, not_required=N
- clusters_compiled:
- selected_normal_forms:
- abstraction_rent: paid=N, unpaid=N, not_applicable=N

Surface delta:
- production_insertions:
- production_deletions:
- production_net:
- test_insertions:
- test_deletions:
- test_net:
- duplicate_or_shadow_surfaces_retired:
- surface_delta_call:

Implementation:
- fixed_point_runs:
- implementation_handoffs:
- accretive_implementer_routes:
- surface_delta_calls:

Validation:
- commands_passed:
- commands_blocked_or_not_available:
- validation_mode:

PR sweep:
- inventory_status:
- unresolved_actionable_comments:

Resolve Bottom Line:
- status:
- strongest proof:
- open blocker:
- exact next action:
```

`Resolve Bottom Line` must be final.

## Non-negotiables

- Three consecutive clean reviews from the pinned backend class are required.
- CAS-first; native review is fallback-only.
- Do not collapse adjudication into `address` / `do-not-address`.
- Do not route review findings directly to `apply_patch`.
- Do not mutate without structured route receipt.
- Invoke `$review-compression-compiler` for hot clusters, add-surface pressure, repeated address routes, same-cluster recurrence, or surface growth.
- Do not select `add-new-surface` with unpaid abstraction rent.
- Do not route to `$fixed-point-driver` without selected normal form, surface budget, forbidden actions, and proof requirements.
- Do not count stale review/validation/PR proof.
- Do not claim resolved with incomplete PR sweep, failed validation, unpaid rent, missing receipts, or open compiler blockers.
- Do not stage unrelated work.
- Do not fabricate validation, review outcomes, PR state, commit SHAs, surface delta, or compiler safety.

## Resources

- [review-compression-compiler-integration.md](references/review-compression-compiler-integration.md)
- [adjudication-route-contract.md](references/adjudication-route-contract.md)
- [implementation-handoff.md](references/implementation-handoff.md)
- [surface-delta-reporting.md](references/surface-delta-reporting.md)
- [cas-review-backend.md](references/cas-review-backend.md)
- [native-review-driver.md](references/native-review-driver.md)
- [review-result-contract.md](references/review-result-contract.md)
- [pr-sweep-contract.md](references/pr-sweep-contract.md)
- [validation-policy.md](references/validation-policy.md)
