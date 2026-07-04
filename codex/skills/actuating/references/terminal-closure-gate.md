# Actuating Terminal Closure Gate

## Purpose

ATCG-v1 prevents `$actuating` from treating local verification as terminal
completion when proof-patch, CAS review, delivery, or ship evidence is still
required.

The gate enforces this separation:

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
  source: accepted_spec | direct_goal | review | st_handoff
  closure_candidate: proof-patch | ship-handoff | ship-complete | blocked
  next_owner: none | $cas | $proof-patch | $ship | $goal-grind | $goal-actuating | $st | human
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

The local workflow must then run the completion allowance guard:

```bash
uv run python codex/skills/actuating/tools/actuation_terminal_gate.py \
  allow-complete \
  --decision .ledger/actuating/<run-id>/terminal-decision.json
```

The guard emits:

```yaml
actuation_completion_allowance:
  verdict: allowed | denied
  can_call_update_goal_complete: yes | no
  decision_verdict: complete | continue | blocked
  next_owner: none | $cas | $proof-patch | $ship | $goal-grind | $goal-actuating | $st | human
  blocked_reasons: []
  continue_reasons: []
```

Only `can_call_update_goal_complete: yes` permits `update_goal complete`.
Denied `continue` and `blocked` decisions are valid ATCG outputs, not malformed
gate results.

Any other verdict keeps the actuation run active or reports the specific blocked
state. A local verifier pass, proof-complete graph, or ADD-v1
`handoff_to_ship` result is not enough by itself.

## Inputs

ATCG-v1 consumes current receiver-owned evidence:

```text
current branch/head/diff binding
loop governance: ALSR-v1, HYL-v1, HSR-v1, or explicit fused/$st exemption
evidence-fold verdict and proof commands
proof-patch presence/currentness
CAS requirement, tuple, freshness, and standard clean-run count
auxiliary CAS review-lane folded/blocker state when selected
ADD-v1 delivery decision
ship result receipt when publication is required
side-effect boundary evidence
final report field values
```

It does not run CAS, create proof-patch output, call `$ship`, publish PRs, or
mutate workspace state.

## CAS lane closure rule

For review-closeout and exhaustive review, the terminal CAS count means:

```text
three clean normalized standard CAS review attempts
```

Only the `standard` CAS review lane may increment the clean-run count that ATCG
uses for terminal completion. Auxiliary CAS review lanes such as
`footgun-finder`, `invariant-ace`, and `complexity-mitigator` are review
evidence, but they do not count toward the three standard clean reviews and do
not interrupt standard-review consecutiveness.

Auxiliary lanes may still block completion. ATCG rejects completion when a
required auxiliary lane is missing, blocked, rerun-required, or not folded
through `$review-fold` / the resolution fold.

The preferred reducer fields are:

```text
cas_review.standard_clean_runs_required
cas_review.standard_clean_runs_count
final_report_fields.standard_clean_cas_runs
cas_review.required_auxiliary_lanes
cas_review.auxiliary_lanes.<lane>.folded
cas_review.auxiliary_lanes.<lane>.unresolved_blockers
cas_review.auxiliary_lanes.<lane>.rerun_required
cas_review.auxiliary_lanes.<lane>.head_sha
cas_review.auxiliary_lanes.<lane>.target_fingerprint
```

Compatibility fields may still be named `clean_runs_required`,
`clean_runs_count`, or `normalized_cas_clean_runs`, but their meaning is
standard-only unless a context provides explicit `standard_clean_*` fields.

## Common outcomes

```text
ALSR/HYL required + missing -> blocked-loop-contract-missing, next_owner=$goal-actuating
ALSR/HYL required + stale -> blocked-loop-contract-stale, next_owner=$goal-actuating
material mutation without unfold/action evidence -> blocked-hylo-frontier-missing, next_owner=$goal-actuating
previous material action without fold evidence -> blocked-hylo-fold-missing, next_owner=$goal-actuating
completion without terminal HSR -> blocked-hylo-terminal-missing, next_owner=$goal-actuating
$st-governed completion without current $st control receipt -> st-authority-blocked, next_owner=$st
CAS required + standard clean runs < required -> blocked, next_owner=$cas
CAS required + standard_clean_runs_required <= 0 -> blocked, next_owner=$cas
CAS required + final report standard clean runs < required -> blocked, next_owner=$cas
required auxiliary CAS review lane missing|not-folded|blocked|rerun-required -> cas-review-blocked, next_owner=$cas
required auxiliary CAS review lane stale against head/diff -> cas-review-blocked, next_owner=$cas
review-closeout protocol incomplete -> cas-review-blocked, next_owner=$cas
proof-patch required + missing/stale -> continue, next_owner=$proof-patch
proof-patch closure + missing proof-patch receipt -> continue, next_owner=$proof-patch
ADD-v1 handoff + ship result missing -> continue, next_owner=$ship
ship-complete closure + missing delivery evidence -> blocked, next_owner=$ship
public side effect outside $ship boundary -> side-effect-boundary-violated, next_owner=$ship
proof verifier mismatch or stale current-artifact binding -> proof-stale, next_owner=$goal-grind
ship-complete closure + missing ADD-v1 or ship receipt -> invalid decision
wrapped ADD-v1 delivery decision -> accepted as delivery evidence
ADD-shaped handoff without decision_version=ADD-v1 -> blocked
partial ADD-v1 handoff without proof/integration receipts -> blocked
ADD-v1 target_head or ship_input.head_sha mismatches current artifact -> blocked
complete + closure_candidate=ship-handoff|blocked -> invalid decision
artifact binding missing/stale -> blocked, next_owner=$goal-grind
continue|blocked + next_owner=none -> invalid decision
evidence-fold refactor-kernel -> continue, next_owner=$goal-grind
all required receipts current -> complete
tracked-dirty artifact + current proof-patch receipt -> may complete
tracked-dirty artifact without proof-patch receipt -> blocked
```

## Hard blocker names

ATCG-v1 hard decisions use these canonical blocker names:

```text
blocked-loop-contract-missing
blocked-loop-contract-stale
blocked-hylo-frontier-missing
blocked-hylo-fold-missing
blocked-hylo-terminal-missing
cas-review-blocked
st-authority-blocked
proof-stale
side-effect-boundary-violated
```

Detailed legacy reasons may accompany canonical blockers for compatibility, but
canonical blockers are the terminal governance signal.

## Advisory validation

Advisory mode reports the same ATCG-v1 completion blockers without enforcing
them. A would-block advisory result is evidence for the caller, not a terminal
stop condition by itself.

```json
{
  "verdict": "advisory",
  "would_block": true,
  "would_block_reasons": [
    "blocked-hylo-terminal-missing"
  ],
  "can_mark_goal_complete": false,
  "next_owner": "$goal-actuating"
}
```

Advisory mode checks loop governance and terminal proof state in the same
required-check order used by `$actuating`:

```text
ALSR exists when required
ALSR current against branch/head/diff
HYL exists when recursive/material
terminal HSR exists
every material mutation has HSR unfold/action/fold
latest fold is current-artifact-bound
selected loop matches task shape
review-closeout obeyed CAS/review-fold/resolution-fold
three clean normalized standard CAS attempts complete when required
required auxiliary CAS review lanes folded or not-required
side-effect boundary respected
proof matches verifier
```

Direct-action fused and `$st`-governed runs may exempt ALSR/HYL/HSR receipt
checks only when the context explicitly carries the exemption. `$st`-governed
completion additionally requires current `$st` control evidence; `source:
st_handoff` alone is not sufficient. Advisory would-block results exit
successfully; malformed input or unsupported mode/format remains a CLI failure.

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

uv run python codex/skills/actuating/tools/actuation_terminal_gate.py \
  validate \
  --context .ledger/actuating/<run-id>/terminal-context.json \
  --mode advisory \
  --format json
```

## Falsifier

The gate is working when future actuation reports show:

```text
local_proof_passed_but_goal_complete = 0
cas_required_with_zero_standard_clean_runs_complete = 0
auxiliary_review_lane_counted_as_standard_clean_run = 0
add_v1_handoff_without_ship_result_complete = 0
```
