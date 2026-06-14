---
name: resolve
description: "Resolve the current branch through a CAS-first, receipt-backed review loop with native review as recorded fallback only. Use for `$resolve`, branch resolution, review/fix/validate/commit/push loops, PR comment sweep, three consecutive clean reviews, route-wave artifact publication, review_compression_packet enforcement, universalist_check enforcement/falsification, RCP-v1/RRW-v1 gates, dirty-tree slice commits, CAS review lanes, full review-adjudication route consumption, surface-budgeted fixed-point fixes, and final pushed readiness. Do not use for one-shot review, PR creation only, merging/landing, isolated adjudication, or final closure proof without branch mutation."
---

# resolve

## Purpose

Resolve the current branch to a pinned-review-clean, validated, committed, pushed, and PR-comment-swept state without letting review findings accumulate unbounded code.

## Core doctrine

```text
Review findings are counterexamples, not tasks.
No route-wave artifact, no closure.
No packet, no review-driven production patch when RCP is required.
No universalist_check, no hot-cluster production patch.
If same cluster reappears, prior universalist not-needed is falsified.
Green slice, then checkpoint commit; do not drag a huge dirty tree through repeated reviews.
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
+ no missing RCP packet where required
+ no missing universalist_check where required
+ no falsified universalist not-needed left unresolved
+ no unpaid abstraction rent
```

## Entry guard

Before any review command or patch runs, load enough of this skill to include:

- Backend selection
- Review adjudication route consumption
- Route-wave artifact publication
- RCP gate
- Universalist check enforcement and falsification
- Slice commit cadence
- Fixed-point and implementation handoff
- Non-negotiables

## Backend selection

`$resolve` is CAS-first. Native review is fallback-only after recorded CAS failure or explicit user request. Do not run naked `codex review --base main`.

Review results must pin backend class, base ref/SHA, `HEAD` SHA, and target fingerprint when available.

## Route-wave artifact publication

For every review wave with findings or any route/RCP/universalist decision, publish a first-class artifact.

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
  route_receipts:
    - review_item_id:
      adjudication_route:
      rcp_required: yes | no
      rcp_packet_id:
      universalist_check_required: yes | no
      universalist_decision: use-universalist | not-needed | blocked
      selected_route:
      proof_required: []
  rcp_packets:
    - packet_id:
      packet_status:
      selected_normal_form:
      abstraction_rent_status:
      proof_matrix_summary:
      commit_boundary:
  universalist_checks:
    - packet_id:
      decision:
      boundary_packet_ref:
      prior_not_needed_falsified: yes | no
  falsification_rules:
    - cluster_id:
      if_same_cluster_reappears:
      prior_decision_invalidated:
      next_required_action:
  gate:
    route_receipts_complete: pass | fail
    rcp_required_packets_present: pass | fail | not-required
    universalist_checks_complete: pass | fail | not-required
    rent_paid_or_not_applicable: pass | fail | not-required
    implementation_handoff_allowed: yes | no
```

After writing or updating the artifact, emit a visible line:

```text
Resolve route artifact: <path>; gate=<pass|fail>; rcp=<accepted|blocked|not-required>; universalist=<use-universalist|not-needed|blocked>; route=<selected-route>; next=<action>
```

If a route/RCP/universalist decision is not in a route-wave artifact or final visible `Resolve route artifact:` line, it does not count for closure.

When possible, validate:

```bash
python codex/skills/review-compression-compiler/tools/route_wave_gate.py <route-wave-file>
```

## Review loop

Repeat until `clean_review_streak == 3`:

1. Run selected review driver.
2. If clean, verify pins and increment streak.
3. If findings/comments appear:
   - reset streak;
   - adjudicate every in-scope item through `$review-adjudication`;
   - decide whether RCP is required;
   - if RCP required, emit or obtain `review_compression_packet`;
   - reject prose-only normal-form reasoning;
   - reject hot-cluster packets without `universalist_check`;
   - apply falsification rule for prior `universalist_check.decision: not-needed`;
   - publish/update route-wave artifact;
   - route accepted packet to `$fixed-point-driver`;
   - run targeted proof;
   - if local proof is green and the slice is coherent, checkpoint commit before another long review cycle.

## Review adjudication route consumption

Do not collapse everything to `address`.

| adjudication route | `$resolve` handling |
|---|---|
| `address` / `mutate-code` | route receipt, RCP gate if triggered, route-wave artifact, then `$fixed-point-driver` |
| `delete-collapse-canonicalize` | RCP/fixed-point with ablation preferred |
| `validate-only` | proof only; reset streak if files change |
| `resolve-thread-only` | reply/resolve only if provider policy permits |
| `do-not-address` | record rationale; review run still not clean |
| `blocked` | stop before commit/push |

## RCP gate

Every mutation-capable review item must create a route receipt:

```yaml
resolve_route_receipt:
  receipt_version: RR-v4
  review_item_id: "..."
  artifact_state_id: "..."
  adjudication_route: "..."
  mutation_capable: yes
  rcp_required: yes | no
  rcp_packet_id: "RCP-..." # required when rcp_required=yes
  universalist_check_required: yes | no
  prior_universalist_not_needed_falsified: yes | no
  bypass_reason: "isolated existing-owner no-new-surface direct proof" # only when rcp_required=no
  selected_route: no-change | validate-only | delete-collapse-canonicalize | refactor-existing-owner | mutate-existing-owner | add-new-surface | blocked
  proof_required: []
```

`rcp_required: yes` when any are true:

- same cluster has two or more findings;
- same cluster reappears after a fix;
- an existing-owner repair was already attempted in the cluster;
- prior universalist not-needed was falsified;
- route would add production surface;
- route would add helper/wrapper/adapter/fallback/flag/branch/state variant/public symbol/compatibility path;
- boundary/protocol/state-machine shape is suspicious;
- review findings are repeatedly selecting `address`;
- dirty tree contains multiple review-driven repairs;
- surface delta would be `larger-with-warrant` or `larger-without-warrant`.

`universalist_check_required: yes` when any are true:

- same cluster has two or more findings;
- existing-owner repair already attempted in cluster;
- same cluster reappeared after a selected normal form;
- prior universalist not-needed was falsified;
- route would add public surface, fallback, compatibility path, parser tolerance, state variant, or abstraction;
- a missing boundary artifact, duplicated projection, protocol/state-machine gap, generated provenance gap, public-contract/internal mismatch, or effect/callback IR gap is plausible.

If `rcp_required: yes`, no production patch may occur until an accepted `review_compression_packet` exists.

If `universalist_check_required: yes`, the packet must include `universalist_check.considered: yes`.

## Required review_compression_packet

When required, the packet must contain the literal keys:

```yaml
review_compression_packet:
universalist_check:
falsification:
route_wave_ref:
```

For packet files, run when possible:

```bash
python codex/skills/review-compression-compiler/tools/rcp_gate.py <packet-file>
```

A failed gate blocks mutation.

## Universalist check enforcement and falsification

If RCP says:

```yaml
universalist_check:
  decision: use-universalist
```

then `$resolve` must obtain `$universalist` output or a root-equivalent `universal_boundary_packet` before mutation.

If decision is `blocked`, stop before mutation.

If decision is `not-needed`, record the reason and the falsification rule in the route-wave artifact.

If the same cluster reappears after a `not-needed` decision:

```yaml
prior_universalist_not_needed_falsified: yes
```

The next packet cannot keep `universalist_check.decision: not-needed` unless a universal boundary packet explicitly proves the boundary artifact is still unnecessary. Otherwise route to `use-universalist` or `blocked`.

## Slice commit cadence

After an accepted RCP or coherent review-addressed slice:

1. apply the selected normal form through `$fixed-point-driver` / `$accretive-implementer`;
2. run targeted proof;
3. inspect diff and surface delta;
4. update the route-wave artifact;
5. create a local checkpoint commit before another long CAS review cycle unless the slice is tiny and final clean review is immediate.

Checkpoint commits are not final closure. They create stable tuples for CAS review and keep review-driven accumulation from becoming one giant dirty tree.

Do not checkpoint when unrelated changes are present, proof failed, RCP is blocked, rent is unpaid, universalist_check is blocked, route-wave gate fails, or surface delta is `larger-without-warrant`.

## Fixed-point and implementation handoff

Pass to `$fixed-point-driver`:

```yaml
implementation_handoff:
  source_skill: resolve
  target_skill: fixed-point-driver
  artifact_state_id: "..."
  review_item_id: "..."
  rcp_packet_id: "..."
  route_wave_ref: "..."
  selected_normal_form:
    kind: "..."
    owner: "..."
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

Do not hand off mutation with unpaid rent, blocked universalist_check, falsified unresolved not-needed, missing route-wave artifact, or missing proof matrix.

## Surface delta reporting

For any changed slice:

```yaml
surface_delta_summary:
  production_insertions:
  production_deletions:
  production_net:
  test_insertions:
  test_deletions:
  test_net:
  helpers_wrappers_adapters_added:
  public_symbols_added:
  flags_fallbacks_compat_paths_added:
  duplicate_or_shadow_surfaces_retired:
  surface_delta_call: smaller | same | larger-with-warrant | larger-without-warrant | unknown
```

`larger-without-warrant` blocks resolved completion unless revised, warranted, or explicitly accepted.

## Validation and PR sweep

After three clean reviews, run full validation. If validation fails, route contested actionability through adjudication and run RCP gate when mutation or surface growth may result.

After push, sweep PR comments/threads. PR items follow the same adjudication -> RCP gate -> universalist_check when required -> route-wave artifact -> fixed-point flow.

## Final report

End with:

```text
Resolve Bottom Line:
- status: resolved | blocked | partial
- review_backend/base/head:
- clean_review_streak:
- route_wave_artifacts:
- rcp_packets: accepted=N, blocked=N, not_required=N, missing=N
- universalist_checks: use=N, not_needed=N, blocked=N, missing=N, falsified=N
- abstraction_rent: paid=N, unpaid=N, not_applicable=N
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
- No route-wave artifact, no closure.
- No packet, no review-driven production patch when RCP is required.
- No hot-cluster production patch without `universalist_check`.
- A same-cluster recurrence falsifies prior `universalist_check.decision: not-needed`.
- `add-new-surface` requires paid abstraction rent and universalist_check.
- Do not route mutation to `$fixed-point-driver` without selected normal form, route-wave ref, universalist decision, surface budget, forbidden actions, rent status, and proof.
- Do not claim resolved with failed validation, missing route-wave artifact, missing RCP, missing required universalist_check, unresolved falsification, unpaid rent, incomplete PR sweep, or stale review tuple.

## Resources

- [route-wave-artifact.md](references/route-wave-artifact.md)
- [review-compression-compiler-integration.md](references/review-compression-compiler-integration.md)
- [universalist-check.md](references/universalist-check.md)
- [falsification-rules.md](references/falsification-rules.md)
- [rcp-gate.md](references/rcp-gate.md)
- [slice-commit-cadence.md](references/slice-commit-cadence.md)
- [implementation-handoff.md](references/implementation-handoff.md)
- [surface-delta-reporting.md](references/surface-delta-reporting.md)
