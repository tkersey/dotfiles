---
name: ship
description: "Create, update, or promote a pull request for validated work without merging. Also observe or adopt an exact already-public subject when Actuating explicitly hands off that route."
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

## Selected guidance

For `pull-request`, read [pull-request.md](pull-request.md) before any push or PR
effect. It owns readiness, managed-body preservation, mutation order, and readback.
For an explicit Actuating `observe-existing` or `adopt-existing` handoff, read
[existing-publication.md](existing-publication.md); these routes remain read-only.
All routes retain Input, Receipts, Guardrails, and Output below. Do not load the
other route's procedure just because it shares this package.

<a id="pull-request-route"></a>
Pull-request route: [pull-request.md](pull-request.md#pull-request-route).
<a id="managed-body"></a>
Managed body: [pull-request.md](pull-request.md#managed-body).
<a id="public-mutation-and-readback"></a>
Public mutation and readback: [pull-request.md](pull-request.md#public-mutation-and-readback).
<a id="existing-publication-observation"></a>
Existing-publication observation: [existing-publication.md](existing-publication.md#existing-publication-observation).
<a id="existing-publication-adoption"></a>
Existing-publication adoption: [existing-publication.md](existing-publication.md#existing-publication-adoption).

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

Report the PR link, resulting public state, head, and relevant validation or
limitations concisely. Include receipt identity and the next owner when an
enclosing workflow needs that handoff. Preserve the full immutable publication
evidence in the Ship receipt; do not repeat its fields as a mandatory chat form.
