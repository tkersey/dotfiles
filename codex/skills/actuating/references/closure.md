# Closure

`closure-decision/v1` is a pure live recomputation. It does not trust summary
booleans or a previously issued decision.

## Inputs

~~~text
current repository state
actuation-run/v1
review-resolution/v1 when review is required
embedded review-admission/v1 for every completed review edit
EF-v1 evidence for every completed material step
CAS-RER-v1 records for selected review lanes
SHIP-v1 when publication was requested and performed
~~~

Repository input is canonicalized to the Git worktree root and the base to its
full commit identity before any path authorization. Every workflow input must
bind to the same repository, base, branch, head, and live-state fingerprint. An
index carrying `assume-unchanged`
or `skip-worktree` flags blocks as `blocked-index-observer-flags`; closure does
not simulate content hidden from the observer. A tracked regular path that Git
reports clean must retain its index blob and executable mode in the raw
worktree; filter, line-ending, or `core.fileMode` aliases block as
`blocked-worktree-observer-alias`. One root gitlink layer is
observed, including its live index flags. A gitlink declared inside that layer
in either HEAD or the index blocks as `blocked-nested-gitlink-observer`; a
retained untracked embedded-repository marker blocks likewise. Nested topology
is outside the observer domain rather than recursively approximated. Unmerged
index stages block as `blocked-unmerged-index`; combined diffs are not admitted
as partial evidence. CAS
additionally carries its producer-native opaque `targetFingerprint`; do not
relabel a local state digest as that field.

## Evidence-fold requirements

Each completed step resolves its exact `evidence_fold_ref`. Evidence must:

- identify the same run and step;
- bind to the current step artifact;
- support the step's done claim;
- contain no proof gap or stale binding;
- report no deleted tests, weakened assertions, skipped checks, reduced
  coverage, or out-of-goal behavior.

Malformed evidence, including a null evidence body, produces a structured
blocking reason and never escapes the closure gate.

For a selected review edit, the gate derives `review-admission/v1` only after
the live resolution exactly selects that step's node, owner boundary, paths,
and verifier. Embed that receipt as the step's `review_admission` before
mutation. Its exact payload is the full admission-time `review_resolution`, an
`observations` block containing review source refs, changed paths, and hunk
IDs, an optional full SHIP-v1 snapshot, and its canonical `admission_digest`.
A NUL-delimited root-path inventory is paired with forced short submodule diff
sections, so patch text, path quoting, and local diff configuration cannot
impersonate or multiply observer control records.
The step remains the sole source of run, artifact, node, owner, paths, and
verifier facts. Completed-step validation replays the same resolution laws
against those step facts and the receipt observations; EF-v1 cites
`review-admission:<admission_digest>` in `review_refs`. The final resolution
does not retroactively relabel an earlier mutation admission, but every node it
marks resolved must still match exactly one completed admitted edit by node,
owner boundary, paths, and verifier.

The resolution inverse assigns each non-empty abstraction exactly one
disposition across all decisions. Its hunk, liability, and retirement balance
fields are exact lists of non-empty strings; malformed elements never collapse
into accepted empty evidence.

Before a later iterative step is admitted, every initial-to-live path-state
delta must already appear in prior completed steps' exact `changed_paths`.
Untouched initial dirt remains user-owned; carried, unclaimed dirt cannot be
assigned to a newly selected step.

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
grant no credit; ineligible findings still require classification. Attempt
identity, chronology, and freshness are validated over the complete visible
current-epoch sequence before proof eligibility filters clean credit. Every
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
artifact, review-contract, resolution, or publication epoch change creates a
new binding and resets prior credit. When `review.ship_receipt` exists, the
binding's `resolutionDigest` is derived from the resolution's verified
self-digest and the canonical digest of that complete SHIP-v1 snapshot.

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
terminal goal state. A valid implement-phase SHIP-v1 returns verdict and goal
`continue`, implementation `complete`, and next owner `goal-actuating`.
Publication-bearing review-closeout requires that prior valid SHIP-v1 and may
then complete after current review proof closes. Preserve the complete receipt
as `review.ship_receipt`; the run gate validates its live PR and artifact
binding before deriving any review admission. The admission records publication
intent by snapshotting that complete SHIP receipt. After an edit and EF-v1, a current
resolved refold must observe that exact admitted node; closure then returns
`ready-to-ship` before CAS. `$ship` updates the PR and replaces
`review.ship_receipt` before another edit or final CAS. Final review-closeout
consumes only the current embedded receipt; a duplicate external SHIP input is
invalid. CAS produced before that replacement belongs to the prior publication
epoch and grants no credit afterward. The replacement must report `updated` /
`update-existing`, retain an
existing PR, and use the exact PR URL captured by the prior admission; creating
a second PR cannot continue the review epoch.

A prior review edit ending `ready-for-closure` admits a following selected step
only when the canonical digest of its SHIP snapshot differs from the newly
embedded receipt;
prior EF-v1 and live validation of that fresh receipt remain mandatory.

SHIP-v1 is an immutable pre-review publication handoff. Its exact
`actuation_binding` contains only `actuation_run_id` and `state_fingerprint`;
review-contract, resolution, lens, and CAS fields are not part of this object.
Never extend or relabel it with the later review epoch; final closure validates
current resolution and CAS evidence separately. Closure queries live PR
metadata and requires its repository, base ref and SHA, head ref and SHA, URL,
open state, and ready status to match the current run and SHIP result.

The final proof-patch is a derived human view emitted after the current closure
decision. It is never an input to that decision.

An `implement` run cannot declare `review.required: true`; review-required work
uses `review-closeout`. A mode relabel cannot erase admission history.
