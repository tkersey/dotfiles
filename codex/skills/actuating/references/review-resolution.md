# Review Resolution

Use `review-resolution/v1` after `$review-fold` has classified a current review
source. The resolution owns repair strategy; individual findings do not.

## Shape

~~~yaml
review_resolution:
  version: review-resolution/v1
  resolution_id:
  run_id:
  artifact:
    repo:
    base_sha:
    branch:
    head_sha:
    state_fingerprint:
  review_folds:
    - version: RF-v2
      fold_id:
      goal_id:
      source: {}
      findings: []
      compression: {}
      routing_obligations: []
  finding_ids: []
  change_surfaces: []
  review_profile:
    review_contract_fingerprint:
    selected_lenses: [standard]
  decisions:
    - decision_id:
      owner_boundary:
      finding_ids: []
      liability_classes: []
      strategy: local-repair | replacement-kernel | blocked
      alternatives_considered: []
      falsifier:
      abstraction_account:
        - abstraction:
          disposition: retain | retire | collapse | delegate | replace
          obligation_id:
      selected_work_node: # optional while another owner decision is current
        node_id:
        run_id:
        owner_boundary:
        paths: []
        verifier: []
      blockers: []
  outcome:
    status: pending | clean | resolved | blocked
    resolution_digest:
    semantic_balance:
      accounted_hunks: []
      unaccounted_hunks: []
      covered_liabilities: []
      uncovered_liabilities: []
      added_constructs:
        - name:
          obligation_id:
          obligation_ref:
          replaces:
      required_retirements: []
      completed_retirements: []
      dominated_remaining: []
~~~

`change_surfaces` records judgment-derived surfaces. The gate also derives
`multi-live-path` whenever the accepted-base diff contains more than one path,
so callers cannot suppress that change surface by omission.

## Strategy selection

Use `local-repair` only when an existing owner abstraction can absorb the
correction without a new protocol, state, helper abstraction, branch family, or
wound-specific test family.

Use `replacement-kernel` when local repair would distribute one invariant,
preserve a dominated abstraction, add machinery to tolerate invalid state, or
patch several symptoms of one owner-level cause. Admit at most one current
owner node; keep other owner decisions strategy-complete but node-free while
the outcome is `pending`.

Use `blocked` when authority, intended semantics, current evidence, or a
falsifiable verifier is absent.

Embed the validated RF-v2 evidence used by the resolution. Rejected,
proof-only, ask-human, and follow-up findings remain terminal RF-v2
dispositions and do not enter this object. Dangling fold IDs
are insufficient: the gate joins the current artifact and exact
`resolution-input` finding set to each decision. In `remediation-plan`, record
the strategy but omit `selected_work_node`; the plan grants no execution
authority. In review closeout, a pending multi-owner resolution may omit nodes
for non-current decisions. Re-fold the changed artifact before admitting the
next owner node; closure rejects `pending`.

Record rejected alternatives and a falsifier for every material decision.
Judgment owns the strategy; comment count does not.

## Abstraction audit

Audit every abstraction participating in the touched invariant or transition,
not only edited symbols.

- `retain` requires a live obligation.
- `retire` removes a dominated or dead construct.
- `collapse` merges duplicated representations.
- `delegate` restores the canonical owner.
- `replace` introduces the smallest new owner while retiring its predecessor.

## Semantic balance

Closure requires:

~~~text
unaccounted_hunks = []
uncovered_liabilities = []
required_retirements - completed_retirements = []
dominated_remaining = []
~~~

While `status=pending`, `dominated_remaining` must equal the exact outstanding
retirement debt. `clean` and `resolved` require that debt to be empty.

Every added construct names a live goal or domain obligation, its source
`obligation_ref`, and a displaced construct.
`local-repair` requires `added_constructs=[]`.

The resolution digest is the canonical digest of the artifact binding, source
finding set, change surfaces, review profile, decisions, and semantic balance.
CAS evidence used for closeout must carry that digest.

## Review contract

Select only `standard` for CAS evidence. Change surfaces remain part of the
review-contract fingerprint, but RF-v2 routing metadata cannot be relabeled as
producer-observed auxiliary execution. A new finding or code change updates the
resolution, changes its digest, and resets standard review credit.
