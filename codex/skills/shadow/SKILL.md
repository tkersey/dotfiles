---
name: shadow
description: "Follow one Codex session until it stops, repeatedly reading new session evidence and applying a named skill as the lens for interpretation, reporting, proposal, or explicit action. Trigger when asked to shadow, tail, watch, follow, monitor, supervise, or companion a single session id/path with a target skill such as $tune, $seq, $ship, $pdf, or another skill."
---

# Shadow

## Overview

Use `$shadow` to attach a goal-driven companion to exactly one Codex session.

`$shadow` tails one watched session, interprets new evidence from that session through a named target skill, and continues until the watched session stops. It is designed to be used with `/goal` so the monitoring loop can continue across turns without broadening into an ecosystem scan.

The target skill is parameterized. `$tune` is the defining example, not a hard-coded dependency.

Core question:

```text
Given this watched session and this target skill's intended workflow,
what does the new session evidence imply, and what should $shadow report,
propose, or explicitly do before continuing to watch?
```

## Trigger Cues

Use `$shadow` when the user asks to:

- Shadow a session.
- Tail or follow a session until it stops.
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

- Monitor multiple unrelated sessions.
- Run broad autonomous skill-ecosystem scans; use `$auto`.
- Mine arbitrary sessions without a single watched session target; use `$seq`.
- Replace the target skill's workflow.
- Hard-code `$tune` behavior.
- Edit skills or files unless apply mode is explicit and the target skill supports the action.
- Create or update PRs unless the target skill and user mode explicitly require that workflow.
- Continue after the watched session stops.
- Assume `$shadow` can inject messages into or steer the watched session.
- Treat raw skill mentions as proof that the watched session used a skill correctly.
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

## Evidence Rules

Use `$seq` first for watched-session evidence.

Prefer specialized `seq` commands over generic `seq query`:

```bash
seq session-detail --root ~/.codex/sessions --session-id <session_id> --format markdown
seq turns --root ~/.codex/sessions --session-id <session_id> --format table
seq tool-lifecycle --root ~/.codex/sessions --session-id <session_id> --format table
seq session-tooling --root ~/.codex/sessions --session-id <session_id> --format table
seq tool-search --root ~/.codex/sessions --session-id <session_id> --contains "<pattern>" --mode rows --format table
```

When the target skill itself needs broader historical evidence, allow that skill's own evidence workflow, but keep the watched session as the anchor.

For example, `$shadow` with `$tune` may inspect the watched session first and then use `$tune`'s `$seq` commands only if the watched session raises a skill-usage question that requires historical comparison.

Always exclude the shadowing session itself from broader evidence searches when supported by the command, unless the user explicitly asks to include it.

Do not include raw transcript excerpts, raw memory text, secrets, credentials, private personal details, sensitive local paths, or long command outputs in user-facing reports unless explicitly allowed and safe.

## Worker and Subagent Sessions

Default scope is the single watched session only.

Include linked worker/subagent sessions only when:

- the user asks for them,
- the watched session delegates essential work to workers,
- the target skill's contract requires worker evidence, or
- a finding would be misleading without inspecting the linked worker.

When workers are included, keep the root watched session as the lifecycle anchor. Stop when the root watched session stops unless the user explicitly says to continue until workers stop too.

## Stop Condition

`$shadow` stops when the watched session stops.

A watched session is stopped when session evidence indicates no active turn/process remains and the session has reached a terminal or inactive state. Use `seq session-detail`, `seq turns`, `seq tool-lifecycle`, or another structured session-status surface when available.

If the watched session state is unknown:

- report uncertainty,
- avoid irreversible action,
- continue one more monitoring cycle if `/goal` is active and the user did not specify a stricter stop rule.

Do not invent additional stop conditions unless the user provides them.

## Workflow

### 1. Scope the Shadow Run

Write a compact setup line:

```text
Shadow: session <session_id> through <target_skill> in <observe|propose|apply> mode until the watched session stops.
```

Record:

- watched session id/path,
- target skill,
- mode,
- include-workers setting,
- raw-excerpt policy,
- specific watch objective, if any.

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

Use `$seq` session surfaces first.

Start with:

```bash
seq session-detail --root ~/.codex/sessions --session-id <session_id> --format markdown
seq turns --root ~/.codex/sessions --session-id <session_id> --format table
seq tool-lifecycle --root ~/.codex/sessions --session-id <session_id> --format table
```

Use targeted searches only when the target skill or new evidence calls for them:

```bash
seq tool-search --root ~/.codex/sessions --session-id <session_id> --contains "<command-or-tool-pattern>" --mode rows --format table
seq message-search --root ~/.codex/sessions --contains "<trigger-or-failure-phrase>" --roles user,assistant --limit 50 --format jsonl
seq skill-blocks --root ~/.codex/sessions --skill <skill> --history latest --format json
```

Never paste raw `session-detail` output into the user-facing report by default. Convert it into sanitized findings.

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
- Session: <session_id>
- Lens: <target_skill>
- Mode: <observe|propose|apply>
- Watched session state: <running|stopped|unknown>

New evidence:
- <sanitized summary>

Lens interpretation:
- <what the target skill contract implies>

Finding:
- <classification and explanation>

Action:
- <none | proposed brief | applied change | needs approval>

Next:
- <continue shadowing | stop because watched session stopped | continue with uncertainty | wait for approval>
```

### 7. Continue or Stop

If the watched session is still running, continue shadowing under `/goal`.

If the watched session has stopped, report a final summary and do not continue.

Final summary:

```text
Shadow complete:
- Session: <session_id>
- Lens: <target_skill>
- Final state: stopped
- Key findings: <summary>
- Actions proposed/taken: <summary>
- Remaining uncertainty: <summary>
```

## Helper Script

Use `scripts/shadow-scaffold` to print a repeatable command set and report skeleton:

```bash
codex/skills/shadow/scripts/shadow-scaffold --session <session_id> --skill <skill> --mode propose
```

The helper scaffolds evidence collection. It does not replace the target skill's judgment.

## Quality Bar

A good `$shadow` run:

- Follows exactly one watched session.
- Stops when that watched session stops.
- Reads the target skill before interpreting evidence.
- Uses `$seq` for watched-session evidence.
- Applies the named target skill as a lens without hard-coding `$tune`.
- Excludes the shadowing session from broader evidence searches when possible.
- Produces concise, sanitized cycle reports.
- Does not claim it can steer the watched session unless a real mechanism exists.
- Takes action only in explicit apply mode.
- Preserves protected-skill boundaries.

A bad `$shadow` run:

- Broadly scans all sessions.
- Keeps running after the watched session stops.
- Treats `$tune` as mandatory.
- Dumps raw transcript text.
- Edits files in propose or observe mode.
- Treats raw mentions as correct skill usage.
- Uses generic shell searching before `$seq` session surfaces.
- Confuses the shadowing session with the watched session.
