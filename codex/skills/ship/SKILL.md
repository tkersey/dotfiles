---
name: ship
description: "Finalize validated work into proof-backed public state without merging, and return immutable Ship-owned publication evidence to Actuating without taking architecture, review, or closure authority. Use for $ship, opening or updating a PR, promoting a draft, adopting an exact already-public subject, publishing validation proof, or producing a publication handoff."
---

# Ship

## Purpose

Publish validated work through a concise, non-destructive proof trail. `$ship`
may create, update, or promote a pull request, or read-only adopt an exact
already-public subject that cannot truthfully be represented by a current PR
tuple. It never merges.

Within Actuating, Ship remains the sole publication-evidence owner and the sole
public-effect owner. `SHIP-v1`, `SHIP-OBSERVATION-v1`, and
`SHIP-ADOPTION-v1` are external publication evidence, not a Goal,
Counterexample, Construction, Evidence event, review decision, or closure
artifact.

~~~text
Validated complete work -> ready PR
Incomplete work with an explicit warrant -> draft PR
~~~

## Activation

Use Ship when the user asks to create, update, finalize, or promote a PR, or
when Actuating supplies a current `ready-to-ship` handoff. The Actuating handoff
may select `adopt-existing` only when the exact subject is already public and a
current PR cannot truthfully represent that publication epoch.

Do not use Ship when implementation is incomplete without explicit early-
visibility intent, validation failure lacks an accepted draft warrant, the user
wants merge/landing, or neither publication nor publication readback was
requested.

## Inputs

~~~yaml
ship_input:
  source: direct | actuation
  publication_route: pull-request | observe-existing | adopt-existing
  repository: owner/name
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
    comparison_base_ref:
    comparison_base_sha:
    observation_ref: null | sha256-digest
    release: null | { provider, repository, publication_state, draft, tag, url, target_sha, assets: [{ name, size, sha256 }] }
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
    closure_receipt:
      schema: actuating-closure-receipt/v1
      receipt_id:
      goal_contract_ref:
      construction_ref:
      subject_digest:
      evidence_head:
      review_contract_digest:
      closure_route: final-closeout
      verdict: ready-to-ship
      cited_premise_refs: []
      blockers: []
    actuation_binding:
      closure_receipt_ref:
      goal_contract_ref:
      construction_ref:
      subject_digest:
      evidence_head:
      review_contract_digest:
      closure_route: final-closeout
  user_requested_pr_mode: ready | draft | update-existing | promote-draft | none
  repo_policy_pr_mode: ready | draft | unknown
~~~

For compatibility, an existing input that omits `publication_route` selects
`pull-request` only when no `existing_publication` field or other
adoption-specific field is present. Otherwise omission blocks before any public
effect. Only an explicit Actuating handoff may select `observe-existing` or
`adopt-existing`. For either existing-publication route, the top-level
`repository`, `base`, and `head` tuple is authoritative. Require
`existing_publication.branch == head.branch`,
`existing_publication.head_sha == head.sha`,
`existing_publication.comparison_base_ref == base.branch`, and
`existing_publication.comparison_base_sha == base.sha`; any disagreement blocks
before readback or receipt construction.

Direct shipping omits `actuation`. For Actuating input, require the current
owner-supplied readiness receipt, exact published subject, and
`closure_route: final-closeout`. Reject `local-implementation` receipts: that
route has no public-effect premise. Ship does not rederive closure, inspect or
revise the Construction, classify findings, count review credit, or choose
Actuating's next action.

`observe-existing` and `adopt-existing` are Actuating-only and read-only.
Require the remote branch to
resolve to the supplied head SHA, require the comparison base ref to resolve
exactly to the supplied base SHA, reject an equal base and head, and prove that
base is an ancestor of the head. Query the complete live open-PR inventory for
the exact repository/base/head tuple; adoption requires zero exact matches.
Bind the latest provider-authored branch publication event for that repository
and canonical head ref. Its repository, canonical head ref, and head SHA must
exactly equal the adoption repository, head ref, and head SHA. Its `before_sha`
records the provider's preceding remote tip and is not the review base.
Provider history from that event through observation must be complete
and contain no later event for the same repository and ref, so the event begins
the current uninterrupted publication epoch. `observe-existing` requires
`existing_publication.release == null`; final adoption performs all optional
release validation. For a non-null adopted release, require its provider to
equal the branch publication event's provider, require its repository to
exact-match the adopted repository, require provider state `published` and
`draft: false`, resolve its tag target and require it to equal the adopted head,
obtain the complete live provider asset inventory, require exact set equality
with the receipt, and then verify every asset name, size, and SHA-256 digest.
Reject missing or truncated history, an incomplete PR or asset inventory, an
empty or mismatched tuple, an unpublished or draft release, an unverified asset,
or any requested mutation. The receipt records live provider timestamps; it
must not invent an earlier publication time.

Before a review campaign that may later use `adopt-existing`, Ship performs the
same branch, comparison-base, PR-absence, and publication-epoch readback through
`observe-existing` and returns immutable `SHIP-OBSERVATION-v1`. Actuating must
record that receipt before binding or dispatching the campaign. A later
`SHIP-ADOPTION-v1` may retain the campaign only by carrying the observation
digest and exact-matching its repository, base/head tuple, current publication
epoch, subject, Goal, Construction, and review contract. Ledger event order
between the recorded observation and campaign establishes causality; provider
and Ledger wall-clock timestamps are never compared. The later adoption keeps
its own complete current actuation binding; review events are not required to
leave the earlier readiness receipt current.

Before publication, canonicalize the complete `closure_receipt` with only
`receipt_id` replaced by JSON `null`, recompute its SHA-256 identity, and require
exact equality with `receipt_id`. Missing or extra receipt fields, including
`cited_premise_refs` or `blockers`, block; Ship must not validate a truncated
projection of the receipt.

Actuating supplies this exact publication binding:

~~~text
actuation_binding.closure_receipt_ref = closure_receipt.receipt_id
actuation_binding.goal_contract_ref = closure_receipt.goal_contract_ref
actuation_binding.construction_ref = closure_receipt.construction_ref
actuation_binding.subject_digest = closure_receipt.subject_digest
actuation_binding.evidence_head = closure_receipt.evidence_head
actuation_binding.review_contract_digest = closure_receipt.review_contract_digest
actuation_binding.closure_route = closure_receipt.closure_route
closure_receipt.closure_route = final-closeout
~~~

Ship validates and copies every actuation binding field verbatim. It never
synthesizes, relabels, or revises them.

## PR decision

This section applies only to `publication_route: pull-request`.

Keep operation and final state separate:

~~~yaml
pr_decision:
  operation: create | update | update-and-promote | blocked
  final_state: ready | draft | preserve
~~~

Default to `ready` when validation is complete and no task remains blocked,
deferred, or open. Draft requires explicit user intent, incomplete or accepted-
caveat validation, an open task, or repository policy. Actuating input cannot
take the early-draft route because draft publication has no lawful closure
re-entry; conflicting repository policy blocks.

For an existing exact repository/base/head PR, update rather than duplicate it.
Preserve its current ready/draft state unless explicit policy authorizes a
transition. Promotion is `update-and-promote`: update the proof block first,
then mark ready.

Read [pr-readiness-policy.md](references/pr-readiness-policy.md).

## Managed body

Only replace content between:

~~~text
<!-- ship-proof:start -->
<!-- ship-proof:end -->
~~~

Preserve all human-authored content outside the markers byte-for-byte. Create
the marker block when absent. Duplicated, nested, reversed, or unbalanced
markers block mutation. Read [pr-body-proof.md](references/pr-body-proof.md).

## Mutation and readback

Before any public effect:

1. Verify repository, remote, base/head branches and SHAs, worktree scope, and
   current validation.
2. Inspect live PRs for the exact repository/base/head tuple; ambiguous or
   mismatched state blocks.
3. Determine `pr_decision` and build the complete managed proof block.
4. Push the exact intended committed head when required.
5. Create, update, or update then promote according to `operation`.
6. Read back repository, base/head refs and SHAs, URL, open/draft state, and the
   managed proof block.

For `observe-existing` or `adopt-existing`, perform no public effect: read back
the exact repository, branch head and publication event, comparison base
ancestry, and zero open exact-tuple PRs. Observation requires null release state.
Final adoption additionally reads back any optional release target, publication
state, complete asset inventory, and asset digests before emitting its receipt.
Emit `SHIP-OBSERVATION-v1` for pre-review observation and `SHIP-ADOPTION-v1`
for final adoption. Either succeeds only after all readback matches the current
readiness input; final adoption must ratify the cited observation when review
credit depends on it.

A zero exit status is not publication proof. If mutation succeeds but readback
fails, report the partial public effect and block; re-read live state before
retrying.

For Actuating input, emit immutable `SHIP-v1` after successful PR readback,
immutable `SHIP-OBSERVATION-v1` after pre-review existing-state readback, or
immutable `SHIP-ADOPTION-v1` after final existing-state readback and return it
to Actuating. Actuating decides how it affects publication currentness and
records the evidence event. Ship never appends Actuating Evidence or interprets
its receipt as architecture, review, or closure authority.

Return the complete canonical receipt bytes together with their SHA-256 digest.
Actuating retains those immutable bytes as the supporting attachment, records
that digest as `publication_observed.receipt_ref`, and must dereference and
exact-match the record and route-specific readback. It exact-matches
`actuation_binding` for `SHIP-v1` and `SHIP-ADOPTION-v1`, and `review_binding`
for `SHIP-OBSERVATION-v1`. Actuating must not substitute its own live-readback
record for any Ship-owned receipt.

## Ship record

Follow [ship-record.md](references/ship-record.md). `actuation_binding` is
required for Actuating `SHIP-v1` and `SHIP-ADOPTION-v1`; the pre-review
`SHIP-OBSERVATION-v1` instead requires its exact stable `review_binding`.
Bindings are omitted for direct shipping. Each receipt describes one
publication epoch and is immutable. Existing PR-based `SHIP-v1` records remain
valid and unchanged.

## Guardrails

- Never publish without validation evidence or an explicit reported limitation.
- Never create a draft by default after full validation.
- Never create a duplicate exact-tuple PR.
- Never use adoption to disguise a mutation, fabricate publication history, or
  accept an unverified public-state field.
- Never overwrite human-authored body content outside the managed block.
- Never promote before updating proof.
- Never claim success without matching live readback.
- Never select architecture, classify findings, count review credit, decide
  closure, or choose Actuating's next action.
- Never merge or land.
- Never stage or commit unrelated work.

## Output

End with:

~~~text
Ship Bottom Line:
- Operation:
- Final state:
- PR:
- Head:
- Validation:
- Publication readback:
- Ship receipt:
- Next owner:
~~~
