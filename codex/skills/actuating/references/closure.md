# Closure

`closure-decision/v1` is a pure live recomputation. It does not trust summary
booleans or a previously issued decision.

## Inputs

~~~text
current repository state
actuation-run/v1
review-resolution/v1 when review is required
EF-v1 evidence for every completed material step
CAS-RER-v1 records for selected review lanes
SHIP-v1 when publication was requested and performed
~~~

Every workflow input must bind to the same repository, base, branch, head, and
live-state fingerprint. CAS additionally carries its producer-native opaque
`targetFingerprint`; do not relabel a local state digest as that field.

## Evidence-fold requirements

Each completed step resolves its exact `evidence_fold_ref`. Evidence must:

- identify the same run and step;
- bind to the current step artifact;
- support the step's done claim;
- contain no proof gap or stale binding;
- report no deleted tests, weakened assertions, skipped checks, reduced
  coverage, or out-of-goal behavior.

Node completion remains distinct from goal completion.

## CAS requirements

CAS transports review evidence. Closure derives workflow meaning.

Each closeout record carries:

~~~yaml
workflowBinding:
  actuationRunId:
  artifactStateFingerprint:
  reviewContractFingerprint:
  resolutionDigest:
  selectedLenses: [standard]
  reviewLane: standard
  lensContract: standard-review-v1
~~~

The record tuple must match the live repository, base, and head; its non-empty
native `targetFingerprint` must be identical across the records. The workflow
binding joins that tuple to the live-state fingerprint. The closure gate must
query the complete current `CAS-LIST-v1` envelope itself with the run-bound
base and Codex thread ID; a saved or caller-selected set is not closure
evidence. Standard credit requires a normalized, source-valid strong-principal
record whose matching `recordRefs` row has `proofCreditEligible: true`, with a
distinct record and attempt ID. Ineligible clean records remain visible but
grant no credit; ineligible findings still require classification. Every
record after the first must originate from an explicit fresh attempt.

Partition tuple history by the producer-owned workflow binding before granting
credit. Discard records bound to a foreign `actuationRunId` before tuple or
native target-fingerprint accounting. Superseded epochs grant no credit, but a
findings record remains blocking until a current RF-v2 source cites that record.
Any findings verdict in the exact current epoch poisons that epoch permanently;
later clean attempts cannot clear it. Remediation requires a newly bound
resolution epoch.

Sort the complete current binding sequence by `createdAt`. Closure requires the
maximal clean suffix to contain at least three consecutive standard attempts.
Caller-authored auxiliary labels are observational and grant no credit. Any
artifact, review-contract, or resolution change creates a new binding and
resets prior credit.

## Outcomes

~~~yaml
closure_decision:
  version: closure-decision/v1
  decision_id:
  run_id:
  evaluated_artifact: {}
  run_digest:
  resolution_digest: # null when review is not required
  verdict: complete | ready-to-ship | continue | blocked
  outcomes:
    goal_outcome: complete | continue | blocked
    implementation_outcome: complete | incomplete | not-applicable
    next_owner: none | goal-actuating | ship | human
  evidence_basis: []
  review_basis: []
  ship_basis: []
  reasons: []
~~~

No-code modes may return goal `complete` with implementation
`not-applicable`.

Material work with no publication request completes locally. In the bare
lifecycle, implementation hands off to `$ship`, then continues through
`review-closeout` before final closure is recomputed; ship handoff is not a
terminal goal state. A ship record must carry the same run ID, live-state
fingerprint, review-contract fingerprint, selected lenses, resolution digest,
and CAS record IDs. Closure queries live PR metadata and requires its repository,
base ref and SHA, head ref and SHA, URL, open state, and ready status to match
the current run and SHIP result.

The final proof-patch is a derived human view emitted after the current closure
decision. It is never an input to that decision.

When review is not required, the review-contract fingerprint, resolution
reference, and resolution digest remain `null`; SHIP-v1 copies those values
without inventing an empty-string sentinel.
