---
name: shadow
description: "Explicitly shadow, tail, watch, follow, monitor, supervise, or companion exactly one Codex session id/path through `$seq`, then apply a named target skill as an interpretation/reporting/proposal/action lens until the watched session stops."
---

# Shadow

## Overview

Use `$shadow` to attach a goal-driven companion to exactly one Codex session.

`$shadow` monitors one watched session through `$seq` session surfaces, interprets new evidence from that session through a named target skill, and continues only until the watched session stops. It is designed for `/goal`-driven monitoring loops without broadening into an ecosystem scan.

The target skill is parameterized. `$tune` is the defining example, not a hard-coded dependency.

Core question:

```text
Given this watched session and this target skill's intended workflow,
what does the new session evidence imply, and what should $shadow report,
propose, or explicitly do before continuing to watch?
```

## Trigger Cues

Use `$shadow` when the user explicitly asks to:

- Use `$shadow`.
- Shadow a session.
- Tail or follow one session until it stops.
- Monitor a specific session id or session path.
- Watch one running session through a named skill.
- Use `/goal` to keep checking another session.
- Apply a skill lens to a single session over time.
- Keep producing reports, proposals, or guarded actions based on one watched session.

Example prompts:

- "Use `$shadow` on session `<session_id>` with `$tune`."
- "Give `/goal` a `$shadow` objective: watch session `<id>` through the pdf skill until it stops."
- "Shadow this session with `$seq` and report any trace anomalies."
- "Follow session `<id>` with `$ship` as the lens and tell me when it becomes PR-ready."
- "Use `$shadow` to monitor session `<id>` with `$tune`; propose refinements but do not edit."
- "Shadow session `<id>` with `$refine` and apply only after explicit approval."

## Non-Goals

Do not use `$shadow` to:

- Monitor multiple unrelated root sessions.
- Run broad autonomous skill-ecosystem scans; use `$auto`.
- Mine arbitrary sessions without a single watched session target; use `$seq`.
- Replace the target skill's workflow.
- Hard-code `$tune` behavior.
- Edit skills or files unless apply mode is explicit and the target skill supports the action.
- Create or update PRs unless the target skill and user mode explicitly require that workflow.
- Continue after the watched session stops.
- Promise asynchronous or background monitoring outside an active `/goal` loop or explicit reinvocation.
- Assume `$shadow` can inject messages into or steer the watched session.
- Treat raw skill mentions as proof that the watched session used a skill correctly.
- Tail, read, grep, parse, or otherwise inspect watched-session JSONL directly.
- Fall back to non-`seq` session monitoring when `$seq` cannot answer a monitoring question.
- Dump raw transcript text by default.

## Required Inputs

Identify these before starting:

- Watched session id or session path.
- Target skill name or path.
- Mode: `observe`, `propose`, or `apply`.
- Whether linked worker/subagent sessions should be included. Default: no.
- Specific watch objective or concern, if provided.
- Whether raw transcript excerpts are allowed. Default: no.

If the user omits mode, default to `propose`.

If the user omits a target skill, ask for the target skill unless the prompt itself clearly implies one. Do not default to `$tune` merely because `$tune` is the defining example.

## Input Normalization

Normalize user inputs before the first cycle:

- Treat `$tune` and `tune` as the same target skill name for lookup and for `seq skill-blocks`.
- If the target skill input is a path to a skill directory, use that directory and derive the display name from the directory basename.
- If the target skill input is a path to `SKILL.md`, use its parent directory and derive the display name from that directory basename.
- If the watched session input is an absolute path, relative path, slash-containing path, or `.jsonl` file, use `$seq` `--path` surfaces where supported.
- If the watched session input is not path-like, use `--session-id <id> --root <root>`.
- If the target skill cannot be resolved, fail closed and ask for the skill path/name; do not silently substitute `$tune` or any other skill.
- If the watched session cannot be resolved through `$seq`, report `state_unknown` or `tooling_gap`; do not inspect raw JSONL.

When a watched session path is provided, prefer path-capable `$seq` commands for the first cycle:

```bash
seq session-detail --path <rollout.jsonl> --format markdown
seq turns --path <rollout.jsonl> --format table
seq tool-lifecycle --path <rollout.jsonl> --format table
```

After `session-detail` exposes a canonical session id, use that id for commands that are id-only or id-preferred, such as `session-prompts` and `skill-blocks`.

## Operating Modes

### Observe

Use when the user wants monitoring only.

Behavior:

- Read the target skill contract.
- Inspect the watched session.
- Summarize new evidence.
- Explain what the target skill lens implies.
- Do not produce an action brief unless the user asks.
- Do not edit, run external actions, or invoke target-skill action phases.

### Propose

Default mode.

Behavior:

- Read the target skill contract.
- Inspect the watched session.
- Interpret new evidence through that skill.
- Produce concise proposals, briefs, checklists, or next-step recommendations that the target skill would justify.
- Do not mutate files, open PRs, merge work, send messages into the watched session, or take irreversible action.

### Apply

Use only when explicitly requested with language such as `apply`, `edit`, `patch`, `fix`, `refine`, `ship`, `open the PR`, or `take action`.

Behavior:

- Produce the target-skill brief first.
- Take the smallest action justified by new evidence and by the target skill's contract.
- Preserve target-skill guardrails and validation requirements.
- If the target skill is protected, keep changes narrow and require strong evidence or explicit user direction.
- Report validation proof for any applied change.

The word `shadow` alone never implies apply mode.

## Skill Lens

A skill lens is the target skill's intended-use contract applied to the watched session's evidence.

For every target skill:

1. Read the target skill first.
2. Reconstruct its intended-use contract.
3. Inspect only the watched session by default.
4. Compare new session evidence to the target skill contract.
5. Decide whether the watched session is following, missing, misusing, or producing evidence for that skill.
6. Report, propose, or act according to `$shadow` mode.

Examples:

- With `$tune`, ask whether the watched session produces evidence about a skill's intended vs observed use and whether a `$refine` brief is justified.
- With `$seq`, ask whether the watched session is using session evidence, tool traces, memory artifacts, and lifted `seq` commands correctly.
- With `$refine`, ask whether the watched session has a precise evidence-backed edit target, minimal diff plan, and validation proof.
- With `$ship`, ask whether the watched session is approaching a PR boundary and whether branch, diff, validation, and PR hygiene are ready.
- With an artifact skill such as pdf/docx/slides/spreadsheets, ask whether the watched session follows that artifact skill's required workflow, validation, and artifact-output rules.

Do not use `$tune` rules unless `$tune` is the target skill.

## Protected Skill Gate

Protected skills require extra care as target lenses:

- `seq`
- `shadow`
- `tune`
- `refine`
- `cron`
- `auto`
- `ship`
- `land`
- `.system/*`

For protected target skills:

- Proceed only when the user explicitly names the protected skill.
- Default to `propose` unless the user clearly asks for apply mode.
- Keep any applied action narrow.
- Preserve companion-skill boundaries.
- Require validation proof for every edit or external workflow action.

If the target skill is `$shadow`, do not recursively start another shadow loop. Treat `$shadow` as a contract-review lens only unless the user explicitly asks for nested monitoring and names the nested watched session.

## Evidence Rules

Use `$seq` only for watched-session evidence.

This is a hard boundary: `$shadow` may read skill files, helper scripts, and local resources needed to reconstruct the target skill contract, but it must monitor the watched session only through `seq` commands. Do not use `tail`, `cat`, `jq`, `rg`, Python scripts, editor inspection, raw JSONL reads, or filesystem globbing as watched-session evidence collection.

If a needed watched-session fact is not available through a `seq` surface, or the available `seq` path is too slow or awkward for repeated monitoring:

- classify the cycle as `tooling_gap`, `seq_tuning_gap`, or `state_unknown`,
- report the missing `seq` surface or command shape,
- produce a `$tune`-on-`$seq` brief when the gap is concrete enough to improve `$seq`,
- do not substitute direct transcript or JSONL inspection.

Prefer specialized `seq` commands over generic `seq query`:

```bash
seq session-detail --root ~/.codex/sessions --session-id <session_id> --format markdown
seq turns --root ~/.codex/sessions --session-id <session_id> --format table
seq tool-lifecycle --root ~/.codex/sessions --session-id <session_id> --format table
seq session-tooling --root ~/.codex/sessions --session-id <session_id> --summary --group-by executable --format table
seq session-prompts --root ~/.codex/sessions --session-id <session_id> --roles user,assistant --strip-skill-blocks --limit 100 --format jsonl
seq tool-search --root ~/.codex/sessions --session-id <session_id> --contains "<pattern>" --mode summary --group-by command --limit 20 --format table
```

For monitoring loops, prefer summarized `session-tooling` and `tool-search`
surfaces before row-level tables. Use row mode only after a summary identifies a
narrow target and add an explicit `--limit`; an unbounded command-text table is
too noisy to serve as a stable cycle cursor.

Use `session-prompts --session-id` for full watched-session message recovery after a `session-detail` or `turns` preview changes. Do not use corpus-wide `message-search` for that job unless the target skill explicitly needs cross-session comparison; broad message searches can mix the shadowing session with the watched session and create false evidence.

When the target skill itself needs broader historical evidence, allow that skill's own evidence workflow only if the session evidence path remains `$seq`-backed and the watched session remains the anchor.

For example, `$shadow` with `$tune` may inspect the watched session first and then use `$tune`'s `$seq` commands only if the watched session raises a skill-usage question that requires historical comparison.

Always exclude the shadowing session itself from broader evidence searches when supported by the command, unless the user explicitly asks to include it.

Do not include raw transcript excerpts, raw memory text, secrets, credentials, private personal details, sensitive local paths, or long command outputs in user-facing reports unless explicitly allowed and safe.

## Cycle Cursor

Track a compact cursor across monitoring cycles. New evidence means the current cursor differs from the previous cursor.

Record these fields when available:

- `last_seen_turn_index`
- `last_seen_assistant_message_index`
- `last_seen_assistant_timestamp`
- `last_seen_tool_call_id`
- `last_seen_tool_end_timestamp`
- `last_seen_session_state`
- `last_reported_finding`

Classify the cycle delta as one of:

- `none`
- `turn_added`
- `assistant_message_added`
- `tool_started`
- `tool_completed`
- `tool_failed`
- `session_state_changed`
- `worker_added`
- `unknown`

Use `no_new_evidence` only when the cursor is unchanged and the watched session state is not newly stopped.

## Stop Condition

`$shadow` stops when the watched session stops.

A watched session is stopped when session evidence indicates no active turn/process remains and the session has reached a terminal or inactive state. Use `seq session-detail`, `seq turns`, `seq tool-lifecycle`, or another structured session-status surface when available.

Watched session state decision:

1. If `session-detail` reports a terminal/inactive state and `tool-lifecycle` has no unresolved active tool calls, classify the state as `stopped`.
2. If `turns` shows an active/incomplete latest turn, or `tool-lifecycle` has unresolved/running calls, classify the state as `running`.
3. If the session lookup fails, parsed status is absent, or lifecycle evidence is unavailable, classify the state as `unknown`.
4. If state is `unknown`, report uncertainty, avoid irreversible action, and continue one more cycle only when `/goal` is active and the user did not specify a stricter stop rule.
5. If state remains `unknown` after one follow-up cycle, stop with `state_unknown` unless the user explicitly asks to keep polling.

Do not invent additional stop conditions unless the user provides them.

## No Background Monitoring Promise

`$shadow` continues only inside the current active `/goal` loop or when the user explicitly reinvokes it. If `/goal` is unavailable, perform one cycle and report that continued monitoring requires reinvocation or a real goal loop.

Do not say you will keep watching in the background, notify later, or continue asynchronously unless the environment provides an explicit automation mechanism and the user requested it.

## `$seq` Tuning Handoff

`$shadow` depends on `$seq` for session monitoring. When that dependency is missing a needed surface, requires repeated caller-side filtering, requires direct JSONL access to answer a normal monitoring question, or is inefficient enough to make a monitoring loop impractical, treat that as `$tune` evidence for `$seq`.

Default handoff mode is proposal-only because `$seq` is a protected skill. Apply a `$seq` refinement only when the user explicitly asks to tune, fix, update, or patch `$seq`.

Use this brief shape:

```text
Target skill: seq

Tuning goal:
- Make <watched-session monitoring need> available as an efficient seq surface for $shadow.

Observed usage:
- Evidence class: repeated_manual_workaround | clear_validation_failure | explicit_user_feedback | tooling_gap
- Source: $shadow cycle for session <session_id-or-path>
- Finding: <sanitized missing/slow/awkward seq command shape>

Gap:
- Type: tooling
- Diagnosis: $shadow cannot monitor this session requirement through an efficient seq surface.

Recommended $refine action:
- <smallest seq skill or CLI-surface update needed>

Validation:
- quick_validate seq
- representative seq command sample, if the command surface changed
```

## Worker and Subagent Sessions

Default scope is the single watched root session only.

Include linked worker/subagent sessions only when:

- the user asks for them,
- the watched session delegates essential work to workers,
- the target skill's contract requires worker evidence, or
- a finding would be misleading without inspecting the linked worker.

Worker inclusion algorithm:

1. Run `seq session-graph` for the watched root session when worker evidence is needed and a session id is available.
2. Include only directly linked workers whose edge/timing overlaps the new root-session evidence window.
3. Inspect a worker only if the root session delegated target-skill-relevant work to it.
4. Report worker evidence under a separate `Linked worker evidence` heading.
5. Keep the root watched session as the lifecycle anchor unless the user explicitly says to continue until workers stop too.

When workers are included, stop when the root watched session stops unless the user explicitly says to continue until workers stop too.

## Workflow

### 1. Scope the Shadow Run

Write a compact setup line:

```text
Shadow: session <session_id-or-path> through <target_skill> in <observe|propose|apply> mode until the watched session stops.
```

Record:

- watched session id/path,
- target skill,
- normalized target skill display name,
- mode,
- include-workers setting,
- raw-excerpt policy,
- specific watch objective, if any,
- initial cycle cursor, if any.

### 2. Reconstruct the Target Skill Contract

Read the target skill before judging the session:

```text
codex/skills/<skill>/SKILL.md
codex/skills/<skill>/agents/openai.yaml
codex/skills/<skill>/AUTO.md
codex/skills/<skill>/scripts/
codex/skills/<skill>/references/
codex/skills/<skill>/assets/
```

Only read resources relevant to the target skill or the observed session behavior.

Summarize:

- purpose,
- triggers,
- anti-triggers and non-goals,
- expected inputs,
- expected workflow,
- expected outputs,
- required tools/scripts/references/assets,
- validation requirements,
- companion-skill handoffs,
- protected-skill constraints.

### 3. Inspect the Watched Session

Use only `$seq` session surfaces.

Start with:

```bash
seq session-detail --root ~/.codex/sessions --session-id <session_id> --format markdown
seq turns --root ~/.codex/sessions --session-id <session_id> --format table
seq tool-lifecycle --root ~/.codex/sessions --session-id <session_id> --format table
```

For path-based inputs, start with:

```bash
seq session-detail --path <rollout.jsonl> --format markdown
seq turns --path <rollout.jsonl> --format table
seq tool-lifecycle --path <rollout.jsonl> --format table
```

Use targeted searches only when the target skill or new evidence calls for them:

```bash
seq tool-search --root ~/.codex/sessions --session-id <session_id> --contains "<command-or-tool-pattern>" --mode rows --format table
seq session-prompts --root ~/.codex/sessions --session-id <session_id> --roles user,assistant --strip-skill-blocks --limit 100 --format jsonl
seq skill-blocks --root ~/.codex/sessions --session-id <session_id> --skill <skill> --history latest --format json
```

Prefer `tool-search --mode summary --group-by command --limit <N>` before row
mode when the goal is to discover whether a tool pattern matters. Switch to rows
only for the narrow command/pattern that the summary makes relevant.

If you need the complete assistant message behind a `session-detail` preview, prefer `session-prompts --session-id <session_id> --roles assistant --limit <N> --format jsonl` and inspect the newest matching watched-session rows through `$seq` output. Never paste raw `session-detail` output into the user-facing report by default. Convert it into sanitized findings.

### 4. Interpret Through the Skill Lens

Classify the cycle finding:

- `no_new_evidence`
- `aligned`
- `missed_activation`
- `false_activation`
- `partial_activation`
- `workflow_gap`
- `validation_gap`
- `tooling_gap`
- `seq_tuning_gap`
- `boundary_gap`
- `ready_for_target_action`
- `needs_user_approval`
- `watched_session_stopped`
- `state_unknown`

Use the target skill's own taxonomy if it has one. For example, if the target is `$tune`, use `$tune` evidence classes and gap types.

### 5. Decide the Response

In observe mode:

- report the finding only.

In propose mode:

- produce the smallest target-skill brief or recommendation justified by evidence.

In apply mode:

- take the smallest target-skill action justified by evidence,
- obey target-skill validation requirements,
- report exactly what changed or what action ran,
- stop before risky actions that need user approval.

### 6. Report the Cycle

Use this shape:

```text
Shadowing:
- Session: <session_id-or-path>
- Lens: <target_skill>
- Mode: <observe|propose|apply>
- Watched session state: <running|stopped|unknown>

Cycle cursor:
- Previous: turn=<n|unknown>, tool_end=<timestamp|unknown>, state=<running|stopped|unknown>
- Current: turn=<n|unknown>, tool_end=<timestamp|unknown>, state=<running|stopped|unknown>
- Delta: <none|turn_added|assistant_message_added|tool_started|tool_completed|tool_failed|session_state_changed|worker_added|unknown>

New evidence:
- <sanitized summary>

Lens interpretation:
- <what the target skill contract implies>

Finding:
- <classification and explanation>

Action:
- <none | proposed brief | proposed $tune-on-$seq brief | applied change | needs approval>

Next:
- <continue shadowing | stop because watched session stopped | continue once with uncertainty | wait for approval | reinvoke/enable /goal for continued monitoring>
```

### 7. Continue or Stop

If the watched session is still running and `/goal` is active, continue shadowing under `/goal`.

If the watched session is still running but `/goal` is not active, stop after the current cycle and say continued monitoring requires reinvocation or a real goal loop.

If the watched session has stopped, report a final summary and do not continue.

Final summary:

```text
Shadow complete:
- Session: <session_id-or-path>
- Lens: <target_skill>
- Final state: stopped
- Key findings: <summary>
- Actions proposed/taken: <summary>
- Remaining uncertainty: <summary>
```

## Helper Script

Use `scripts/shadow-scaffold` to print a repeatable command set and report skeleton:

```bash
codex/skills/shadow/scripts/shadow-scaffold --session <session_id_or_path> --skill <skill> --mode propose
```

Useful options:

```bash
codex/skills/shadow/scripts/shadow-scaffold \
  --session /absolute/path/to/rollout.jsonl \
  --skill '$tune' \
  --mode propose \
  --skills-root codex/skills \
  --include-workers
```

The helper scaffolds evidence collection. It does not replace the target skill's judgment.

## Quality Bar

A good `$shadow` run:

- Follows exactly one watched root session.
- Stops when that watched session stops.
- Reads the target skill before interpreting evidence.
- Normalizes `$skill` names and session id/path inputs before generating commands.
- Tracks a cycle cursor so `new evidence` means a real observed delta.
- Uses only `$seq` for watched-session evidence.
- Produces a `$tune`-on-`$seq` brief when `$seq` lacks an efficient monitoring surface.
- Applies the named target skill as a lens without hard-coding `$tune`.
- Excludes the shadowing session from broader evidence searches when possible.
- Produces concise, sanitized cycle reports.
- Does not claim it can steer the watched session unless a real mechanism exists.
- Does not promise background monitoring outside an actual `/goal` or automation mechanism.
- Takes action only in explicit apply mode.
- Preserves protected-skill boundaries.

A bad `$shadow` run:

- Broadly scans all sessions.
- Keeps running after the watched session stops.
- Treats `$tune` as mandatory.
- Dumps raw transcript text.
- Edits files in propose or observe mode.
- Treats raw mentions as correct skill usage.
- Uses direct transcript reads, generic shell searching, or raw JSONL parsing for watched-session monitoring.
- Treats a missing or inefficient `$seq` monitoring surface as a reason to bypass `$seq` instead of tuning it.
- Uses generic `seq query` before specialized `$seq` session surfaces.
- Confuses the shadowing session with the watched session.
- Re-reports old evidence because no cursor was tracked.
