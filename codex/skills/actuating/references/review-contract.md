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

## Review scheduling

Review-bearing routes accept one request-local scheduling modifier:

| Mode | Selection | Initial lens dispatch |
|---|---|---|
| `parallel-reviews` | default when no modifier is supplied | standard plus all four auxiliaries concurrently |
| `serial-reviews` | explicit opt-in | standard, footgun-finder, invariant-ace, complexity-mitigator, then fresh-eyes serially |

The modifier changes dispatch topology only. Both modes require every lens,
exactly the same receipt quality, the same finding adjudication, and five
consecutive clean standard attempts on one unchanged head. The initial clean
standard counts as clean attempt one, so the clean path contains nine review
attempts in either mode.

## Review entry

Closure-grade review may start only when the selected construction is completely
realized on the exact head:

```text
complete applicable class-to-generator coverage
complete affected-factor dispositions
family-level mechanism or honest residual for every generator
predicted-sibling or exhaustive disposition
all selected retirements and bypass closures realized
strongest relevant validation current
```

Review is stochastic falsification of that construction, not a mechanism for
finishing it.

### Parallel reviews

Launch all five owner-lived `cas review start --wait` processes before accepting
an initial terminal result.

- A finding, clean result, or transport failure never cancels a sibling.
- Every launched request reaches terminal transport evidence.
- Every finding passes through `$review-fold`.
- An accepted material finding exits convergence only after the initial terminal
  barrier and enters one reconciliation epoch before any mutation.
- Non-material findings are resolved or rejected before serial standard
  confirmation.

### Serial reviews

Launch exactly one owner-lived `cas review start --wait` process at a time in the
initial lens order. Obtain terminal transport evidence and adjudicate every
finding before dispatching the next request.

- A finding that does not authorize material mutation does not erase valid
  exact-head receipts; continue when its disposition permits review to proceed.
- A finding that reopens Goal authority or remains unresolved blocks rather than
  allowing later reviews to assume a settled target.
- When an adjudicated finding leads to material code mutation, stop before the
  next request and enter one reconciliation epoch. Do not restart until its
  complete selected target is realized and proved on the final head.

## Material finding transition

One reconciliation epoch owns every review-induced material mutation for the
current evidence cut.

- Wait for every already-launched request required by the selected schedule.
- Fold all currently applicable accepted classes before selecting mutation.
- Complete causal-generator, sibling, factor, and target dispositions.
- Materialize the direct-repair gate once for the complete target when direct
  repair is selected.
- Keep review dispatch closed across coherent realization commits.
- Restart the selected initial schedule only on the completely realized and
  proved final head.

A same-generator recurrence after repair cannot authorize another enumerative
member extension. It requires separation proof, generative or exhaustive family
evidence, or theory/architecture reconsideration.

## Request-local recovery

A terminal request without a structured semantic verdict:

- contributes no semantic attempt or clean credit;
- preserves completed review evidence on the unchanged head;
- may run one fresh exact-request recovery;
- in `parallel-reviews`, runs recovery after the initial terminal barrier;
- in `serial-reviews`, runs recovery before dispatching the next request;
- blocks after a second verdictless terminal result.

Recover a live known handle with CAS `wait`; do not create a duplicate attempt.

## Convergence

After the selected initial schedule is fully adjudicated, launch fresh standard
attempts serially until the trailing exact-head clean suffix reaches five.

- A standard finding resets the suffix to zero.
- A material standard finding stops further confirmations and enters one
  reconciliation epoch.
- An auxiliary finding does not change standard credit unless resolution changes
  the head.
- Any material Git head change invalidates all prior credit by tuple mismatch and
  permits restart only after the reconciliation epoch's complete target is
  realized and proved.
- No credit crosses a head change.

## Resumption

Credit only exact receipts currently available to Actuating.

- Reuse a known CAS handle or exact receipt when its complete binding can be
  revalidated.
- A prior summary, claimed count, or PR prose grants no credit.
- If the complete current evidence set cannot be resolved after interruption,
  restart the selected schedule from its initial standard.

This fail-closed restart is deliberate. Actuating maintains no review database.

## Findings

A finding affects action only after `$review-fold` classifies the observed fact,
applicability, governing law, and causal relationship. Suggested patches remain
reviewer prose. Neither CAS nor Review Fold selects architecture or grants
mutation.
