# Actuating Terminal Closure Gate

## Purpose

ATCG-v1 decides whether the current actuation run may be marked complete. It does
not run review, edit files, create proof, publish PRs, or update goals.

It enforces this separation:

```text
local proof passed
!= proof-patch complete
!= ship handoff complete
!= actuation complete
```

## ATCG-v1

```yaml
actuation_terminal_decision:
  decision_version: ATCG-v1
  verdict: complete | continue | blocked
  can_mark_goal_complete: yes | no
  run_id:
  source: accepted_spec | direct_goal | review
  closure_candidate: proof-patch | ship-handoff | ship-complete | blocked
  next_owner: none | $cas | $proof-patch | $ship | $goal-grind | $goal-actuating | human
  blocked_reasons: []
  continue_reasons: []
  current_artifact_binding:
    repo:
    branch:
    head_sha:
    diff_fingerprint:
    dirty_state: clean | tracked-dirty | unknown
  required_receipts: []
```

## Handoff rule

Before `$actuating` or `$goal-actuating` may report completion or call
`update_goal complete`, ATCG-v1 must return:

```text
verdict = complete
can_mark_goal_complete = yes
```

Then run the allowance guard:

```bash
uv run python codex/skills/actuating/tools/actuation_terminal_gate.py \
  allow-complete \
  --decision .ledger/actuating/<run-id>/terminal-decision.json
```

Only `can_call_update_goal_complete: yes` permits `update_goal complete`.

## Inputs

ATCG-v1 consumes current receiver-owned evidence:

```text
current branch/head/diff binding
latest actuation_interlock decision for material ALSR/HYL runs
FUSION-v1 receipt or ALSR/HYL/HSR receipts
optional goal-focus frame state
local evidence-fold verdict and proof commands
proof-patch presence/currentness
CAS requirement, tuple, freshness, and standard clean-run count
workflow-owned review_profile auxiliary coverage and folded/blocker state
ADD-v1 delivery decision
ship result when publication is required
side-effect boundary evidence
final report field values
```

## Loop receipt checks

For material work, ATCG requires one of:

```text
valid FUSION-v1 receipt for one simple action
current positive actuation_interlock + current ALSR-v1 + HYL-v1 + terminal HSR-v1 chain
```

A raw boolean such as `direct_action_fused: yes` is not enough. A fused run must
prove the direct-action conditions:

```yaml
fusion_receipt:
  version: FUSION-v1
  one_legal_work_item: yes
  verifier_known: yes
  review_required: no
  parallelism: none
  public_side_effect: no
  repeated_class_or_branch_choice: no
  objective_bound: yes
  artifact_scope_bound: yes
  stop_condition_bound: yes
  proof_ref:
```

For an unfused material run, ATCG checks that ALSR/HYL are present/current and
that HSR step receipts bind unfold, action, fold, and continuation to the current
artifact. A material mutation with only `has_hsr: yes` is not enough; it must
carry unfold/action/fold evidence or a receipt reference.

## Goal-focus checks

When goal-focus mode is active, ATCG rejects completion unless:

```text
primary_goal_stable = yes
all child focus frames folded or blocked = yes
terminal focus matches parent stop rule = yes
child_claimed_parent_completion = no
latest focus fold is parent-bound = yes
```

These checks prevent a child frame or temporary focus from closing the parent goal.

## CAS lane closure rule

For review-closeout and exhaustive review, the terminal CAS count means:

```text
three clean normalized standard CAS review attempts
```

Only the `standard` CAS lane may increment the clean-run count. Auxiliary lanes
such as `footgun-finder`, `invariant-ace`, and `complexity-mitigator` may block
completion, but they do not count toward the three standard clean reviews.

Selected auxiliary lanes with `clean` or `findings-folded` state must carry the
lane contract expected by ATCG:

```text
footgun-finder       -> footgun-lens-v1
invariant-ace        -> invariant-gate-v1
complexity-mitigator -> complexity-preflight-v1
```

`lens_evidence_state` must be `valid` for terminal completion. `not-required` is
valid only for lanes explicitly not selected and still needs a reason.

## Common outcomes

```text
ALSR/HYL required + missing -> blocked-loop-contract-missing, next_owner=$goal-actuating
ALSR/HYL required + stale -> blocked-loop-contract-stale, next_owner=$goal-actuating
FUSION-v1 missing for fused claim -> blocked-loop-contract-missing, next_owner=$goal-actuating
material mutation without unfold/action evidence -> blocked-hylo-frontier-missing, next_owner=$goal-actuating
previous material action without fold evidence -> blocked-hylo-fold-missing, next_owner=$goal-actuating
completion without terminal HSR -> blocked-hylo-terminal-missing, next_owner=$goal-actuating
goal-focus frame not folded to parent -> blocked-hylo-fold-missing, next_owner=$goal-actuating
CAS required + standard clean runs < required -> blocked, next_owner=$cas
required auxiliary lane missing|not-folded|blocked|rerun-required|stale -> cas-review-blocked, next_owner=$cas
proof-patch required + missing/stale -> continue, next_owner=$proof-patch
ADD-v1 handoff + ship result missing -> continue, next_owner=$ship
public side effect outside $ship boundary -> side-effect-boundary-violated, next_owner=$ship
proof verifier mismatch or stale current-artifact binding -> proof-stale, next_owner=$goal-grind
all required receipts current -> complete
```

ATCG-v1 must not infer a missing receipt from final report prose, `update_plan`,
a PR body, or a proof summary. Those artifacts may reference evidence, but they
are not the evidence owner.

## Hard blocker names

```text
blocked-loop-contract-missing
blocked-loop-contract-stale
blocked-hylo-frontier-missing
blocked-hylo-fold-missing
blocked-hylo-terminal-missing
cas-review-blocked
proof-stale
side-effect-boundary-violated
```

Detailed reasons may accompany these names, but these canonical blockers are the
main terminal signal.

## Advisory validation

Advisory mode reports the same blockers without making a terminal decision.

```bash
uv run python codex/skills/actuating/tools/actuation_terminal_gate.py \
  validate \
  --context .ledger/actuating/<run-id>/terminal-context.json \
  --mode advisory \
  --format json
```

A would-block advisory result is evidence for the caller. It is not a terminal
stop condition by itself.

## Validator

```bash
uv run python codex/skills/actuating/tools/actuation_terminal_gate.py \
  decide \
  --context .ledger/actuating/<run-id>/terminal-context.json \
  --out .ledger/actuating/<run-id>/terminal-decision.json

uv run python codex/skills/actuating/tools/actuation_terminal_gate.py \
  check \
  --decision .ledger/actuating/<run-id>/terminal-decision.json

uv run python codex/skills/actuating/tools/actuation_terminal_gate.py \
  allow-complete \
  --decision .ledger/actuating/<run-id>/terminal-decision.json
```

## Falsifier

The gate is working when future reports show:

```text
local_proof_passed_but_goal_complete = 0
cas_required_with_zero_standard_clean_runs_complete = 0
auxiliary_review_lane_counted_as_standard_clean_run = 0
add_v1_handoff_without_ship_result_complete = 0
fused_run_without_FUSION_v1_complete = 0
material_run_without_HSR_chain_complete = 0
child_focus_claimed_parent_completion = 0
```
