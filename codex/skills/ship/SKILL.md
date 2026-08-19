---
name: ship
description: "Finalize validated work into proof-backed public state without merging, and return immutable Ship-owned publication evidence without taking architecture, review, or closure authority. Use for $ship, opening or updating a PR, promoting a draft, or read-only observing and adopting an exact already-public subject through an Actuating handoff."
---

# Ship

## Purpose

Publish validated work through a concise, non-destructive proof trail. `$ship`
may create, update, or promote a pull request, or read-only observe and adopt an
exact already-public default-branch subject that no current PR tuple can
truthfully represent. It never merges.

Ship is the sole public-effect and publication-evidence owner. Actuating
supplies current Git and validation facts; Ship does not require an Actuating
closure receipt, Construction reference, Evidence head, or Ledger event.

```text
validated complete work -> ready PR
incomplete work with explicit warrant -> draft PR
```

## Activation

Use Ship when the user asks to create, update, finalize, or promote a PR, or
when Actuating supplies a current publication handoff.

Only an explicit Actuating handoff may select `observe-existing` or
`adopt-existing`. Direct Ship requests use the pull-request route.

Do not use Ship when the user wants merge/landing, implementation is incomplete
without an accepted draft reason, validation failure lacks an accepted caveat,
or no publication/readback was requested.

## Input

```yaml
ship_input:
  source: direct | actuation
  publication_route: pull-request | observe-existing | adopt-existing
  repository:
  base:
    branch:
    sha:
  head:
    branch:
    sha:
  existing_pr:
    exists:
    url:
    draft:
  existing_publication:
    branch:
    head_sha:
    comparison_base_sha:
    publication_observation_ref: null | sha256-digest
    release: null | { provider, repository, publication_state, draft, tag, url, target_sha, assets: [] }
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
    goal_context_digest:
    review_contract_digest:
    review_context_digest: null | sha256-digest
    publication_required: true | false
  user_requested_pr_mode: ready | draft | update-existing | promote-draft | none
  repo_policy_pr_mode: ready | draft | unknown
```

Direct shipping omits `actuation`. For Actuating input, exact repository,
base/head, validation, task state, and Goal context are mandatory. Ship copies
the Actuating binding into its receipt but never interprets it as architecture,
review, mutation, or closure authority.

## Pull-request route

Keep operation and final state separate:

```yaml
pr_decision:
  operation: create | update | update-and-promote | blocked
  final_state: ready | draft | preserve
```

Default to `ready` when validation is complete and no task remains blocked,
deferred, or open. Draft requires explicit user intent, incomplete or
accepted-caveat validation, open work, or repository policy.

For an existing exact repository/base/head PR, update rather than duplicate it.
Preserve its ready/draft state unless current authority permits a transition.
Promotion is `update-and-promote`: update proof first, then mark ready.

Read [pr-readiness-policy.md](references/pr-readiness-policy.md).

## Managed body

Only replace content between:

```text
<!-- ship-proof:start -->
<!-- ship-proof:end -->
```

Preserve human-authored content outside the markers byte-for-byte. Duplicated,
nested, reversed, or unbalanced markers block mutation.

Read [pr-body-proof.md](references/pr-body-proof.md).

## Public mutation and readback

Before any PR effect:

1. Verify repository, remote, base/head branches and SHAs, worktree scope, task
   state, and validation.
2. Inspect live PRs for the exact repository/base/head tuple.
3. Determine `pr_decision` and build the complete managed proof block.
4. Push the exact intended committed head when required.
5. Create, update, or update then promote.
6. Read back repository, base/head refs and SHAs, URL, open/draft state, and the
   managed proof block.

A zero exit status is not publication proof. If mutation succeeds but readback
fails, report the partial public effect and block; re-read live state before
retrying.

Return immutable `SHIP-v1` for the exact publication epoch.

## Existing-publication observation

`observe-existing` is Actuating-only and read-only.

Require:

- the supplied head ref is the provider's current default branch;
- the supplied head SHA equals the live default-branch tip;
- base and head differ and base is an ancestor;
- base and head refs normalize to the same default-branch ref;
- no open exact repository/base/head PR exists;
- release input is null.

Return immutable `SHIP-OBSERVATION-v2` with:

```text
repository
canonical default-branch ref
base SHA
head SHA
provider readback
goal context digest
review contract digest
observed time
mutation_performed = false
```

Actuating computes the receipt digest and includes it in the review context and
every CAS request fingerprint before dispatch. The echoed CAS workflow binding
therefore proves that this exact observation existed before review.

No Actuating event ordering or wall-clock comparison is needed.

## Existing-publication adoption

`adopt-existing` is Actuating-only and read-only.

Require a non-null `publication_observation_ref` resolving to the exact
`SHIP-OBSERVATION-v2` used in the current review context. Exact-match:

- repository and canonical default-branch ref;
- immutable base and reviewed head;
- Goal context digest and Review Contract digest;
- current provider branch readback;
- CAS review-context binding supplied by Actuating.

If the exact observation was not bound before the current review, do not adopt a
historical campaign. Obtain a fresh observation and run a fresh review wave.

For an optional release, require current provider state `published`,
`draft: false`, tag target equal to the adopted head, unique asset names, equal
cardinality and exact set equality with the live inventory, and exact asset
name, size, and SHA-256 digest matches.

Return immutable `SHIP-ADOPTION-v2`. It ratifies current public state; it does
not manufacture publication history or decide Actuating closure.

## Receipts

Read [ship-record.md](references/ship-record.md).

For Actuating routes, return the complete canonical receipt bytes and SHA-256
digest. Actuating compares the owner-issued receipt directly with the current
Git and review context. It does not copy the receipt into a workflow event log.

## Guardrails

- Never publish without validation evidence or an explicit reported limitation.
- Never create a draft by default after complete validation.
- Never create a duplicate exact-tuple PR.
- Never use adoption to disguise mutation or avoid fresh review.
- Never overwrite human-authored body content outside the managed block.
- Never promote before updating proof.
- Never claim publication without matching live readback.
- Never require or synthesize an Actuating closure receipt.
- Never select architecture, classify findings, count review credit, decide
  closure, or choose Actuating's next action.
- Never merge or land.
- Never stage or commit unrelated work.

## Output

```text
Ship Bottom Line:
- Operation:
- Final state:
- PR:
- Head:
- Validation:
- Publication readback:
- Ship receipt:
- Next owner:
```
