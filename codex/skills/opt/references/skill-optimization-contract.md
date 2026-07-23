# Skill Optimization Contract

A skill optimization is valid only when it improves at least one of these surfaces without degrading another.

## 1. Trigger precision

The skill should activate for the right prompts and avoid accidental activation.

Valid improvements:

- Front-load exact trigger cues in the description.
- Add non-goals for broad words such as optimize, audit, watch, tune, fix, refactor, or ship.
- Separate user-facing trigger phrases from implementation details.
- Clarify when a companion skill owns the workflow.

Invalid improvements:

- Adding "always use this skill" language.
- Making a description broad merely to catch more prompts.
- Hiding important trigger constraints deep in `SKILL.md` while the frontmatter stays vague.

## 2. Operational clarity

The skill should tell the agent how to act.

Valid improvements:

- Declare required inputs.
- Route ambiguous prompts into safe default modes.
- State edit/apply gates.
- Define outputs and stop conditions.
- Add delegation prompts for subagents when subagents are part of the workflow.

Invalid improvements:

- Inspirational doctrine without executable steps.
- Several overlapping modes with no precedence rule.
- Apply behavior that can be inferred from weak verbs like improve or optimize.

## 3. Evidence quality

The skill should connect changes and conclusions to a proof surface.

Valid improvements:

- Declare evidence source kind and limitations.
- Add probes for false activation, missed activation, and partial activation.
- Name the outcome evidence and its limitations.
- Preserve concrete receipts from CAS, Shadow, Tune, or observed worktree behavior.

Invalid improvements:

- Treating raw mentions of a skill as proof it was used correctly.
- Generalizing from one session without saying the evidence is local.
- Marking a goal complete without evidence for every claimed outcome.

## 4. Companion-skill boundaries

The skill should preserve neighboring responsibilities.

Boundary map:

- `$cas`: durable goal and app-server/thread lifecycle control.
- `$shadow`: one watched session, interpreted through one target skill lens.
- `$tune`: intended-vs-observed skill-use diagnosis and refinement briefs.
- `$refine`: in-place skill edit workflow when a refinement brief is ready.
- `$ms`: new skills or direct skill surgery when no usage-backed diagnosis is required.
- `$ship` / `$land`: PR and merge workflows.

Invalid improvements:

- Replacing a companion skill's workflow instead of calling or consuming it.
- Letting a subagent mutate the parent goal lifecycle.
- Letting a monitoring skill edit files without an explicit apply gate.

## 5. Context economy

The skill should be cheap to load and easy to route.

Valid improvements:

- Keep `SKILL.md` concise and operational.
- Move long examples, matrices, templates, and doctrine into `references/`.
- Use scripts only for substantive operations that natural-language instructions cannot perform.

Invalid improvements:

- Adding long historical analysis to `SKILL.md`.
- Adding unused references.
- Adding scripts that require network access or hidden local state.

## 6. Session ergonomics

The skill should be easy to call repeatedly during active work.

Valid improvements:

- Provide one compact default prompt.
- Provide a reusable subagent delegation template.
- Return stable report fields.
- Keep parent/child goal status separate.

Invalid improvements:

- Making the user remember a long spawn prompt.
- Returning prose that cannot be used by `$cas`, `$shadow`, or `$tune`.
- Collapsing audit, proposal, apply, outcome observation, and ship into one ambiguous mode.
