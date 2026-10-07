# Negative Ledger capture and scope

Read [store.md](store.md) before a canonical operation. Scope review alone grants
no write or retry permission. If a lifecycle correction is selected, read
[lifecycle.md](lifecycle.md) before that transition.

## Capture Workflow

Capture only a failure that changes future routing: witnessed no-effect attempt,
local/global regression, unsound route, complexity disproportionate to value,
revert with concrete rationale, repeated proof-wound pattern, or a strategy pivot
whose abandoned route would otherwise be retried.

Before capture/promotion, apply the [scope challenge](#exclusion-scope-challenge).
A witnessed failure alone does not justify its breadth.

```bash
ledger transact \
  --definition "$negative_ledger_definition" \
  --operation capture \
  --store-root "<context.store_root>" --store-id "<context.store_id>" \
  --input capture=capture.json \
  --format json
```

`capture.json` contains one `record`, including requested initial `status`.
Inadequate witness evidence means `need-evidence` or `capture_candidate`, not an
active exclusion. Active capture requires supported scope/identity, immutable
artifact identity, structured source references, applicability conditions,
a narrow exclusion, and identified reopening criteria. Select `need-evidence`
when structure is incomplete; never assert `active` after Ledger rejects it.

Every transition to `active`, including promotion/reactivation/reopening,
requires transition proof and a complete replacement record with status `active`.
Use the dedicated operation to replace the reducer's retained record atomically:

```bash
ledger transact \
  --definition "$negative_ledger_definition" \
  --operation promote \
  --store-root "<context.store_root>" --store-id "<context.store_id>" \
  --input promotion=promotion.json \
  --format json
```

## Exclusion Scope Challenge

Ask whether a materially different realization of the excluded route could meet
the same requirement under declared applicability conditions. Distinguish a
failed implementation from a failed strategy; broader suppression requires a
stronger scope argument. Inspect existing witnesses/proofs first; use a
necessary, authorized discriminating evaluation when evidence is insufficient.
No fixed number of challenges or successful samples establishes a universal ban.

An inspectable success within the exclusion scope is counterevidence to its
breadth; success outside scope is not. Confirm the case exercises the disputed
route, uses an independently justified requirement as oracle, and isolates the
route rather than an invalid fixture or unrelated environment error. An imagined
alternative warrants scrutiny, not a claimed successful execution.

A successful sample alone does not refute a failure-rate, cost, or risk claim.
Evaluate counterevidence against the recorded hypothesis and measurement
conditions; contrary samples can warrant investigation without changing the
gate. Do not treat variable outcomes as deterministic impossibility proofs.

Use existing hypothesis, outcome, evidence, exclusion, applicability, and
reopening fields to retain the supported boundary. A stale cache entry may
justify excluding reuse when its key omits a semantic input, not all caching.
For a failure involving feedback or accumulated effects, retain the relevant
workload/regime, observation delay, and evaluated horizon in those same fields.
Separate the witnessed outcome from a hypothesized mechanism; recurrence alone
does not establish policy resistance or a general strategy exclusion. A changed
delay, capacity, or response policy can be an applicability or reopening condition
when it could change the result. Do not add a pattern schema or diagnosis authority.
Choose the narrowest useful supported scope, retaining `need-evidence` or
`capture_candidate` when support is inadequate. Do not weaken active structure
just to make a transaction pass.

For counterevidence to an active record, preserve the gate until its legal
source-owned lifecycle changes it. Capture any still-supported narrower
exclusion before superseding an overbroad one, linking evidence/replacement with
structured source references. Reopening still requires proved changes to
identified existing criteria; an unjustified old conclusion is not a fabricated
artifact change. Use proof-bearing supersession when appropriate.

Scope review grants no retry/mutation permission. Do not bypass an active exact
applicable exclusion by calling the retry a test, sandbox, or experiment. Use
supported lifecycle and enclosing authority before retry; project the gate again.
An unchanged/inapplicable challenge requires no write. Stop when scope is
supported, narrowed, or pending evidence. Correcting an exclusion does not
activate Learnings automatically or grant architecture-selection authority.

