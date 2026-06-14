---
name: resolve
description: "Resolve the current branch through a CAS-first, receipt-backed review loop with native review as recorded fallback only. Use for `$resolve`, branch resolution, review/fix/validate/commit/push loops, PR comment sweep, three consecutive clean reviews, route-wave artifact publication, review_compression_packet and review_distillation_packet enforcement, negative-ledger route memory, NREC-v1 negative route exclusion cards, universalist_check enforcement/falsification, RCP/RDP/RRW/NREC gates, review-lab/delivery distillation, dirty-tree slice commits, CAS review lanes, full review-adjudication route consumption, surface-budgeted fixed-point fixes, and final pushed readiness. Do not use for one-shot review, PR creation only, merging/landing, isolated adjudication, or final closure proof without branch mutation."
---

# resolve

## Purpose

Resolve the current branch to a pinned-review-clean, validated, committed, pushed, and PR-comment-swept state without delivering the accumulated review loop.

## Core doctrine

```text
Review findings are counterexamples, not tasks.
Do not deliver the review loop.
The lab learns; the delivery branch forgets.
Repeated review decisions are falsified hypotheses.
No route-wave artifact, no closure.
No required packet, no review-driven production patch.
No negative-ledger pass after repeated route failure, no repeated route.
No active negative exclusion may be violated unless reopened, stale, superseded, or explicitly accepted.
No universalist_check, no hot-cluster production patch.
Green slice, then checkpoint commit.
```

## Completion bar

```text
3 consecutive clean reviews
+ pinned backend/base/head/fingerprint
+ full validation pass
+ intended commit/push
+ complete post-push PR sweep
+ no unprocessed in-scope PR comments
+ no actionable PR comments remaining
+ route-wave artifacts published for review waves
+ no missing RCP/RDP/NREC packet where required
+ no missing negative evidence pass where required
+ no active negative exclusion against selected route
+ no missing universalist_check where required
+ no unresolved falsification
+ no unpaid abstraction rent
+ no lab scar tissue delivered without rent
```

## Entry guard

Before any review command or patch runs, load enough of this skill to include:

- Backend selection
- Review adjudication route consumption
- Route-wave artifact publication
- RCP/RDP/NREC gates
- Negative-ledger route memory and route ratchet
- Universalist check enforcement and falsification
- Review Distillation Mode
- Slice commit cadence
- Fixed-point and implementation handoff
- Non-negotiables

## Backend selection

`$resolve` is CAS-first. Native review is fallback-only after recorded CAS failure or explicit user request. Do not run naked `codex review --base main`.

Review results must pin backend class, base ref/SHA, `HEAD` SHA, and target fingerprint when available.

## Route-wave artifact publication

For every review wave with findings or any route/RCP/RDP/NREC/negative-ledger/universalist decision, publish a first-class artifact.

Preferred path:

```text
.step/proof/resolve/<resolve-run-id>/review-wave-<n>.route.yml
```

Minimum shape:

```yaml
resolve_review_wave_packet:
  packet_version: RRW-v1
  resolve_run_id:
  artifact_state_id:
    branch:
    base_sha:
    head_sha:
    target_fingerprint:
  review_wave:
    backend:
    receipt_id:
    finding_ids: []
  route_receipts: []
  rcp_packets: []
  rdp_packets: []
  negative_evidence:
    pass_status: pass | fail | not-required
    active_exclusions: []
    captured_failures: []
    reopened_entries: []
    durable_writeback:
      status: appended | duplicate-skip | not-attempted | unavailable
      ids: []
  negative_route_exclusion_cards:
    - card_id:
      excluded_route:
      active_against_selected_route: yes | no
      status: active | stale | superseded | reopened | unknown
  universalist_checks: []
  falsification_rules: []
  gate:
    route_receipts_complete: pass | fail
    negative_evidence_complete: pass | fail | not-required
    negative_route_gate: pass | fail | not-required
    rcp_required_packets_present: pass | fail | not-required
    distillation_required_packets_present: pass | fail | not-required
    universalist_checks_complete: pass | fail | not-required
    rent_paid_or_not_applicable: pass | fail | not-required
    implementation_handoff_allowed: yes | no
```

After writing or updating the artifact, emit:

```text
Resolve route artifact: <path>; gate=<pass|fail>; packet=<RCP|RDP|not-required>; negative=<pass|fail|not-required>; nrec=<active|none|reopened|blocked>; universalist=<use-universalist|not-needed|blocked>; route=<selected-route>; next=<action>
```

If a route/RCP/RDP/NREC/negative-ledger/universalist decision is not in a route-wave artifact or final visible `Resolve route artifact:` line, it does not count for closure.

## Review loop

Repeat until `clean_review_streak == 3`:

1. Run selected review driver.
2. If clean, verify pins and increment streak.
3. If findings/comments appear:
   - reset streak;
   - adjudicate every in-scope item through `$review-adjudication`;
   - update cluster and prior-decision state;
   - decide whether RCP or RDP is required;
   - run `$negative-ledger` query/map when route repetition or falsification is present;
   - emit NREC cards for falsified routes or active route exclusions;
   - emit or obtain required packet;
   - reject prose-only normal-form reasoning;
   - reject hot-cluster packets without `universalist_check`;
   - apply falsification rules for prior routes and prior `universalist not-needed`;
   - publish/update route-wave artifact;
   - route accepted packet to `$fixed-point-driver`;
   - run targeted proof;
   - if local proof is green and the slice is coherent, checkpoint commit before another long review cycle.

## Packet gates

Every mutation-capable review item must create a route receipt:

```yaml
resolve_route_receipt:
  receipt_version: RR-v6
  review_item_id: "..."
  artifact_state_id: "..."
  adjudication_route: "..."
  mutation_capable: yes
  rcp_required: yes | no
  rdp_required: yes | no
  nrec_required: yes | no
  packet_id: "RCP-... | RDP-..."
  negative_ledger_required: yes | no
  universalist_check_required: yes | no
  prior_route_falsified: yes | no
  prior_universalist_not_needed_falsified: yes | no
  active_negative_exclusion_match: yes | no
  bypass_reason: "isolated existing-owner no-new-surface direct proof" # only when packet_required=no
  selected_route: no-change | validate-only | delete-collapse-canonicalize | refactor-existing-owner | mutate-existing-owner | add-new-surface | distill-from-lab | blocked
  proof_required: []
```

`rcp_required: yes` when any are true:

- same cluster has two or more findings;
- same cluster reappears after a fix;
- existing-owner repair was already attempted in the cluster;
- prior route or universalist not-needed was falsified;
- route would add production surface;
- route would add helper/wrapper/adapter/fallback/flag/branch/state variant/public symbol/compatibility path;
- boundary/protocol/state-machine shape is suspicious;
- review findings are repeatedly selecting `address`;
- surface delta would be `larger-with-warrant` or `larger-without-warrant`.

`rdp_required: yes` when any are true:

- dirty tree contains multiple review-driven repairs;
- CAS keeps finding adjacent issues after green local proof;
- exploratory repair history exists and should not be delivered;
- repeated same-cluster local repairs are becoming the branch history;
- route would transplant lab/helper/fallback/compatibility surface into delivery branch.

`negative_ledger_required: yes` when any are true:

- same cluster reappears after repair;
- prior selected route is falsified;
- prior universalist not-needed is falsified;
- add-surface route failed or became unsound;
- public bypass / compatibility / tolerance path was introduced then rejected;
- one-change candidate resembles a prior failed route;
- Review Distillation Mode is active.

`nrec_required: yes` when any are true:

- `negative_ledger_required: yes` and there is a falsified route;
- active negative evidence excludes a route family;
- same route is proposed after same-cluster recurrence;
- durable writeback is not appropriate but route-wave exclusion is needed.

If a required packet, negative-ledger pass, or NREC is missing, do not mutate.

## Negative-ledger route memory

Before repeating any route in a hot cluster, run a root-owned negative-ledger query/map pass or use `negative_ledger_mapper` / `negative_evidence_route_auditor` when evidence is spread across route waves, RCP/RDP packets, CAS receipts, commits, PR comments, lab history, and learnings.

Every falsified route creates a negative route exclusion candidate:

```yaml
negative_capture_candidate:
  hypothesis: "..."
  attempted_change_or_decision: "..."
  observed_outcome: "same-cluster counterexample reappeared"
  failure_class: no-effect | local-regression | global-regression | unsound | too-complex | stale | unknown
  exclusion_rule: "..."
  reopening_criteria: []
```

Before implementation handoff, emit:

```yaml
negative_route_gate:
  prior_route_checked: yes | no
  active_exclusion_match: yes | no
  if_match:
    neg_id: "..."
    selected_route: "..."
    exclusion_rule: "..."
    status: reopened | superseded | stale | blocked
  handoff_allowed: yes | no
```

If `active_exclusion_match: yes` and the status is not reopened/superseded/stale, implementation is blocked.

## Universalist check enforcement and falsification

If packet says `universalist_check.decision: use-universalist`, obtain `$universalist` output or a root-equivalent `universal_boundary_packet` before mutation.

If decision is `blocked`, stop before mutation.

If decision is `not-needed`, record the reason and falsification rule in the route-wave artifact.

If the same cluster reappears after a `not-needed` decision, the next packet cannot keep `not-needed` unless a universal boundary packet explicitly proves the boundary artifact is still unnecessary.

## Review Distillation Mode

When `rdp_required: yes`, freeze the delivery branch and treat further exploratory repair as review-lab evidence.

Policy:

1. Freeze delivery base: branch, head SHA, base SHA, diff digest, proof state.
2. Use or create a disposable review lab branch/worktree outside final delivery.
3. Lift lab findings and repairs into counterexamples and scar-tissue entries.
4. Emit `review_distillation_packet`.
5. Rebuild selected normal form from delivery base.
6. Do not cherry-pick lab commits by default.
7. Prove delivery branch covers lab counterexamples.
8. Discard or retain lab only as evidence.

No RDP, no delivery patch when distillation is required.

## Negative evidence compaction and writeback

When three or more same-family exclusions appear, compact them into a route-family NREC.

Durable writeback to `.learnings.jsonl` is reserved for decision-shaping, transferable, counterfactually useful evidence. One-off route failures stay in route-wave artifacts.

## Slice commit cadence

After an accepted RCP/RDP or coherent review-addressed slice:

1. apply selected normal form through `$fixed-point-driver` / `$accretive-implementer`;
2. run targeted proof;
3. inspect diff and surface delta;
4. update route-wave artifact;
5. create a local checkpoint commit before another long CAS review cycle unless the slice is tiny and final clean review is immediate.

Do not checkpoint when unrelated changes are present, proof failed, packet is blocked, negative evidence blocks the route, rent is unpaid, universalist_check is blocked, route-wave gate fails, or surface delta is `larger-without-warrant`.

## Fixed-point and implementation handoff

Pass to `$fixed-point-driver`:

```yaml
implementation_handoff:
  source_skill: resolve
  target_skill: fixed-point-driver
  artifact_state_id: "..."
  review_item_id: "..."
  packet_id: "RCP-... | RDP-..."
  route_wave_ref: "..."
  selected_normal_form:
    kind: "..."
    owner: "..."
  negative_evidence:
    active_exclusions: []
    negative_route_exclusion_cards: []
    reopened_entries: []
    capture_required: []
    negative_route_gate:
      active_exclusion_match: yes | no
      handoff_allowed: yes | no
  universalist_check:
    decision: use-universalist | not-needed | blocked
    boundary_packet_ref: "..."
    prior_not_needed_falsified: yes | no
  permitted_action: mutate-code | add-validation-only | resolve-thread | draft-reply | defer | none
  permitted_scope: []
  forbidden_actions: []
  surface_budget:
    production_surface: zero_or_negative | bounded_positive | explicit_expansion
    added_helpers_allowed: yes | no
    added_wrappers_adapters_allowed: yes | no
    added_flags_or_fallbacks_allowed: yes | no
    public_symbols_allowed: yes | no
    compatibility_paths_allowed: yes | no
  abstraction_rent_status: paid | unpaid | not-applicable
  proof_required: []
  stale_if: []
```

Do not hand off mutation with active negative exclusion, unpaid rent, blocked universalist_check, unresolved falsification, missing route-wave artifact, or missing proof matrix.

## Final report

End with:

```text
Resolve Bottom Line:
- status: resolved | blocked | partial
- review_backend/base/head:
- clean_review_streak:
- route_wave_artifacts:
- packets: rcp_accepted=N, rdp_accepted=N, blocked=N, missing=N
- negative_evidence: active=N, captured=N, reopened=N, compacted=N, blocked=N
- negative_route_cards: active=N, reopened=N, stale=N, superseded=N
- universalist_checks: use=N, not_needed=N, blocked=N, missing=N, falsified=N
- abstraction_rent: paid=N, unpaid=N, not_applicable=N
- distillation: used=yes/no, lab_discarded_or_retained:
- checkpoint_commits:
- surface_delta_call:
- validation:
- PR sweep:
- open blocker:
- exact next action:
```

## Non-negotiables

- CAS-first; native review fallback-only.
- Three clean pinned review runs required.
- Review comments are not tasks.
- Do not deliver the review loop.
- No route-wave artifact, no closure.
- No required RCP/RDP/NREC, no review-driven production patch.
- No repeated route after falsification without negative-ledger map/reopen/block.
- No active negative exclusion may be violated by selected normal form unless reopened/stale/superseded or explicitly accepted.
- No hot-cluster production patch without `universalist_check`.
- Add-new-surface requires paid abstraction rent and universalist_check.
- Review-lab commits are not delivery commits.
- Do not route mutation to `$fixed-point-driver` without selected normal form, route-wave ref, negative-evidence status, NREC status, universalist decision, surface budget, rent status, and proof.
- Do not claim resolved with failed validation, missing route-wave artifact, missing packet, missing negative-ledger pass, active negative exclusion against selected route, unpaid rent, incomplete PR sweep, or stale review tuple.

## Resources

- [route-wave-artifact.md](references/route-wave-artifact.md)
- [review-compression-compiler-integration.md](references/review-compression-compiler-integration.md)
- [review-distillation-mode.md](references/review-distillation-mode.md)
- [negative-ledger-integration.md](references/negative-ledger-integration.md)
- [negative-route-exclusion-card.md](references/negative-route-exclusion-card.md)
- [universalist-check.md](references/universalist-check.md)
- [falsification-rules.md](references/falsification-rules.md)
- [gates.md](references/gates.md)
- [slice-commit-cadence.md](references/slice-commit-cadence.md)
- [implementation-handoff.md](references/implementation-handoff.md)
- [surface-delta-reporting.md](references/surface-delta-reporting.md)
