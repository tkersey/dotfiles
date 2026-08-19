# Static Review Contract

Actuating owns one checked-in review policy:
[review-contract.json](review-contract.json). It is source policy, not mutable
per-goal state and not a Ledger definition.

## Contract identity

Before dispatch, read the exact raw bytes and compute:

```text
review_contract_digest = sha256(raw review-contract.json bytes)
```

For each required lens, read the exact instruction file named by
`instructions_ref` and compute:

```text
instruction_digest = sha256(exact UTF-8 instruction bytes)
```

Do not trim or normalize. A changed policy or lens file naturally produces a
new binding. No stored self-digest or manifest copy is required.

## Review context

Build one canonical ephemeral context:

```yaml
review_context:
  repository:
  base_sha:
  head_sha:
  target_fingerprint:
  goal:
    objective:
    non_goals: []
    required_observations: []
    compatibility: []
  validation_summary:
  publication_observation_ref: null | sha256-digest
```

Canonicalize this JSON in memory and compute `review_context_digest`. The
context is request input, not a durable artifact.

When reviewing already-public state for later adoption,
`publication_observation_ref` is the exact Ship publication observation digest obtained
before dispatch.

## Campaign and request bindings

```text
campaign_id = sha256(
  "actuating-review-campaign/v2" || NUL ||
  repository || NUL ||
  base_sha || NUL ||
  head_sha || NUL ||
  target_fingerprint || NUL ||
  review_contract_digest || NUL ||
  review_context_digest
)
```

For each required request:

```text
request_fingerprint = sha256(
  "actuating-review-request/v2" || NUL ||
  campaign_id || NUL ||
  request_id || NUL ||
  lens_name || NUL ||
  role || NUL ||
  instruction_digest
)
```

Supply only `requestId` and `requestFingerprint` through CAS's opaque workflow
binding. Actuating retains the context and expected fingerprints during the
active run. CAS echoes the binding and owns the exact review receipt.

## CAS boundary

Before dispatch, require the current CAS review compatibility and capability
checks. Each credited attempt must report:

- a structured semantic verdict;
- strong principal evidence with no reduced protection;
- backend class `cas-start-wait`;
- exact current base, head, and target fingerprint;
- exact workflow-binding echo;
- exact instruction bytes or their receipt-bound digest;
- status `clean` or `findings`.

Process exit, prose, or a thread handle is not a review verdict.

Actuating checks owner-issued receipt fields directly. Do not pass CAS receipts
through Ledger or copy them into an Actuating event log.

## Compact lenses

The required lenses are:

| Lens | Role | Instruction |
|---|---|---|
| standard | standard | `standard-review.md` |
| footgun-finder | auxiliary | `lenses/footgun-review.md` |
| invariant-ace | auxiliary | `lenses/invariant-review.md` |
| complexity-mitigator | auxiliary | `lenses/complexity-review.md` |
| fresh-eyes | auxiliary | `lenses/fresh-eyes-review.md` |

These are bounded read-only projections. They do not launch the standalone
skill workflows, spawn authority lanes, persist artifacts, select repairs, or
certify closeout.

## Initial wave

Launch all five owner-lived `cas review start --wait` processes before accepting
an initial terminal result.

- A finding, clean result, or transport failure never cancels a sibling.
- Every launched request reaches terminal transport evidence.
- The initial standard clean is clean attempt one.
- Every finding passes through `$review-fold`.
- Accepted pressure is resolved or rejected before serial confirmation.

## Request-local recovery

A terminal request without a structured semantic verdict:

- contributes no semantic attempt or clean credit;
- preserves completed sibling evidence on the unchanged head;
- may run one fresh exact-request recovery after the initial barrier;
- blocks after a second verdictless terminal result.

Recover a live known handle with CAS `wait`; do not create a duplicate attempt.

## Convergence

After the initial wave is fully adjudicated, launch fresh standard attempts
serially until the trailing exact-head clean suffix reaches five.

- A standard finding resets the suffix to zero.
- An auxiliary finding does not change standard credit unless resolution changes
  the head.
- Any material Git head change invalidates all prior credit by tuple mismatch
  and requires a fresh 1+4 wave.
- No credit crosses a head change.

## Resumption

Credit only exact receipts currently available to Actuating.

- Reuse a known CAS handle or exact receipt when its complete binding can be
  revalidated.
- A prior summary, claimed count, or PR prose grants no credit.
- If the complete current evidence set cannot be resolved after interruption,
  start a fresh full wave.

This fail-closed restart is deliberate. Actuating maintains no review database.

## Findings

A finding affects action only after `$review-fold` classifies the observed fact,
applicability, governing law, and causal relationship. Suggested patches remain
reviewer prose. Neither CAS nor Review Fold selects architecture or grants
mutation.
