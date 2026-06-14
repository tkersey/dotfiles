---
name: shadow
description: "Goal-native session shadowing: watch exactly one Codex session through `$seq`, apply one named target-skill lens, emit a compact cycle result, and avoid repeated full analysis when evidence has not changed. Use for `$shadow`, shadow/tail/watch/follow/monitor/supervise one session, `$shadow $tune`, goal-cycle monitoring, target-skill evidence delta, partial activation, status-only-stop, or proposal handoff. Do not use for broad session mining, autonomous scans, raw transcript inspection, editing without apply mode, or creating a second continual controller outside `/goal`."
---

# Shadow

## Purpose

`$shadow` is a **goal-native cycle filter** for exactly one watched Codex session.

It monitors one watched session through `$seq`, applies one named target skill as an interpretation lens, and returns a decision for the current `/goal` cycle.

Core rule:

```text
No evidence delta, no full shadow report.
```

`/goal` owns continuation. `$shadow` owns only the current cycle decision.

## Mental model

```text
/goal cycle
  -> $shadow checks watched-session evidence delta
  -> if no decision-relevant delta: status-only-stop
  -> if delta exists: apply target-skill lens
  -> emit goal_skill_delta_record
  -> /goal decides whether to continue, stop, hand off, apply, or wait
```

`$shadow` must not become a second autonomous runtime.

## Trigger cues

Use `$shadow` when the user explicitly asks to:

- use `$shadow`;
- shadow/tail/follow/watch/monitor one session;
- watch one running session through a named skill;
- use `/goal` to keep checking another session;
- apply a target-skill lens to one session over time;
- monitor a session with `$tune`, `$seq`, `$refine`, `$ship`, or another skill lens.

Example prompts:

```text
Use $shadow on session <id> with $tune.
Give /goal a $shadow objective: watch session <id> through $tune.
Shadow this session with $seq and report trace anomalies.
Follow session <id> with $ship as the lens and tell me when it becomes PR-ready.
```

## Non-goals

Do not use `$shadow` to:

- monitor multiple unrelated root sessions;
- run broad autonomous skill-ecosystem scans;
- mine arbitrary sessions without one watched-session target;
- replace the target skill's workflow;
- hard-code `$tune` behavior;
- edit files unless apply mode is explicit and the target skill supports action;
- promise asynchronous/background monitoring outside `/goal` or explicit reinvocation;
- inject messages into or steer the watched session;
- treat raw skill mentions as proof of correct skill use;
- inspect watched-session JSONL directly with `tail`, `cat`, `jq`, `rg`, Python, or raw file reads;
- bypass `$seq` when `$seq` lacks a monitoring surface;
- produce another full analysis when no decision-relevant evidence changed.

## Required inputs

Identify before the first cycle:

- watched session id or path;
- target skill name or path;
- mode: `observe`, `propose`, or `apply`;
- specific watch objective or concern, if provided;
- include-workers setting, default `no`;
- raw-excerpt policy, default `no`;
- prior cycle cursor, if any.

If mode is omitted, default to `propose`.

If target skill is omitted, ask for the target skill unless the prompt clearly implies one. Do not default to `$tune`.

## Self-shadow guard

Bare `$shadow $tune` with no external watched session, no target skill concern, and no evidence question is a partial activation.

Return one compact cycle:

```yaml
goal_skill_delta_record:
  record_version: GSD-v1
  cycle_result: partial_activation
  reason: "No external watched session or target evidence concern was supplied."
  next_goal_action: stop-cycle
```

Do not recursively shadow the current shadowing session unless the user explicitly supplies a distinct watched session and asks for nested monitoring.

## Input normalization

- Treat `$tune` and `tune` as the same target skill name.
- If the watched session input is path-like or ends in `.jsonl`, use `$seq --path` surfaces where supported.
- If the watched session input is an id, use `--session-id <id> --root <root>`.
- If target skill is a directory or `SKILL.md` path, normalize to its skill directory.
- If watched session cannot be resolved through `$seq`, return `state_unknown` or `tooling_gap`; do not inspect raw JSONL.

## Operating modes

### observe

Monitor and report only. Do not create an action brief unless asked.

### propose

Default. Interpret new evidence through the target skill and produce concise proposals, briefs, or next-step recommendations. Do not mutate.

### apply

Use only when explicitly requested with `apply`, `edit`, `patch`, `fix`, `refine`, `ship`, `open PR`, or similar. Produce the brief first, then take only the smallest target-skill-supported action.

`shadow` alone never implies apply mode.

## Skill lens

A skill lens is the target skill's intended-use contract applied to new watched-session evidence.

For every target skill:

1. Read the target skill first.
2. Reconstruct its intended-use contract.
3. Inspect only the watched session by default.
4. Compare new session evidence to the target skill contract.
5. Decide whether the watched session is aligned, missing, misusing, or producing evidence for that skill.
6. Report, propose, or act according to mode.

Do not use `$tune` rules unless `$tune` is the target skill.

## Protected skill gate

Protected target skills:

- `seq`
- `shadow`
- `tune`
- `refine`
- `ship`
- `land`
- `.system/*`

For protected targets:

- proceed only when explicitly named;
- default to `propose`;
- keep changes narrow;
- preserve companion boundaries;
- require validation proof for edits.

## Evidence rules

Use `$seq` only for watched-session evidence.

`$shadow` may read the target skill files to reconstruct the skill contract, but it must monitor the watched session only through `$seq`.

If a needed watched-session fact is not available through `$seq`:

- classify as `tooling_gap`, `seq_tuning_gap`, or `state_unknown`;
- produce a `$tune`-on-`$seq` handoff when concrete;
- do not substitute raw transcript/file inspection.

Preferred `$seq` surfaces:

```bash
seq session-detail --root ~/.codex/sessions --session-id <session_id> --format markdown
seq turns --root ~/.codex/sessions --session-id <session_id> --format table
seq tool-lifecycle --root ~/.codex/sessions --session-id <session_id> --format table
seq session-tooling --root ~/.codex/sessions --session-id <session_id> --summary --group-by executable --format table
seq session-prompts --root ~/.codex/sessions --session-id <session_id> --roles user,assistant --strip-skill-blocks --limit 100 --format jsonl
seq tool-search --root ~/.codex/sessions --session-id <session_id> --contains "<pattern>" --mode summary --group-by command --limit 20 --format table
```

For proposed `$seq` CLI changes, `$shadow` may produce a special-spec handoff only. It does not modify `$seq`.

## Cycle cursor

Track a compact cursor across cycles:

```yaml
cycle_cursor:
  last_seen_turn_index:
  last_seen_assistant_message_index:
  last_seen_assistant_timestamp:
  last_seen_tool_call_id:
  last_seen_tool_end_timestamp:
  last_seen_session_state:
  last_reported_finding_signature:
```

Classify the raw cursor delta:

```text
none
turn_added
assistant_message_added
tool_started
tool_completed
tool_failed
session_state_changed
worker_added
unknown
```

## Productive-cycle gate

Before a full target-skill report, decide whether there is a **decision-relevant delta**.

Full analysis is allowed only when at least one is true:

- new target-skill evidence appeared;
- new validation failure appeared;
- new user feedback appeared;
- watched session stopped;
- new concrete skill gap appeared;
- new worker evidence changes the interpretation;
- prior finding was falsified or resolved;
- user explicitly asked for full analysis.

If none are true, emit a compact status-only record and stop the current cycle:

```yaml
goal_skill_delta_record:
  record_version: GSD-v1
  watched_session:
    session_id_or_path: "..."
    state: running | stopped | unknown
  evidence_delta:
    changed: no
  decision_event:
    needed: no
    reason: "No new evidence capable of changing the target-skill decision."
  proposed_delta:
    kind: status-only-stop
  next_goal_action: stop-cycle
```

Do not expand unchanged findings every cycle.

## Goal Skill Delta Record

Every cycle should return this compact record, either inline or in the final report:

```yaml
goal_skill_delta_record:
  record_version: GSD-v1
  goal_id: "unknown | ..."
  cycle_id: "..."
  target_skill: "..."
  watched_session:
    session_id_or_path: "..."
    cursor_start: "..."
    cursor_end: "..."
    state: running | stopped | unknown
  evidence_delta:
    changed: yes | no | unknown
    new_target_skill_evidence: yes | no | unknown
    new_validation_failure: yes | no | unknown
    new_user_feedback: yes | no | unknown
    watched_session_stopped: yes | no | unknown
    new_skill_gap: yes | no | unknown
    new_worker_evidence: yes | no | unknown
  decision_event:
    needed: yes | no | unknown
    reason: "..."
  proposed_delta:
    kind: none | status-only-stop | target-skill-brief | apply-request | seq-special-spec | retire | blocked
    expected_decision_change: "..."
  next_goal_action:
    continue-watch | stop-cycle | ask-apply-permission | handoff-refine | handoff-seq-special-spec | retire-finding | wait-for-session-stop
```

This is the return value of one `/goal` cycle. It is not a background subscription.

## Stop condition

`$shadow` stops the current cycle when:

- watched session has stopped;
- evidence delta is not decision-relevant;
- state remains unknown after one follow-up cycle;
- target action needs approval;
- target evidence is insufficient;
- `/goal` is unavailable and the current cycle is complete.

`$shadow` does not promise to keep watching in the background.

## `$seq` special-spec handoff

If `$shadow` discovers a `$seq` CLI surface gap, produce a special-spec brief rather than editing `$seq`:

```text
Target: seq CLI special spec

Need:
- <watched-session monitoring need>

Observed gap:
- <sanitized missing or inefficient seq command shape>

Required behavior:
- <desired session-scoped evidence surface>

Acceptance:
- <representative command should distinguish injected skill blocks, assistant-declared use, manual skill-file reads, target-skill lens use, successful activation evidence, and raw mentions>

Validation:
- quick_validate seq
- representative seq command samples
```

## Worker sessions

Default scope is the watched root session only.

Include linked workers only when user asks, the watched session delegates target-skill-relevant work, or the target skill requires worker evidence.

Root watched session remains the lifecycle anchor unless user says otherwise.

## Report shape

Use this compact shape:

```text
Shadowing:
- Session:
- Lens:
- Mode:
- Watched session state:

Cycle cursor:
- Previous:
- Current:
- Delta:

Goal skill delta:
- Evidence changed:
- Decision needed:
- Proposed delta:
- Next goal action:

Finding:
- <classification and explanation>

Action:
- <none | target-skill brief | seq special-spec handoff | applied change | needs approval>
```

If stopped:

```text
Shadow complete:
- Session:
- Lens:
- Final state:
- Key findings:
- Actions proposed/taken:
- Remaining uncertainty:
```

## Quality bar

A good `$shadow` run:

- follows exactly one watched root session;
- uses `$seq` only for watched-session evidence;
- reads the target skill before interpreting;
- tracks cursor state;
- emits status-only-stop when no decision-relevant evidence changed;
- fails fast for bare/self-shadow partial activation;
- returns a `goal_skill_delta_record`;
- does not edit in observe/propose mode;
- preserves protected-skill boundaries;
- lets `/goal` own continuation.

A bad `$shadow` run:

- broadly scans all sessions;
- re-reports unchanged evidence;
- treats `$tune` as mandatory;
- dumps raw transcripts;
- edits files without apply mode;
- bypasses `$seq`;
- treats raw mentions as skill success;
- tries to manage its own continual loop outside `/goal`.
