# $opt Delegation Prompts

Use these templates from the parent session. The parent session remains responsible for interpreting the result and updating CAS goal state.

## Audit pass

```text
Spawn the custom agent `skill-optimizer` and wait for its result.

Delegation:
- target_skill: <skill path/name>
- mode: audit
- current_goal: <CAS parent goal or none>
- evidence: <current-turn context or provided notes>
- allowed_files: <target skill package, read-only>
- forbidden_files: <anything outside target unless read-only inspection is needed>
- validation_commands: none
- apply_policy: no_edit
- output_required: structured report with trigger precision, non-goal clarity, workflow clarity, validation surface, residual risk, and suggested parent CAS status.

Do not edit files. Do not manage the parent goal lifecycle.
```

## Tune-backed proposal

```text
Use $tune to produce or update a refinement brief for <target skill> from <evidence source>.
Then spawn `skill-optimizer` and wait for its result.

Delegation:
- target_skill: <skill path/name>
- mode: tune
- current_goal: <CAS parent goal or none>
- evidence: <paste or path to $tune brief>
- allowed_files: <target skill package, read-only unless explicitly applying>
- forbidden_files: <unrelated skills and repo code>
- validation_commands: <known checks or discover minimally>
- apply_policy: no_edit | propose_patch
- output_required: refinement-ready proposal, validation plan, residual risk, suggested parent CAS status.

Do not edit unless apply_policy is edit_allowed.
```

## Shadow-backed diagnosis

```text
Use $shadow on watched session <session-id-or-path> with target skill <target skill> in propose mode.
Use the $shadow report as the evidence source.
Then spawn `skill-optimizer` and wait for its result.

Delegation:
- target_skill: <skill path/name>
- mode: shadow-diagnose
- current_goal: <CAS parent goal or none>
- evidence: <$shadow report summary; no raw transcript unless authorized>
- allowed_files: <target skill package, read-only unless explicitly applying>
- forbidden_files: <unrelated skills, raw watched-session files unless authorized>
- validation_commands: <known checks or none>
- apply_policy: no_edit | propose_patch
- output_required: observed skill implication, local-vs-general evidence limit, proposed $tune brief if needed, suggested parent CAS status.

Do not infer broad recurrence from one watched session unless there is additional evidence.
```

## Goal-managed loop

```text
Use $cas to set or inspect the parent goal before delegation.
Goal shape:
- target_skill: <skill>
- desired_behavior: <behavior>
- constraints: <files/modes/no-go areas>
- evidence_required: <validation/probe/report>
- blocked_condition: <what would require user input>

Spawn `skill-optimizer` for exactly one bounded pass and wait for its result.

Delegation:
- target_skill: <skill path/name>
- mode: <audit|propose|tune|patch|validate|regression>
- current_goal: <CAS parent goal text/id>
- evidence: <selected evidence>
- allowed_files: <explicit list>
- forbidden_files: <explicit list>
- validation_commands: <commands>
- apply_policy: <no_edit|propose_patch|edit_allowed>
- output_required: structured report plus Suggested parent CAS status.

After the subagent returns, the parent validates the evidence and uses $cas to continue, pause, block, clear, or complete.
```

## Explicit patch pass

```text
Spawn the custom agent `skill-optimizer` and wait for its result.

Delegation:
- target_skill: <skill path/name>
- mode: patch
- current_goal: <CAS parent goal or none>
- evidence: <user request + $tune brief or current-turn diagnosis>
- allowed_files: <exact files/directories that may be edited>
- forbidden_files: <explicit no-go files/directories>
- validation_commands: <frontmatter check, opt-sanity, target validator, or probe>
- apply_policy: edit_allowed
- output_required: files inspected, exact changes made, validation output, residual risks, suggested parent CAS status.

Make only the smallest defensible edit. Do not commit, push, or manage the parent goal lifecycle.
```
