# Ship Record

Existing PR-based `SHIP-v1` records remain valid. Their schema and semantics
below are unchanged.

~~~yaml
ship_record:
  record_version: SHIP-v1
  source: direct | actuation
  repository:
  branch:
  base_branch:
  base_sha:
  head_sha:
  existing_pr:
    exists:
    url:
    draft:
  validation:
    build:
    lint:
    tests:
    language_specific:
    acceptance:
  pr_readiness:
    mode: ready | draft | update-existing | promote-draft | blocked
    reason:
    draft_allowed_reason:
  action:
    command:
    result:
    pr_url:
  actuation_binding:
    closure_receipt_ref:
    goal_contract_ref:
    construction_ref:
    subject_digest:
    evidence_head:
    review_contract_digest:
    closure_route: final-closeout
~~~

`pr_readiness.mode` reports the selected publication posture. The controlling
decision keeps operation and final state separate:

~~~yaml
pr_decision:
  operation: create | update | update-and-promote | blocked
  final_state: ready | draft | preserve
~~~

`action.result` is successful only after live PR readback matches repository,
base and head identities, URL, open/draft state, and managed proof block.

`actuation_binding` is required when `source=actuation` and omitted for direct
shipping. Ship copies every field verbatim from Actuating's current readiness
receipt and requires `closure_route: final-closeout`. It does not reconstruct
them from PR text or interpret them as architecture, review, or closure
authority.

`SHIP-v1` is immutable evidence for one publication epoch. Return the complete
record to Actuating; only Actuating may evaluate publication currentness and
record it in the Evidence Ledger.

## Existing-publication adoption

Use this exact companion record only when Actuating supplies a current
`ready-to-ship` receipt for an exact subject that is already public and no
current PR tuple can truthfully represent that publication epoch:

~~~yaml
ship_adoption_record:
  record_version: SHIP-ADOPTION-v1
  source: actuation
  publication_route: adopt-existing
  repository:
  review_target:
    base_ref:
    base_sha:
    head_ref:
    head_sha:
  eligibility:
    open_exact_pr_count: 0
    observed_at:
  public_state:
    branch:
      name:
      sha:
      publication_event:
        provider:
        event_id:
        repository:
        ref:
        before_sha:
        head_sha:
        published_at:
        history_complete_through:
    release: null | {
      tag: string,
      url: string,
      target_sha: git-oid,
      assets: [{ name: string, size: integer, sha256: sha256-digest }]
    }
    observed_at:
  validation:
    build:
    lint:
    tests:
    language_specific:
    acceptance:
  action:
    operation: adopt-existing
    result: adopted
    mutation_performed: false
  actuation_binding:
    closure_receipt_ref:
    goal_contract_ref:
    construction_ref:
    subject_digest:
    evidence_head:
    review_contract_digest:
    closure_route: final-closeout
~~~

Canonicalize the complete record as JSON and hash those exact bytes with
SHA-256. Arrays retain their declared order; `assets` is sorted by `name` and
has exact set equality with the complete live provider asset inventory, so
every live release asset appears exactly once.

Adoption is read-only. Ship requires `repository`, `review_target.head_ref`,
`public_state.branch.name`, and the publication event's repository and canonical
ref to identify the same repository and branch. The remote branch SHA must equal
both `public_state.branch.sha` and `review_target.head_sha`. The comparison base
ref must resolve exactly to `review_target.base_sha`, the base and head must
differ, and the base must be an ancestor. Ship obtains a complete live PR
inventory whose exact open repository/base/head match count is
`open_exact_pr_count: 0`. The provider-authored publication event's `before_sha`
and `head_sha` must equal the review base and head, and complete provider history
through `history_complete_through` must prove it is the latest event for that
repository and ref: the current uninterrupted publication epoch. For a non-null
release, Ship resolves `target_sha`, requires it to equal
`review_target.head_sha`, requires the receipt asset names to equal the complete
live provider asset-name set, and exact-matches every release field and asset
name, size, and SHA-256 digest. Ship copies the complete current ready-to-ship
`actuation_binding` verbatim. Any mismatch, missing or truncated history,
missing digest, requested mutation, blocked result, or ambiguous target yields
no receipt.

Return the complete immutable `SHIP-ADOPTION-v1` record and its SHA-256 digest
to Actuating. It has the same owner boundary as `SHIP-v1`; it is not a second
publication authority.
