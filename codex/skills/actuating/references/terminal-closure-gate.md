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
  next_owner: none | $cas | $proof-patch | $ship | $goal-grind | human
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

Any other verdict keeps the actuation run active or reports the specific blocked
state. A local verifier pass, proof-complete graph, or ADD-v1
`handoff_to_ship` result is not enough by itself.

## Inputs

ATCG-v1 consumes current receiver-owned evidence:

```text
current branch/head/diff binding
evidence-fold verdict and proof commands
proof-patch presence/currentness
CAS requirement, tuple, freshness, and clean-run count
ADD-v1 delivery decision
ship result receipt when publication is required
final report field values
```

It does not run CAS, create proof-patch output, call `$ship`, publish PRs, or
mutate workspace state.

## Common outcomes

```text
CAS required + clean runs < required -> blocked, next_owner=$cas
CAS required + clean_runs_required <= 0 -> blocked, next_owner=$cas
CAS required + final report clean runs < required -> blocked, next_owner=$cas
proof-patch required + missing/stale -> continue, next_owner=$proof-patch
proof-patch closure + missing proof-patch receipt -> continue, next_owner=$proof-patch
ADD-v1 handoff + ship result missing -> continue, next_owner=$ship
ship-complete closure + missing delivery evidence -> blocked, next_owner=$ship
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

## Validator

```bash
uv run python codex/skills/actuating/tools/actuation_terminal_gate.py \
  decide \
  --context .ledger/actuating/<run-id>/terminal-context.json \
  --out .ledger/actuating/<run-id>/terminal-decision.json

uv run python codex/skills/actuating/tools/actuation_terminal_gate.py \
  check \
  --decision .ledger/actuating/<run-id>/terminal-decision.json
```

## Falsifier

The gate is working when future actuation reports show:

```text
local_proof_passed_but_goal_complete = 0
cas_required_with_zero_clean_runs_complete = 0
add_v1_handoff_without_ship_result_complete = 0
```
