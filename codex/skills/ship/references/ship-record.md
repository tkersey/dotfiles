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

Before a review campaign that will later close through adoption, Ship may emit
this read-only observation record after the same exact Git and PR-absence
readback required by adoption:

~~~yaml
ship_observation_record:
  record_version: SHIP-OBSERVATION-v1
  source: actuation
  publication_route: observe-existing
  repository:
  review_target:
    base_ref:
    base_sha:
    head_ref:
    head_sha:
  eligibility:
    open_exact_pr_count: 0
    pr_unrepresentable_reason: head-is-default-branch
  public_state:
    branch:
      provider:
      repository:
      ref:
      sha:
      is_default: true
    observed_at:
  action:
    operation: observe-existing
    result: observed
    mutation_performed: false
  review_binding:
    goal_contract_ref:
    construction_ref:
    subject_digest:
    review_contract_digest:
~~~

`SHIP-OBSERVATION-v1` is not final publication closure. Actuating records its
digest before binding or dispatching the campaign. Final adoption ratifies that
exact digest and tuple; the Evidence Ledger's event order, rather than a
comparison between provider and Ledger clocks, proves observation-before-review.
Observation admits no release state: its input requires
`existing_publication.release == null`. Final adoption alone validates and
records an optional release.

Use this exact companion record only when Actuating supplies a current
`ready-to-ship` receipt for an exact subject that is already public and no
current PR tuple can truthfully represent that publication epoch:

~~~yaml
ship_adoption_record:
  record_version: SHIP-ADOPTION-v1
  source: actuation
  publication_route: adopt-existing
  repository:
  publication_proof:
    pre_review_observation_ref: null | sha256-digest
    provider_event_ref: null | sha256-digest
  review_target:
    base_ref:
    base_sha:
    head_ref:
    head_sha:
  eligibility:
    open_exact_pr_count: 0
    pr_unrepresentable_reason: head-is-default-branch
    observed_at:
  public_state:
    branch:
      provider:
      repository:
      ref:
      sha:
      is_default: true
    release: null | {
      provider: string,
      repository: string,
      publication_state: published,
      draft: false,
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
has unique names, equal cardinality, and exact set equality with the complete
live provider asset inventory, so every live release asset appears exactly
once.

Adoption is read-only. Ship requires `repository`, `review_target.head_ref`,
`public_state.branch.repository`, and `public_state.branch.ref` to identify the
same repository and canonical branch. The canonical ref is the sole branch
identity; normalize short branch names once to `refs/heads/<name>` before
comparison. The provider must report that ref as the
repository's current default branch, and the remote branch SHA must equal
both `public_state.branch.sha` and `review_target.head_sha`. The comparison base
SHA is immutable historical identity: the base and head must differ, and the
base must be an ancestor. A current branch ref need not still resolve to that
base. Ship obtains a complete live PR
inventory whose exact open repository/base/head match count is
`open_exact_pr_count: 0`; `pr_unrepresentable_reason: head-is-default-branch`
records why a feature-branch PR cannot truthfully represent this state. For a
new campaign, `publication_proof.pre_review_observation_ref` is non-null and
Ship exact-matches the referenced `SHIP-OBSERVATION-v1` repository,
review target, branch provider/repository/ref/SHA/default-branch identity, and
`review_binding`. Actuating's Evidence Ledger order makes that observation the
publication-epoch anchor before campaign binding; adoption separately performs
a fresh exact readback of the same current default-branch tuple. The adoption's
current `actuation_binding` must carry the same Goal, Construction, subject, and
review contract, but its closure receipt and Evidence Ledger head may be later.
For a historical campaign, `publication_proof.provider_event_ref` is non-null;
Ship resolves its immutable bytes, recomputes the digest, and exact-matches the
provider, repository, canonical ref, and head. Actuating, not Ship, proves that
event preceded the exact campaign with a content-addressed causal-order
observation. Exactly one publication-proof field is non-null. Matching current
endpoints does not prove uninterrupted publication history.
For a non-null release, Ship requires its live provider to exact-match
`public_state.branch.provider`, requires its live repository
to exact-match the adopted repository, requires `publication_state: published`
and `draft: false`, resolves
`target_sha`, and requires it to equal
`review_target.head_sha`, requires unique receipt asset names and cardinality
equal to the complete live provider inventory, requires exact set equality, and
exact-matches every release field and asset name, size, and SHA-256 digest. Ship
copies the complete current ready-to-ship `actuation_binding` verbatim. Any
mismatch, missing digest, duplicate asset name, unpublished or draft release,
requested mutation, blocked result, or ambiguous target yields no receipt.

Return the complete immutable `SHIP-ADOPTION-v1` record and its SHA-256 digest
to Actuating. It has the same owner boundary as `SHIP-v1`; it is not a second
publication authority.
