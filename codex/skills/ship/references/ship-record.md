# Ship Records

Ship records are immutable owner-issued evidence for one public-state epoch.
They bind exact Git and provider facts but grant no architecture, review, or
closure authority.

## Pull-request publication

Existing direct `SHIP-v1` records remain historical evidence. Current
publication uses:

```yaml
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
  actuation_binding: null | {
    goal_context_digest: sha256-digest,
    review_contract_digest: sha256-digest,
    review_context_digest: null | sha256-digest,
    publication_required: boolean
  }
```

`action.result` is successful only after live PR readback matches repository,
base/head identities, URL, open/draft state, and managed proof block.

For Actuating input, Ship copies `actuation_binding` verbatim. It does not
reconstruct the Goal, architecture, review state, or closure judgment.

## Pre-review public-state observation

```yaml
ship_observation_record:
  record_version: SHIP-OBSERVATION-v2
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
  actuation_binding:
    goal_context_digest:
    review_contract_digest:
```

Canonicalize the complete record as JSON and hash those exact bytes with
SHA-256. Actuating includes that digest in the canonical review context before
CAS dispatch.

Observation succeeds only when:

- the provider repository and canonical head ref match the input;
- the head ref is the live default branch;
- the live head equals the supplied head;
- base differs from head and is an ancestor;
- base/head refs name the same default-branch publication route;
- the complete live open-PR inventory contains zero exact matches;
- no release is supplied;
- no mutation occurs.

## Existing-publication adoption

```yaml
ship_adoption_record:
  record_version: SHIP-ADOPTION-v2
  source: actuation
  publication_route: adopt-existing
  repository:
  publication_observation_ref:
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
    goal_context_digest:
    review_contract_digest:
    review_context_digest:
```

Ship resolves `publication_observation_ref`, recomputes its digest, and
exact-matches repository, canonical ref, base/head, Goal context, and Review
Contract. Actuating supplies the exact current review context whose digest
contains the same observation reference; the credited CAS receipts echo request
fingerprints derived from that context.

This binding proves observation-before-review without an Actuating event log.
A campaign lacking the bound observation is ineligible; obtain a fresh
observation and fresh review.

For a non-null release, Ship requires current provider state `published`,
`draft: false`, target equal to the reviewed head, unique asset names, equal
cardinality and exact set equality with the complete live inventory, and exact
field and digest matches.

Adoption is read-only. Any mismatch, incomplete provider inventory, duplicate
asset, requested mutation, or stale review context yields no receipt.

Return the complete canonical record and SHA-256 digest to Actuating.
