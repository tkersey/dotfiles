# Static Review Contract

Actuating owns one static review law. It is not mutable per-goal state and does
not become Ledger policy.

## Canonical contract

The checked-in [review-contract.json](review-contract.json) bundle contains the
complete normative `actuating-review-contract/v1` under `review_contract` and
supporting resource manifests under `lens_contract_manifests`. The normative
object contains the immutable nonblank contract identity, topology,
convergence law, recovery law, quality predicate, and all five nonblank lens
references and digests. Each `required_lenses` entry has exactly `name`,
`role`, `contract_ref`, and `contract_digest`. It is the one static contract;
do not synthesize a per-goal copy.

Each same-name supporting manifest declares a sorted, duplicate-free
`resources` array of exact repository-relative UTF-8 paths and SHA-256 digests
of their raw file bytes. The normative `contract_ref` must be one of those
paths. Compute its package digest from the exact bytes and separators:

~~~text
lens_contract_digest = sha256(
  "actuating-lens-contract/v1" || 0x00 ||
  for each resource sorted by path:
    path || 0x00 || resource_digest || 0x00
)
~~~

Encode every digest as `sha256:` plus 64 lowercase hexadecimal digits. The
standard lens is the compact checked-in
[standard-review.md](standard-review.md); auxiliary packages bind the actual
skill resources enumerated in the JSON rather than an empty or symbolic ref.

Compute the aggregate published digest from canonical JSON after replacing
only the nested `review_contract.contract_digest` with JSON `null`:

~~~text
review_contract_digest =
  sha256(canonical_json(review_contract with contract_digest = null))
~~~

Canonical JSON sorts object keys lexicographically, emits arrays in their
declared order, uses UTF-8, and emits no insignificant whitespace. Store the
result in `contract_digest`. A changed resource byte, lens, role, threshold,
recovery rule, material-change rule, or quality predicate requires recomputing
the affected package and aggregate digest and assigning a new immutable
contract identity; no per-goal snapshot may revise the static contract.

Actuating constructs and supplies the exact canonical Review Contract. Ledger
may validate its schema, recompute `contract_digest`, and compare that digest
with a campaign or Counterexample subject. Ledger must not substitute an
internal hardcoded contract, choose a contract version, or interpret the
contract into review credit.

Derive the campaign identity from the exact UTF-8 strings and NUL separators:

~~~text
campaign_id = sha256(
  "actuating-review-campaign/v1" || 0x00 ||
  goal_id || 0x00 ||
  construction_ref || 0x00 ||
  subject_digest || 0x00 ||
  review_contract_digest
)
~~~

The `review_contract_digest` in every `counterexample-set/v1` subject binds the
current static Review Contract. A Counterexample Set produced from a CAS finding
must also bind that finding's campaign, whose digest must match. A failing test,
incident, compatibility failure, or other non-review falsifier does not require
a review campaign before classification or repair. Ledger validates the
artifact's structural subject tuple and digest shape; Actuating evaluates source
provenance and any campaign relationship. Actuating decides whether the matched
evidence earns credit. Any changed campaign input creates a different campaign
and admits no prior review credit.

## Required topology

The required lenses are:

| Lens | Role |
|---|---|
| standard | standard |
| footgun-finder | auxiliary |
| invariant-ace | auxiliary |
| complexity-mitigator | auxiliary |
| fresh-eyes | auxiliary |

Before the first dispatch, Actuating binds all five requests to one current
Goal, Construction, review subject, campaign identity, exact lens contract,
exact instruction digest, and unique opaque request identity.

Derive each request fingerprint from exact UTF-8 strings and NUL separators:

~~~text
request_fingerprint = sha256(
  "actuating-review-request/v1" || 0x00 ||
  goal_id || 0x00 || campaign_id || 0x00 || subject_digest || 0x00 ||
  request_id || 0x00 || lens_name || 0x00 || role || 0x00 ||
  lens_contract_digest || 0x00 || instruction_digest
)
~~~

`instruction_digest` is `sha256:` plus the SHA-256 of the exact UTF-8
`developerInstructions` bytes supplied to CAS, with no trimming or newline
normalization. The retained CAS receipt must contain those exact
`developerInstructions`. Before granting credit, Actuating hashes the receipt
field and requires equality with the bound `instruction_digest`; the opaque
workflow-binding echo alone is insufficient proof of instruction fidelity.

CAS receives only `request_id` and `request_fingerprint` in its opaque
`workflowBinding` and must echo both unchanged. Semantic credit requires that
exact echo and exact equality of the receipt's `baseSha`, `headSha`, and
`targetFingerprint` to the current captured tuple. A digest, request, campaign,
subject, lens, role, instruction, or tuple mismatch earns no credit.

## CAS owner-fact projection

CAS owns the current receipt protocol and reports these exact owner facts under
`reviewVerdict`:

~~~text
tupleVerdictExists
principalStrength
accountFingerprintReducedProtection
backendClass
baseSha
headSha
targetFingerprint
workflowBinding
status
~~~

Actuating owns the semantic credit predicate. Credit requires the exact bound
request and context, `tupleVerdictExists == true`,
`principalStrength == "strong"`,
`accountFingerprintReducedProtection == false`,
`backendClass == "cas-start-wait"`, a current tuple, and a structured `clean`
or `findings` status. The exact `workflowBinding` must match the request whose
fingerprint binds the lens contract and instruction digest. The
`attempt_quality` fields above name Actuating policy; they are not alternate
CAS receipt keys. Invalid, incomplete, reduced, fallback, unknown-backend, or
mismatched attempts remain observable but receive no semantic credit.

## Initial wave

Actuating launches standard plus four auxiliary CAS requests concurrently.
All five starts must exist before it accepts an initial terminal result. A
finding, clean result, start failure, or transport failure never cancels a
launched sibling; every sibling reaches terminal transport evidence.

On a publication-bearing route, Actuating maps the current published subject
to CAS `--base <bound-base>` and requires every returned base, head, and target
fingerprint to match that binding. It must not select `--uncommitted` for a
clean published checkout: that selector covers only working-tree changes, not
the published branch delta. `--commit HEAD` is sufficient only when that one
commit is itself the complete bound review subject.

Each `review_attempt_started` observation must cite the exact CAS start
`receipt_ref`. Ledger checks only that the reference is a digest. Actuating
evaluates the five distinct, current, exactly bound start receipts and owns the
all-five-start barrier.

CAS owns attempt execution and the structured receipt. Actuating owns dispatch
timing, validates request and subject identity, and evaluates the owner facts
under the static Review Contract. Ledger may append the receipt reference and
project structural attempt history. Ledger never launches CAS, classifies its
facts as `clean` or `findings`, or turns any field or process exit status into
review credit.

## Request-local recovery

A terminal attempt without a structured semantic verdict:

- contributes no semantic attempt and no clean credit;
- changes only that request to recovery-required;
- preserves sibling facts on the unchanged subject;
- waits for the initial non-cancelling transport barrier;
- reruns the exact request once with the same subject and binding plus a fresh
  attempt identity;
- blocks after a second verdictless terminal result.

Retrying lost output from an active exact attempt adopts that attempt; it does
not create a second attempt or credit. The admitted recovery creates distinct
attempt B. Active, stale, exhausted, blocked, non-current, or
barrier-incomplete requests expose no recovery action.

## Findings and Counterexamples

Every finding passes through `$review-fold` before repair. It separates fact
from suggested patch, quotients duplicates, and authors the current
`counterexample-set/v1`. Accepted classes require Actuating to evaluate the
current Construction and select a current successor or blocker before any
mutation. Rejection requires evidence.

Every entry in `finding_refs` is the `sha256:` digest of the exact canonical
CAS finding-row bytes. CAS `findingId` and best-effort `findingFingerprint`
values remain provenance; neither participates in Counterexample class
identity.
A `follow-up` class remains recorded and routed to a successor goal but is
nonblocking for the current Goal. Only applicable accepted debt and applicable
blockers constrain current mutation or closure.

Review and Counterexample artifacts never select a repair or grant mutation.

## Convergence

The initial wave succeeds only when the standard attempt is clean, every
auxiliary is terminal and current, every finding is classified, no accepted
Counterexample remains unresolved, and the review subject is unchanged. That
standard clean is clean attempt one.

Actuating then launches fresh standard attempts serially until the trailing
current-subject streak reaches five consecutive distinct clean attempts.

A standard finding on an unchanged subject resets the standard streak to zero.
Auxiliary facts remain current on that unchanged subject. If adjudication causes
a material subject change, all review credit resets and a fresh concurrent 1+4
wave is required. An auxiliary finding does not alter standard credit unless it
causes a material subject change.

When the initial-wave standard attempt reports findings but adjudication causes
no material subject change, the four terminal auxiliary results remain current.
After every finding is classified and every accepted class is resolved or
rejected, Actuating may launch a fresh standard attempt from streak zero; its
first clean result establishes attempt one. It does not relaunch the auxiliaries
unless the subject changes.

No review credit crosses a material subject change. There is no carry.

The review subject includes every repository artifact whose correctness is in
scope. It excludes only Artifact Kernel control storage and declared evidence
attachments. Any other subject-digest change is material.

## Independence

Reviewers receive the exact subject, pinned lens contract, exact instructions,
and opaque workflow identity. They do not automatically receive persuasive
architecture rationale. After independent results return, Actuating joins each
accepted Counterexample to the Construction claim it falsifies.

Changing the lens registry, a lens role or contract, the clean threshold, the
recovery law, the quality predicate, or the material-change law creates a new
immutable Review Contract identity and digest.
