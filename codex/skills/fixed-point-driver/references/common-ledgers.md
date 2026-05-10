# Common ledgers

Use ledger fields consistently across skills, specialist outputs, and closure handoffs.

## Canonical identifiers

- Keep stable IDs for findings, invariants, hazards, checks, passes, and negative-evidence entries when the same issue survives multiple loops.
- Stamp every meaningful pass with the current `artifact_state_label`.
- Stamp every specialist packet and negative-ledger pass with the current `artifact_state_id`.
- If a prior signal is no longer current, mark it stale, superseded, reopened, or accepted-risk rather than silently dropping it.
- Preserve rejected and stale specialist packets when they materially influenced routing or closure confidence.

## Packet-native specialist footer

Every specialist output should end with:
- `artifact_state_id`
- `artifact_state_label`
- `scope`
- `top_material_signals`
- `unresolved_signals`
- `agreement_pressure`: `aligned` | `mixed` | `conflicting` | `unknown`
- `stale`: `yes` | `no` | `unknown`
- one-line final call

Reject specialist output as `transport-invalid` when it contains raw transport wrappers, root-only response text such as `Echo:`, queued prompts, multiple packets, or no packet.

## Common ledger shapes

### Findings ledger

- `finding_id`
- `materiality`
- `severity`
- `category`
- `status`
- `evidence`
- `next_action`

### Soundness ledger

- `claim_id`
- `claim_or_obligation`
- `witness_required`
- `witness_status`
- `preservation`
- `progress`
- `inhabitance`
- `minimum_acceptable_fix`

### Invariant ledger

- `invariant_id`
- `name`
- `tier`
- `status`
- `confidence`
- `blast_radius`
- `supporting_evidence`

### Verification ledger

- `direct_changed_path`
- `claimed_failure_mechanism`
- `regression_surface`
- `checks_run`

### Companion Skill Ledger

Use this to make implicit stage behavior auditable.

- `companion`: `review-adjudication` | `accretive-implementer` | `adversarial-reviewer` | `verification-closure` | `negative-ledger` | `learnings`
- `status`:
  - `used`
  - `root-equivalent`
  - `not-needed`
  - `unavailable`
  - `queried`
  - `mapped`
  - `captured`
  - `handoff`
  - `no-applicable-evidence`
  - `recalled`
  - `not-material`
- `evidence`
- `limitations`

Status rules:
- `used` requires an invocation, output packet, or contract-shaped section.
- `root-equivalent` means root performed the doctrine without a distinct auditable skill invocation.
- `not-needed` requires a task-shape reason.
- `negative-ledger` does not use `root-equivalent`; use `queried`, `mapped`, `captured`, `handoff`, `no-applicable-evidence`, or `unavailable`.
- `learnings` should distinguish `recalled`, `captured`, `not-material`, and `unavailable`.

### Routing and Budget Ledger

Use this to make fanout calibration auditable.

- `task_shape`: `narrow-review-comment` | `review-batch` | `implementation` | `remediation` | `hardening` | `audit` | `optimization` | `migration` | `unknown`
- `fixed_point_lane`: `direct-closure` | `targeted` | `expanded-targeted` | `swarm`
- `subagent_mode`: `off` | `targeted` | `swarm`
- `specialist_budget_planned`
- `specialist_budget_actual`
- `budget_exceptions`
- `lane_change_history`

Lane budgets:
- `direct-closure`: 0 specialists
- `targeted`: 1-2 specialists
- `expanded-targeted`: 3-4 specialists
- `swarm`: 5+ specialists

The root-owned Negative Ledger Pass does not count against specialist budget. `negative-ledger-mapper` does count.

### Budget Exception Ledger

- `requested_extra_role`
- `current_lane`
- `current_specialist_count`
- `budget_limit`
- `distinct_uncertainty_class`
- `why_root_cannot_resolve_locally`
- `expected_decision_delta`: `route` | `finding` | `proof` | `risk-retirement` | `negative-evidence-frontier` | `none`
- `approved`

### Negative Ledger Pass

Use `$negative-ledger` for the full contract. The fixed-point driver must still record this pass shape:

- `phase`: `preflight` | `post-remediation` | `post-review` | `pre-closure` | `capture` | `handoff`
- `mode`: `query` | `map` | `capture` | `reopen` | `handoff` | `none`
- `artifact_state_id`
- `topical_query`
- `sources_checked`
  - `current_run`
  - `fixed_point_ledgers`
  - `learnings`
  - `repo_history`
  - `review_comments`
  - `user_context`
- `result`
  - `active_exclusions`
  - `stale_or_superseded`
  - `reopened_candidates`
  - `need_evidence`
  - `no_applicable_negative_evidence_reason`
  - `safest_next_frontier`
- `durable_capture`: `appended` | `duplicate-skip` | `not-material` | `unavailable` | `not-attempted`

A completed pass with no matching evidence records `no-applicable-negative-evidence`; it is not a skipped pass.

### Negative Evidence Ledger

Use `$negative-ledger` for the full contract. Minimal shared fields:

- `neg_id`
- `hypothesis`
- `attempted_change`
- `source_refs`
- `learning_source_ids` when sourced from `.learnings.jsonl` or `learnings recall/query`
- `evidence`
- `observed_outcome`
- `failure_class`: `no-effect` | `local-regression` | `global-regression` | `unsound` | `too-complex` | `stale` | `unknown`
- `applicability_conditions`
- `current_status`: `active` | `stale` | `superseded` | `reopened` | `unknown` | `need-evidence`
- `exclusion_rule`
- `reopening_criteria`
- `confidence`: `high` | `medium` | `low` | `unknown`
- `next_search_hint`

Negative evidence is active only when it has concrete evidence and current-state applicability. A `learnings` hit is a candidate source, not an exclusion rule by itself. Mark stale or superseded evidence explicitly; do not silently drop it.

### Negative Capture Decision

- `witnessed_event`: `failed-test` | `no-effect` | `benchmark-regression` | `revert` | `review-rejection` | `strategy-pivot` | `none`
- `hypothesis`
- `attempted_change`
- `evidence_anchor`
- `decision_shaping`: `yes` | `no`
- `transferable`: `yes` | `no`
- `counterfactual_value`: `yes` | `no`
- `capture`: `yes` | `no`
- `durable_writeback`: `append` | `duplicate-skip` | `not-material` | `unavailable` | `not-attempted`
- `reason`

### Negative Ledger Handoff

- `active_exclusions`
- `stale_or_superseded`
- `reopened`
- `need_evidence`
- `safest_next_frontier`
- `learnings_source_ids`
- `durable_capture`
- `closure_effect`
  - `blocks_closure`: `yes` | `no`
  - `changes_one_change_challenge`: `yes` | `no`
  - `changes_verification_plan`: `yes` | `no`

### Negative Evidence Closure Gate

- `status`: `satisfied` | `open` | `blocked` | `unavailable`
- `active_exclusions_count`
- `repeated_failed_route_used`: `yes` | `no`
- `reopening_criteria_satisfied`: `yes` | `no` | `n/a`
- `learnings_hits_applicability_checked`: `yes` | `no` | `n/a`
- `reason`

### Specialist Briefing Ledger

- `role`
- `artifact_state_id`
- `artifact_state_label`
- `scope`
- `top_material_signals`
- `unresolved_signals`
- `agreement_pressure`: `aligned` | `mixed` | `conflicting` | `unknown`
- `stale`: `yes` | `no` | `unknown`
- `packet_status`: `accepted` | `stale` | `transport-invalid` | `wrong-scope` | `timeout` | `superseded`
- `used_for`: `evidence mapping` | `negative-evidence pruning` | `soundness pressure` | `invariant pressure` | `hazard pressure` | `complexity pressure` | `verification planning` | `none`
- `rejection_reason`

### Specialist Value Receipt

- `role`
- `packet_status`
- `artifact_state_id_match`
- `scope_match`
- `uncertainty_class`: `evidence` | `soundness` | `invariant` | `hazard` | `complexity` | `verification` | `negative-evidence` | `other`
- `route_changed`
- `finding_added`
- `proof_changed`
- `risk_retired`
- `value`: `positive` | `neutral` | `negative`
- `used_for`
- `reason`

Classify value:
- `positive`: changed route, added a material finding, changed proof, or retired a plausible material risk
- `neutral`: valid packet with no material delta
- `negative`: stale, wrong-scope, transport-invalid, misleading, or avoidably duplicative packet

## State labels

Use stable, phase-aware labels such as:
- `loop-01-post-build`
- `loop-02-post-review`
- `targeted-validation-01`
- `closure-candidate-03`

Use state IDs that bind a packet to the current code shape, such as:
- `branch=feature/foo head=abc123 diff=changed-paths-sha phase=prepatch`
- `branch=feature/foo head=abc123 diff=changed-paths-sha phase=post-fixture-refresh`
