---
name: shadow
description: "Watch exactly one Codex session through one target-skill lens and emit only decision-relevant deltas. Prefer `seq skill-decision-audit --mode delta` for `$shadow $tune`; use for shadow/tail/follow/monitor one session, missed or contrary skill decisions, validation/outcome changes, worker decisions, or goal-cycle status. Do not scan broad history, inspect raw JSONL, create a second continual controller, or repeat full analysis when the cursor contains no new decision evidence."
---

# Shadow

## Mission

`$shadow` is a one-session decision-delta filter.

```text
No decision-relevant delta, no full report.
```

`/goal` owns continuation.

`$shadow` owns one current-cycle decision.

## Required inputs

```text
watched session id or path
target skill
mode: observe | propose | apply
watch objective
include workers: yes | no
prior cursor
```

Default:

```text
mode = propose
include workers = no
```

Do not default the target skill to `$tune`.

## Self-shadow guard

Bare:

```text
$shadow $tune
```

with no distinct watched session or target concern is partial activation.

Emit one compact stop record.

Do not recursively shadow the current session.

## Evidence source

Monitor the watched session only through `$seq`.

Preferred when target lens is `$tune` or when decision influence matters:

```bash
seq skill-decision-audit \
  --root ~/.codex/sessions \
  --session-id <session> \
  --skill <target> \
  --since-cursor '<cursor>' \
  --include-workers=<yes|no> \
  --mode delta \
  --format json
```

Fallback when the installed CLI lacks the command:

```text
skill-evidence
session-detail
turns
tool-lifecycle
session-prompts
session-graph
```

Use the smallest set required.

Do not inspect raw watched-session JSONL with shell, Python, `jq`, `rg`, `cat`, or `tail`.

If `$seq` cannot expose the required fact:

```text
tooling_gap
seq_tuning_gap
state_unknown
```

and produce a special-spec handoff when concrete.

## Target skill contract

Read the target skill package outside the watched session evidence boundary:

```text
SKILL.md
agents/openai.yaml
references/decision-contract.yaml
relevant references/scripts
```

If SKDC-v1 exists, preserve clause IDs.

If absent, use only a provisional contract and label it inferred.

## Productive-cycle gate

A full report is allowed only when at least one is new:

```text
target-skill activation evidence
decision episode
clause compliance/violation
validation failure
user feedback
worker decision
outcome reversal/reopen
watched session state change
prior finding falsified/resolved
explicit full-analysis request
```

Otherwise emit:

```yaml
goal_skill_delta_record:
  record_version: GSD-v2
  cycle_result: status_only_stop
  evidence_delta:
    changed: no
    decision_relevant: no
  next_goal_action: stop-cycle
```

Do not restate unchanged findings.

## Decision-aware cycle

When new evidence exists, classify:

```text
trigger appeared
skill activated
decision changed
clause followed/violated
outcome changed
causality unknown
```

Do not treat a new tool call or message as decision-relevant by itself.

## Goal Skill Delta Record

```yaml
goal_skill_delta_record:
  record_version: GSD-v2
  goal_id:
  cycle_id:
  target_skill:
  watched_session:
    session_id_or_path:
    cursor_start:
    cursor_end:
    state:
    workers_included:
  contract:
    authority: explicit | inferred | absent
    fingerprint:
  evidence_delta:
    changed: yes | no | unknown
    new_activation_evidence: yes | no | unknown
    new_decision_episodes: 0
    new_clause_events: 0
    new_validation_failure: yes | no | unknown
    new_user_feedback: yes | no | unknown
    new_worker_evidence: yes | no | unknown
    new_outcome_event: yes | no | unknown
    watched_session_stopped: yes | no | unknown
  decision_delta:
    classification:
      explicit_route_change |
      prevented_action |
      narrowed_scope |
      added_or_changed_proof |
      escalated_or_blocked |
      reinforced_existing_choice |
      no_visible_delta |
      contrary_to_contract |
      trigger_missed |
      false_activation |
      ceremonial_activation |
      unknown |
      none
    episode_refs: []
    clause_refs: []
    evidence_strength:
  proposed_delta:
    kind:
      none |
      status-only-stop |
      target-skill-brief |
      tune-packet |
      apply-request |
      seq-special-spec |
      retire |
      blocked
    expected_decision_change:
  next_goal_action:
    continue-watch |
    stop-cycle |
    handoff-tune |
    ask-apply-permission |
    handoff-refine |
    handoff-seq-special-spec |
    retire-finding |
    wait-for-session-stop
```

## `$tune` handoff

When the target lens identifies a skill gap, prefer a small watched-session STE packet:

```yaml
skill_tuning_evidence:
  packet_version: STE-v1
  target_skill:
  window:
    session_id:
    cursor_start:
    cursor_end:
  decision_episodes: []
  recurrent_gap_signatures: []
  evidence_limitations: []
```

Do not infer historical recurrence from one watched session.

## Modes

### observe

Report evidence only.

### propose

Default. Emit a tune packet or brief when the decision delta justifies it.

### apply

Only when explicitly requested.

`$shadow` still does not edit the watched session or steer it.

Any target-skill edit follows that skill’s own apply boundary.

## Worker sessions

Include workers only when:

- the user requests them;
- target decisions were delegated;
- the target skill requires worker evidence.

Require a parent/worker proof path.

Do not sweep corpus-wide workers.

## Stop conditions

Stop the current cycle when:

```text
no decision-relevant delta
watched session stopped
state unknown after one bounded follow-up
action requires approval
evidence insufficient
finding retired/transferred
```

## `$seq` special-spec handoff

```yaml
seq_special_spec_handoff:
  spec_version: SEQ-SPEC-HANDOFF-v2
  need:
  watched_session:
  target_skill:
  missing_decision_evidence:
  desired_command:
  acceptance_criteria: []
  validation_examples: []
```

## Report

```text
Shadowing:
- Session:
- Lens:
- Mode:
- State:

Cursor:
- Start:
- End:
- Delta:

Decision evidence:
- Activation:
- Episode:
- Clauses:
- Outcome:
- Strength:

Cycle result:
- Decision-relevant:
- Proposed delta:
- Next action:

Limitations:
```

## Hard rules

- Exactly one root watched session.
- `$seq` only for watched-session evidence.
- No raw JSONL inspection.
- No broad historical claims.
- No full report without decision-relevant delta.
- Raw mention is not activation.
- Activation is not influence.
- Influence is not causality.
- Do not edit in observe/propose.
- Do not promise background monitoring.
