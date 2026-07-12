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
    policy_ref:
    policy_digest:
    review_contract_fingerprint: # equals the v2 aggregate review-contract manifest digest
    selected_lenses: [standard, footgun-finder, invariant-ace, complexity-mitigator, fresh-eyes]
    standard_required_clean_runs: 5
    standard_clean_attempt_ids: []
    auxiliary_requests:
      footgun-finder: selected-pending | clean | findings-folded | candidate-pressure | blocked | rerun-required
      invariant-ace: selected-pending | clean | findings-folded | candidate-pressure | blocked | rerun-required
      complexity-mitigator: selected-pending | clean | findings-folded | candidate-pressure | blocked | rerun-required
      fresh-eyes: selected-pending | clean | findings-folded | candidate-pressure | blocked | rerun-required
  decisions:
    - decision_id:
      owner_boundary:
      finding_ids: []
      liability_classes: [] # exactly one RF-v2 quotient_key
      strategy: local-repair | replacement-kernel | blocked
      correctness_refinement: # required unless strategy=blocked
        class_ref:
        discrepancy: excess | deficit | incoherence | partiality | misbinding
        law_delta:
        owner_refinement:
          kind: restore-existing-law | strengthen-representation | replace-owner
          construction:
        preservation_witness:
          statement:
          verifier: []
        progress_witness:
          kind: exclude | restore | reconcile | totalize | rebind
          statement:
          verifier: []
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

`change_surfaces` records judgment-derived surfaces. Resolution construction
must also include `multi-live-path` whenever the accepted-base diff contains
more than one path. Bind the resulting resolution digest into the next
GoalContract so it cannot be relabeled after kernel `open`.

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
dispositions and do not enter this object. Dangling fold IDs are insufficient:
resolution construction joins the current artifact and exact
`resolution-input` finding set to each decision. In `remediation-plan`, record
the strategy but omit `selected_work_node`; the plan grants no execution
authority. In review closeout, a pending multi-owner resolution may omit nodes
for non-current decisions. Re-fold the changed artifact before admitting the
next owner node; closure rejects `pending`.

Every accepted RF-v2 equivalence class containing a `resolution-input` finding
is consumed by exactly one resolution decision. Do not split one quotiented
cause into multiple comment-shaped decisions; if the quotient is wrong,
correct the RF-v2 classification first. Each decision binds exactly one
liability class; `correctness_refinement.class_ref` must be that same class.
Across fresh folds, the same quotient key remains one class and extends that
decision's finding set. A new quotient key requires a new decision.

Record rejected alternatives and a falsifier for every material decision.
Judgment owns the strategy; comment count does not.

## Correctness refinement

Treat each accepted RF-v2 equivalence class as a counterexample to an intended
law, not as a patch instruction. Invoke `$universalist` on that owner boundary
and materialize exactly one `correctness_refinement` before selecting mutation.
The refinement names:

- the quotiented counterexample class;
- the discrepancy between intended and observed behavior;
- the law restored or strengthened;
- the smallest owner construction that makes the law structural;
- a preservation witness with exact verifier argv for behavior that was already
  valid; and
- a progress witness with exact verifier argv that excludes or repairs the
  whole class.

The discrepancy fixes the progress operation:

~~~text
excess -> exclude
deficit -> restore
incoherence -> reconcile
partiality -> totalize
misbinding -> rebind
~~~

`local-repair` may only use `restore-existing-law`. Use
`replacement-kernel` for `strengthen-representation` or `replace-owner` when
the existing owner cannot make the law structural. This distinction limits
the incision: correctness must strictly improve, but the artifact need not
grow a new abstraction when its current owner already expresses the law.

Run the validator before review mutation and again at closeout:

~~~bash
ledger validate review-resolution \
  --phase preflight --input <resolution.json>
ledger validate review-resolution \
  --phase closeout --input <resolution.json>
~~~

This is a correctness-refinement sub-contract checker, not a complete validator
for every `review-resolution/v1` field. It checks the embedded RF-v2 class,
decision, witness argv, strategy, status, and semantic-balance joins. The
GoalContract and `$goal-actuating` still bind the current artifact, review
profile, resolution digest, selected node, abstraction account, and publication
evidence. They must execute and observe both witness commands against the
current artifact; the checker does not execute them or compare prior snapshots.

Bind both witness commands into the next GoalContract before mutation as
`correctness:<decision_id>:preservation` and
`correctness:<decision_id>:progress`. Their statements and argv must exactly
match the refinement. A passing decision proves structural consistency only;
it grants no authority or semantic truth. A `blocked` decision retains its
exact class and finding set, omits `correctness_refinement`, and necessarily
produces a blocked preflight.
Across adjacent repairs and reships, retain prior class bindings and witnesses.
A new finding extends the refinement set; it never erases prior progress.
`$goal-actuating` proves that cumulative relation from the bound resolution
history; the single-snapshot checker cannot.

At closeout, `clean` means the retained resolution-input and decision sets are
both empty. `resolved` means at least one retained resolution-input was
consumed. Preflight admits only `pending`; clean and resolved snapshots use
closeout. These statuses are not interchangeable labels.

## Live refresh and publication continuation

Refresh the live review source before every repair admission and construct new
RF-v2 folds for the current local artifact. A source name alone or only the
batch that authorized the preceding edit is stale input, even while the PR
intentionally continues to publish the preceding SHIP artifact.

For an adjacent same-publication repair, the pending resolution must preserve
all prior same-epoch finding IDs and source references, add at least one new
material finding, use fold IDs disjoint from every fold already admitted in the
epoch, include at least one new producer source-batch identity, and select the
current node. Every introduced finding must come from a new producer batch.
Open a new actuation-kernel generation whose GoalContract digest binds that cumulative
resolution and publication epoch; a caller-authored continuation token or use
count grants no authority.

Finding semantics and source-to-producer lineage remain cumulative across a
replacement SHIP. The new receipt resets publication-local fold/batch and CAS
current-request credit, not admitted liabilities. Standard clean credit may
cross that publication boundary only through the owning policy's certified
`auxiliary-remediation` carry; no auxiliary result survives. The next repair
resolution must strictly extend the retained finding set and preserve every
retained source backend.

The resolved re-fold after the last repair preserves exactly the admitted
finding set and every admitted source reference, and uses another fresh fold
plus a producer batch that carries material evidence. A newly observed material
finding keeps the resolution pending and requires another admitted
continuation. Only after the retained PR is revalidated against the
admission-bound published artifact may `$ship` update that PR to the resolved
local head. Earlier current-request and auxiliary credit belongs to the
preceding publication epoch and resets to zero. Earlier standard attempts keep
their original epoch and tuple; they contribute to the new trailing suffix only
when the v2 policy binds the intervening auxiliary-remediation carry and later
ends clean on the current tuple.

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
uncovered_liabilities = []
required_retirements - completed_retirements = []
dominated_remaining = []
~~~

`$review-fold` owns hunk and source identity. The actuation kernel independently
observes the exact prepared path state and derives path provenance from its
event chain. The resolution does not repeat a caller-authored hunk inventory.

While `status=pending`, `dominated_remaining` must equal the exact outstanding
retirement debt. `clean` and `resolved` require that debt to be empty.

Every declared added construct names a live goal or domain obligation, its
source `obligation_ref`, and a distinct displaced construct. This is a
declaration consistency check, not independent discovery of omitted
constructs.
`local-repair` requires `added_constructs=[]`.

The resolution digest is the canonical digest of the artifact binding, source
finding set, change surfaces, review profile, decisions, and semantic balance.
The owning `actuation-review-policy/v2` request binds that digest before CAS
execution.

## Review contract

Build the review profile from [review-policy.md](review-policy.md). Select every
registered auxiliary lens. RF-v2 routing obligations and changed surfaces
refine each lens's scope; they do not authorize omission. The policy artifact
binds every request to exact instruction bytes before CAS execution. CAS
returns only the opaque request binding and transport facts.

A post-run label cannot create auxiliary evidence. Credit requires an exact
join among the pre-bound policy request, its actuation event, the returned CAS
binding and tuple, and any RF-v2 fold. Accumulate every terminal result from
the launched wave and resolve every request-local `rerun-required` transport
failure before constructing or updating the resolution. A new finding
terminalizes its source request after RF-v2 classification; a verdictless
`review_failed` fact terminalizes only its dispatch and requires exact-request
same-tuple recovery. Neither fact cancels sibling requests or changes the
preflight-bound resolution digest. After the wave and resolution barriers,
bind the complete resolution to any selected repair.
The resulting code change invalidates the preceding tuple's current requests.
A standard finding or unrelated change resets the standard chain. An
auxiliary-only repair may preserve its existing clean projection solely through
the v2 carry that binds this resolution's class, witnesses, actuation evidence,
and publication receipt.
