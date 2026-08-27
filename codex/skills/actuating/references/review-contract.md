# Static Review Contract

Actuating owns one checked-in policy:
[review-contract.json](review-contract.json). It is source policy, not mutable
workflow state.

## Binding and owner authority

Read the exact Review Contract bytes and every required lens instruction byte.
Do not trim or normalize them.

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
  counterexample_basis_digest:
  counterexample_horizon_complete_for_claims: true | false
  proof_inventory_digest:
  validation_summary:
  publication_observation_ref: null | sha256-digest
```

Compute:

```text
campaign_id = sha256(
  "actuating-review-campaign/v3" || NUL ||
  repository || NUL || base_sha || NUL || head_sha || NUL ||
  target_fingerprint || NUL || review_contract_digest || NUL ||
  review_context_digest
)

request_fingerprint = sha256(
  "actuating-review-request/v3" || NUL ||
  campaign_id || NUL || request_id || NUL || lens_name || NUL ||
  role || NUL || instruction_digest
)
```

CAS owns review execution, terminal receipts, exact target tuples, and finding
provenance. Review Fold owns current finding classification and the append-only
semantic admission of accepted witnesses through
`review-fold/counterexample-corpus`. Actuating checks owner-issued evidence
directly and owns review credit and architectural consequences.

Supply only the request ID and fingerprint through CAS's workflow binding.
Credit only a structured semantic verdict with strong principal evidence, exact
current tuple, exact instruction and workflow binding, and the backend capability
required by the JSON contract. Process exit, prose, or a thread handle is not a
verdict.

The five required lenses and five-consecutive-standard-clean theorem remain
unchanged.

## Counterexample history projection

Before the first Review Fold for a review-bearing decision, project the
repository basis from:

```text
review-fold/counterexample-corpus
```

Include those rows as prior owner evidence. Recompute current applicability,
Goal-law authority, recurrence, observational classes, family hypotheses, and
post-elimination relation. A `CEX-*` identity is durable evidence that the
original witness was accepted under its recorded Goal and subject; it is not a
current liability, family, or construction claim.

An absent local store is an empty local corpus, not proof of complete history.
An unavailable or invalid projection makes the evidence horizon incomplete.
Actuating may still use exact current-wave evidence, but it must not infer
`first-observed`, disjointness, or family elimination from historical absence.
When recurrence or a post-elimination claim depends on unavailable history,
return `unknown` or `blocked` rather than guessing.

After every fold, capture each independent witness that is current, `entailed`,
and `accepted`. Do not capture reviewer preferences, strengthenings, new
requirements, underdetermined claims, rejected findings, non-current witnesses,
classes, families, suggested repairs, or current architecture.

## Candidate lifecycle

```text
realizing
  construction theorem or exact-head proof inventory incomplete

reviewable
  counterexample basis, carrier, producer migrations, bypass closure,
  compensator dispositions, and required proof inventory complete on one head

invalidated
  applicable entailed material finding falsified the candidate
```

Only `reviewable` may dispatch closure review.

### Construction-theorem proof lease

A construction theorem is the current conjunction of:

```text
accepted Goal and law
invalid-family predicate and comparison domain
canonical owner and earliest enforceable cut
admitted carrier and semantic identity
sanctioned producer and trusted-consumer topology
producer factorization and bypass dispositions
required-valid interpretation
proof universe, falsifier, validity horizon, and claim strength
```

Its completeness claim is a revocable proof lease, not a reusable assertion.
A direct falsifier of any declared theorem premise revokes the theorem
immediately.

Otherwise, recurrence is adjudicated only from exact Review Fold evidence:

```text
first exact same-claim successor invalidation
  -> invalidate the candidate
  -> localize the earliest failed premise
  -> retain the theorem only when exact evidence confines the defect
     to realization or proof

second exact same-claim successor invalidation under a materially unchanged theorem
  -> revoke the theorem and its reviewable claim
  -> close mutation, Ship, and review
  -> prohibit a third reviewable candidate under that theorem
```

`same-law-different-family`, `outside-horizon`, `different-law`, and `unknown`
do not increment this recurrence. Same owner or broad law alone is insufficient.

A theorem is materially changed only when the successor revises at least one
falsified semantic premise or its proof universe—not merely code, prose, tests,
or the reviewed head. Re-entry after revocation requires:

```text
source-derived disposition for every producer, parser, serializer, adapter,
  compatibility path, recovery path, trusted consumer, and bypass
material theorem delta tied to the failed premise
executable or exhaustive factorization witness capable of failing when one
  sanctioned producer or bypass is omitted
fresh exact-head construction proof
```

Repeated recurrence is material new evidence. It may re-open Metanoetic and
Universalist reclassification on the changed decision surface; it does not add a
second pass on an unchanged surface.

## Review entry

Require on the exact head:

```text
complete accepted Goal and proof inventory
projected counterexample basis or explicit incomplete-horizon disposition
complete current counterexample basis
invalid family and sibling/exhaustive disposition
admission graph
earliest enforceable cut and admitted carrier
every sanctioned producer disposition
every bypass disposition
required-valid and compatibility proof
downstream primary compensator disposition
all selected migration and retirement work realized
```

Each proof-inventory entry must be unique and have exact-head passing evidence or
authority-backed `not-applicable`. Aggregate proof credit is valid only when the
declared dependency graph covers the required proof.

A known required proof may not first run after review convergence. Such a
discovery proves the candidate was never reviewable and invalidates all credit.

## Invalidation versus evidence acquisition

A material finding immediately:

```text
invalidates the candidate
sets all review credit to zero
closes mutation and new confirmation dispatch
does not request a patch
```

The initial independent falsification wave must still complete against the
frozen candidate.

### Parallel mode

Launch all five initial owner-live requests and never cancel siblings. Wait for
every launched request, including required request-local recovery, to reach a
semantic outcome before closing the evidence cut.

### Serial mode

After the first material finding, continue the remaining initial lenses in the
static order against the same frozen head **for evidence only**:

```text
no mutation
no clean credit
no successor assumptions
```

This completes the same current-wave counterexample basis as parallel mode
without concurrent dispatch.

### Standard confirmation

The initial five-lens wave is already complete. A material confirmation finding
invalidates the candidate and stops further confirmation; no additional lens
wave is implied.

### Request-local recovery

A verdictless terminal contributes no semantic outcome or clean credit. It may
receive one fresh exact-request recovery. Required recovery remains part of the
semantic barrier after invalidation. A second verdictless terminal blocks.

## Evidence cut and successor

After the initial semantic barrier, close one cumulative cut containing:

```text
projected CEX records and exact source references
all current-wave semantic outcomes
all current applicability and Goal-law classifications
all executable witnesses and independence bases
predicted sibling probes or exhaustive-domain evidence
required-valid and compatibility proofs
current construction topology and post-elimination falsifiers
counterexample horizon completeness and missing sources
```

Review Fold captures newly accepted counterexamples after classification and
returns their IDs. The cut uses corpus rows as durable source evidence but
contains current reclassifications; Actuating does not store a second copy.

Actuating then compiles one successor:

```text
invalid family
-> admission graph
-> earliest cut
-> admitted carrier
-> producer migration
-> bypass closure
-> compensator retirement
-> exact-head proof
```

Review stays closed across realization commits. No intermediate head is
reviewable.

## Two routes

Per causal generator:

```text
construction-normalization
isolated-restoration
```

Isolated restoration uses one generator-local
`actuating/direct-repair-admission` materialization bound to the exact starting
predecessor. One admitted generator may span coherent commits until complete; a
later generator gates against the then-current predecessor. Materialize at most
once per generator and never per finding. Architecture successors do not use
that gate.

## Lens obligations

```text
standard
  find an admitted family member or lost required-valid behavior

footgun-finder
  find a bypass, illicit mint, unsafe adapter, or alternate producer

invariant-ace
  falsify carrier closure, legal transitions, or composition

complexity-mitigator
  find duplicate semantic owners or downstream primary compensators

fresh-eyes
  find an earlier enforceable cut, better carrier, or erased distinction
```

Reviewers report evidence and affected law; they never select a repair.

## Convergence and resumption

After a successor becomes `reviewable`, restart the selected schedule on its
final head. Require five consecutive distinct standard cleans. No credit crosses
a material head change.

Reuse only exact CAS receipts and `CEX-*` records whose source references and
subjects can be revalidated. If the current review receipts cannot be resolved,
restart from the initial standard. If historical counterexample evidence cannot
be resolved, mark the horizon incomplete; never reconstruct it from prose or
memory.

A first exact same-claim successor finding reopens and localizes the construction
theorem. A second under a materially unchanged theorem revokes it. No third
reviewable candidate may issue until the theorem materially changes and its
source topology and factorization are proved.
