---
name: ship
description: "Finalize validated work into a proof-backed pull request without merging, and return immutable SHIP-v1 publication evidence to Actuating without taking architecture, review, or closure authority. Use for `$ship`, ship/finalize a branch, prepare/open/update/promote a PR, publish validation proof, choose ready-vs-draft state, update a PR body, or produce PR handoff after proof. Default PR state is ready after full validation; draft PRs require an explicit warrant."
---

# Ship

## Purpose

Finalize deliverables after validation and publish a concise, non-destructive proof trail in a pull request.

`$ship` opens, updates, or promotes a PR. It does not merge.
Within Actuating, `$ship` is the sole public-effect owner. `SHIP-v1` is an
external evidence attachment, not an architecture, review, or closure artifact.

Core rule:

```text
Validated, complete work ships as a ready PR by default.
Draft PR is an exception, not the default.
```

## Activation boundary

Use `$ship` when the user asks to:

- ship/finalize the current branch;
- open a PR;
- update an existing PR body with proof;
- publish validation proof before handoff;
- promote a draft PR to ready after validation;
- create a draft PR explicitly for early visibility.

Do not use `$ship` when:

- implementation is not done and the user did not ask for early visibility;
- validation is failing and the user did not explicitly accept a caveated draft;
- the user wants merge/landing; use `$land`;
- the user wants only a local readiness report and no public PR effect; report readiness and stop. Use `$proof-patch` only when a current complete actuation closure receipt exists;
- the current branch has unrelated or unstaged work that cannot be scoped.

## Inputs

Before acting, establish:

```yaml
ship_input:
  source: direct | actuation
  repository: owner/name
  title:
  branch:
  base_branch:
  base_sha:
  head_sha:
  existing_pr:
    exists: yes | no | unknown
    number:
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
  actuation:
    protocol: artifact-kernel-v1 | legacy-actuating-v1
    actuation_binding:
      actuation_run_id:
      state_fingerprint:
    artifact_kernel:
      closure_receipt:
        schema: actuating-closure-receipt/v1
        receipt_id:
        goal_id:
        goal_contract_ref:
        construction_ref:
        subject_digest:
        evidence_head:
        review_contract_digest:
        verdict: ready-to-ship
        blockers: []
        proof:
          complete: true
          missing_obligations: 0
          missing_retirements: 0
        review:
          auxiliaries_current: false
          clean_streak: 0
          full_wave_complete: false
        publication:
          current: false
    legacy:
      closure_decision_id:
      closure_verdict: ready-to-ship
  user_requested_pr_mode: ready | draft | update-existing | promote-draft | none
  repo_policy_pr_mode: ready | draft | unknown
```

If key state is unknown, inspect the repository and live PR state before creating or updating a PR.

For `source: actuation`, select exactly one protocol. `artifact-kernel-v1`
requires a current deterministic `actuating-closure-receipt/v1` with
`verdict: ready-to-ship`; confirm its subject digest identifies the current
review subject being published. `legacy-actuating-v1` requires the current kernel-derived
`closure-decision/v1` with the same verdict. Ship consumes either receipt as
upstream readiness evidence; it does not rederive closure, inspect the selected
architecture, classify findings, or decide review convergence.

Each `SHIP-v1` is immutable for its publication epoch. Preserve the supplied
`actuation_binding` verbatim as an opaque exact two-field object. For an
Artifact Kernel input, Actuating owns the compatibility projection:

~~~text
actuation_binding.actuation_run_id = closure_receipt.receipt_id
actuation_binding.state_fingerprint = closure_receipt.subject_digest
~~~

Ship SHALL require that exact match against the supplied closure receipt, but
MUST NOT synthesize, relabel, or revise either value. The field names remain a
SHIP-v1 compatibility surface, not Artifact Kernel semantic authority. The
later `publication_observed` Evidence Ledger event binds Ship's owner-issued
receipt reference to the deterministic closure receipt identity, Construction,
and subject after Ship's live readback.

Actuation input cannot use the early-draft path because draft publication has
no valid closure re-entry. If repository policy requires a draft for an
actuation input, block with an incompatible-policy reason rather than
publishing an invalid lifecycle state. A direct ship input does not require the
actuation object.

## PR readiness policy

Default final PR state is `ready`.

Use `draft` only when at least one is true:

- user explicitly requests a draft PR;
- validation is incomplete, partial, blocked, failing, or manually accepted with caveats;
- one or more in-scope tasks are blocked, deferred, or open;
- PR is intentionally being opened for early visibility before readiness;
- required review context is missing and the user asks to publish anyway;
- repository policy explicitly requires draft PRs for this branch/workflow and `source: direct`.

The ordered post-ship review-closeout phase is a goal continuation, not an
incomplete implementation task or a draft warrant.

If the branch is fully validated and no blockers remain, do not create a draft PR by default.

## PR decision

Keep the GitHub operation separate from the desired final state, then project it
to the existing `pr_readiness.mode` field for SHIP-v1 compatibility.

```yaml
pr_decision:
  operation: create | update | update-and-promote | blocked
  final_state: ready | draft | preserve
  compatibility_mode: ready | draft | update-existing | promote-draft | blocked
  reason: "..."
  draft_allowed_reason: "none | explicit-user | incomplete-validation | blocked-tasks | early-visibility | missing-context | repo-policy"
```

Projection:

| Condition | operation | final_state | compatibility_mode |
|---|---|---|---|
| No open PR; fully ready | `create` | `ready` | `ready` |
| No open PR; warranted draft | `create` | `draft` | `draft` |
| Open PR; preserve current draft/ready state | `update` | `preserve` | `update-existing` |
| Open draft; fully ready | `update-and-promote` | `ready` | `promote-draft` |
| Invalid, ambiguous, or unauthorized state | `blocked` | `preserve` | `blocked` |

## Existing PR policy

Before mutation, query live PRs for the exact repository, base branch, and head
branch. Require at most one matching open PR.

- Prefer the matching open PR over creating another PR.
- If a matching open draft is fully validated with no blockers, update its proof body and then promote it unless the user or repository policy explicitly says to preserve draft.
- If a matching open draft still has blockers, preserve draft and update the proof/blocker state.
- If a matching open ready PR is now caveated or blocked, preserve ready state; do not silently convert it to draft.
- A merged PR, a closed unmerged PR, multiple matching open PRs, or a PR with the wrong repository/base/head tuple blocks shipping. Report the exact mismatch instead of guessing, reopening, or creating a duplicate.

## Managed PR body

`$ship` owns only the marker-bounded proof block:

```md
<!-- ship-proof:start -->
...
<!-- ship-proof:end -->
```

For a new PR, the body may consist only of this block. For an existing PR:

1. Read the current body before editing.
2. Replace exactly one complete managed block, or append a new block when neither marker exists.
3. Preserve all text outside the managed block byte-for-byte.
4. Block when only one marker exists, multiple managed blocks exist, or the marker structure is otherwise ambiguous.
5. Never replace the entire existing body with a newly generated proof body unless the existing body is empty.

## Command policy

Use GitHub CLI where applicable.

Ready PR creation:

```bash
gh pr create --title "<title>" --body-file <body-file> --base <base> --head <branch>
```

Draft PR creation only when `pr_decision.final_state: draft`:

```bash
gh pr create --draft --title "<title>" --body-file <body-file> --base <base> --head <branch>
```

Existing PR update:

```bash
gh pr view <pr> --json body | jq -j .body > <current-body-file>
# Replace or append only the managed proof block into <merged-body-file>.
gh pr edit <pr> --body-file <merged-body-file>
```

Existing draft promotion must update proof first:

```bash
gh pr edit <pr> --body-file <merged-body-file>
gh pr ready <pr>
```

After every create, update, or promotion, read back live state:

```bash
gh pr view <pr> \
  --json number,url,state,isDraft,baseRefName,baseRefOid,headRefName,headRefOid,body
```

Do not pass `--draft` unless the decision has a non-`none`
`draft_allowed_reason`. Do not report `created`, `updated`, or `promoted` until
the readback postconditions pass.

## Publication postconditions

The live readback must prove:

- PR state is open;
- repository and URL identify the intended PR;
- `baseRefName` and `baseRefOid` match `base_branch` and `base_sha`;
- `headRefName` and `headRefOid` match `branch` and `head_sha`;
- `isDraft` matches `final_state`, or matches the preflight value when `final_state: preserve`;
- the body contains exactly one managed block whose contents match the generated proof block;
- an update-and-promote operation completed the body update before the draft-to-ready transition.

If a command succeeds but readback fails, do not emit a successful action result.
Report the completed side effect, the failed postcondition, and the exact repair
or retry step. Re-read live state before retrying; never assume the earlier
preflight remains current.

## Workflow

1. Confirm repository, current branch, base branch and SHA, head SHA, and remote.
2. Inspect worktree status and ensure the intended head is committed and available on the remote branch.
3. Inspect live PRs for the exact repository/base/head tuple and reject ambiguous or mismatched state.
4. Confirm recent validation exists for the current change set; if not, run or request validation.
5. For actuation input, require the current protocol-specific readiness receipt,
   confirm its subject digest identifies the review subject being published,
   and preserve the supplied opaque two-field actuation binding.
6. Determine `pr_decision`, including operation, final state, and compatibility mode.
7. Build the managed proof block with proof, scope, risks, follow-ups, readiness, and caveats.
8. Create or merge the managed block into the PR body without overwriting human-authored text.
9. Execute the ordered operation: create; update; or update, then promote.
10. Read back live PR metadata and body and require every publication postcondition.
11. Emit `SHIP-v1` and report PR state. For `artifact-kernel-v1`, hand the
    complete immutable receipt back to `$actuating`, which records the current
    `publication_observed` event with the Ship receipt reference and closure
    receipt identity. Ship must
    not append that event or reinterpret the receipt as architecture, review,
    or closure evidence. For
    `legacy-actuating-v1`, preserve the existing implementation-checkpoint and
    `review.ship_receipt` handback. A proved review edit returns here before
    further review; update the existing PR at the exact retained URL and emit a
    fresh immutable `SHIP-v1`. Creating another PR is invalid for this handback.

## PR body contract

Keep proof concise, scoped, and free of credentials, tokens, private paths, or
sensitive command arguments.

Include this managed block:

```md
<!-- ship-proof:start -->
## Summary
- What changed and why.

## Proof
- `<command>`: pass/fail/blocked/not-run
- `<command>`: pass/fail/blocked/not-run

## Scope
- repository:
- branch:
- head:
- base:
- base SHA:

## Risks
- None identified, or concise residual risks.

## Follow-ups
- None, or explicitly deferred work.

## Readiness
- Operation: create | update | update-and-promote | blocked
- Final state: ready | draft | preserve
- SHIP-v1 compatibility mode: ready | draft | update-existing | promote-draft | blocked
- Reason:
- Caveats:
<!-- ship-proof:end -->
```

Do not overclaim validation. If a category was missing or not run, say so. Use
`None` only after checking the relevant section; do not omit risks or follow-ups
merely because they are empty.

## Ship record

Emit:

```yaml
ship_record:
  record_version: SHIP-v1
  source: direct | actuation
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
  actuation_binding:
    actuation_run_id: "..."
    state_fingerprint: "..."
```

`pr_readiness.mode` is the compatibility projection of `pr_decision`; do not use
it as the sole description of both operation and final state. `action.command`
may contain the ordered mutation and readback commands. A successful
`action.result` means the live publication postconditions passed, not merely
that the mutation command exited zero.

`actuation_binding` is required for every actuation ready/update/promote record
and omitted for direct records. Preserve its exact two fields verbatim and
opaque. Missing, extra, relabeled, or mismatched binding blocks actuation
shipping. For `artifact-kernel-v1`, require the upstream Actuating projection
`receipt_id -> actuation_run_id` and `subject_digest -> state_fingerprint`;
Ship validates and copies that pair but never derives it. The record is never
rewritten with later resolution or review values.

For `artifact-kernel-v1`, return the complete immutable receipt to
`$actuating`; the current `publication_observed` event binds its owner-issued
reference to the closure receipt identity. For `legacy-actuating-v1`, preserve the
existing implementation-checkpoint and `review.ship_receipt` behavior. A later
repair handback updates the same PR URL and creates a fresh `SHIP-v1`.

After publication, closure must independently query live PR metadata and match
the repository, base ref and SHA, head ref and SHA, URL, open state, and ready
status; copied SHIP fields are not authoritative for those facts.

## Guardrails

- Never ship without a validation signal or an explicitly reported validation limitation.
- Never create a draft PR by default after full validation.
- Never pass `--draft` without a `draft_allowed_reason`.
- Never create a duplicate PR when an open exact-tuple PR exists.
- Never overwrite human-authored PR body content outside the managed proof block.
- Never promote a draft before updating its current proof block.
- Never claim publication success without a matching live readback.
- Never select or revise architecture, classify findings, count review credit,
  append `publication_observed`, or decide closure.
- Never merge or land.
- Never stage or commit unrelated work.
- If PR creation/update is blocked by auth, remote, permissions, missing branch push, malformed body markers, or mismatched live state, state the exact blocker and next command.

## Output

End with:

```text
Ship Bottom Line:
- branch:
- head:
- validation:
- operation:
- final PR state:
- PR:
- readback:
- proof:
- blocker / next step:
```

## Resources

- [pr-readiness-policy.md](references/pr-readiness-policy.md)
- [ship-record.md](references/ship-record.md)
- [pr-body-proof.md](references/pr-body-proof.md)
