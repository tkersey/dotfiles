---
name: ship
description: "Finalize validated work into a proof-backed pull request without merging. Use for `$ship`, ship/finalize a branch, prepare/open/update/promote a PR, publish validation proof, choose ready-vs-draft PR state, update an existing PR body, or produce PR handoff after proof. Default PR state is ready after full validation; draft PRs require an explicit warrant."
---

# Ship

## Purpose

Finalize deliverables after validation and publish a concise proof trail in a pull request.

`$ship` opens, updates, or promotes a PR. It does not merge.

Core rule:

```text
Validated, complete work ships as a ready PR by default.
Draft PR is an exception, not the default.
```

## Activation boundary

Use `$ship` when the user asks to:

- ship/finalize current branch;
- open a PR;
- update an existing PR body with proof;
- publish validation proof before handoff;
- promote a draft PR to ready after validation;
- create a draft PR explicitly for early visibility.

Do not use `$ship` when:

- implementation is not done and the user did not ask for early visibility;
- validation is failing and the user did not explicitly accept a caveated draft;
- the user wants merge/landing; use `$land`;
- the user only wants readiness proof; use `$verification-closure`;
- the current branch has unrelated or unstaged work that cannot be scoped.

## Inputs

Before acting, establish:

```yaml
ship_input:
  branch:
  base_branch:
  head_sha:
  existing_pr:
    exists: yes | no | unknown
    url:
    state: open | closed | merged | unknown
    draft: yes | no | unknown
  validation:
    build: pass | fail | missing | not-run
    lint: pass | fail | missing | not-run
    tests: pass | fail | missing | not-run
    language_specific: pass | fail | missing | not-run
    acceptance: pass | fail | missing | not-run
  task_state:
    complete:
    blocked:
    deferred:
    open:
  proof_summary:
  user_requested_pr_mode: ready | draft | update-existing | promote-draft | none
  repo_policy_pr_mode: ready | draft | unknown
```

If key state is unknown, inspect the repository and PR state before creating or updating a PR.

## PR Readiness Policy

Default PR mode is `ready`.

Use `draft` only when at least one is true:

- user explicitly requests a draft PR;
- validation is incomplete, partial, blocked, failing, or manually accepted with caveats;
- one or more in-scope tasks are blocked, deferred, or open;
- PR is intentionally being opened for early visibility before readiness;
- required review context is missing and the user asks to publish anyway;
- repo policy explicitly requires draft PRs for this branch/workflow.

If the branch is fully validated and no blockers remain, do not create a draft PR by default.

```yaml
pr_readiness:
  mode: ready | draft | update-existing | promote-draft | blocked
  reason: "..."
  draft_allowed_reason: "none | explicit-user | incomplete-validation | blocked-tasks | early-visibility | missing-context | repo-policy"
```

## Existing PR policy

If an open PR already exists for the branch:

```text
update-existing
```

is preferred over creating a new PR.

If the existing PR is draft and the branch is fully validated with no blockers:

```text
promote-draft
```

is the default unless the user or repo policy explicitly says to preserve draft.

If the existing PR is draft and blockers remain, preserve draft and update the body with the current proof/blocker state.

If the existing PR is ready and validation is now caveated or blocked, do not silently convert it to draft. Report the blocker and ask for explicit direction if a state change is needed.

## Command policy

Use GitHub CLI where applicable.

Ready PR:

```bash
gh pr create --title "<title>" --body-file <body-file> --base <base> --head <branch>
```

Draft PR only when `pr_readiness.mode: draft`:

```bash
gh pr create --draft --title "<title>" --body-file <body-file> --base <base> --head <branch>
```

Promote existing draft only when `pr_readiness.mode: promote-draft`:

```bash
gh pr ready <pr>
```

Update existing PR body:

```bash
gh pr edit <pr> --body-file <body-file>
```

Do not pass `--draft` unless the readiness record says `mode: draft`.

## Workflow

1. Confirm current branch, base branch, head SHA, and repository remote.
2. Inspect worktree status.
3. Confirm recent validation signal exists for the current change set; if not, run or request validation.
4. Determine PR mode using the readiness policy.
5. Summarize proof: commands/signals and outcomes.
6. Build PR body with proof, scope, risks, and remaining follow-ups.
7. Open/update/promote PR according to `pr_readiness.mode`.
8. Report PR URL/status and any remaining follow-ups.

## PR body contract

Keep proof concise and scoped.

Include:

```md
## Summary
- ...

## Proof
- `<command>`: pass/fail/blocked
- `<command>`: pass/fail/blocked

## Scope
- branch:
- head:
- base:

## Readiness
- PR mode: ready | draft | update-existing | promote-draft | blocked
- Reason:
- Caveats:
```

Do not overclaim validation. If a category was missing or not run, say so.

## Ship record

Emit:

```yaml
ship_record:
  record_version: SHIP-v1
  branch: "..."
  base_branch: "..."
  head_sha: "..."
  existing_pr:
    exists: yes | no | unknown
    url: "..."
    draft: yes | no | unknown
  validation:
    build: pass | fail | missing | not-run
    lint: pass | fail | missing | not-run
    tests: pass | fail | missing | not-run
    language_specific: pass | fail | missing | not-run
    acceptance: pass | fail | missing | not-run
  pr_readiness:
    mode: ready | draft | update-existing | promote-draft | blocked
    reason: "..."
    draft_allowed_reason: "none | explicit-user | incomplete-validation | blocked-tasks | early-visibility | missing-context | repo-policy"
  action:
    command: "..."
    result: created | updated | promoted | blocked | skipped
    pr_url: "..."
```

## Guardrails

- Never ship without a validation signal or an explicitly reported validation limitation.
- Never create a draft PR by default after full validation.
- Never pass `--draft` without a `draft_allowed_reason`.
- Never create a duplicate PR when an open branch PR exists.
- Never merge or land.
- Never stage or commit unrelated work.
- If PR creation/update is blocked by auth, remote, permissions, or missing branch push, state the exact blocker and next command.

## Output

End with:

```text
Ship Bottom Line:
- branch:
- head:
- validation:
- PR mode:
- PR:
- proof:
- blocker / next step:
```

## Resources

- [pr-readiness-policy.md](references/pr-readiness-policy.md)
- [ship-record.md](references/ship-record.md)
- [pr-body-proof.md](references/pr-body-proof.md)
