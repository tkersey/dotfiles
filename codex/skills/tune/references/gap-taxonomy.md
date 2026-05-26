# `$tune` Gap Taxonomy

Use this taxonomy after reconstructing the target skill's intended-use contract and building an evidence ledger.

## Activation Gap

The skill fails to trigger when it should, triggers late, or triggers when it should not.

Evidence patterns:

- User asks for work owned by the skill, but the skill is absent.
- A different skill repeatedly intercepts the request.
- The skill appears in sessions it should not own.
- Trigger language in frontmatter no longer matches actual user phrasing.

Common fixes:

- Frontmatter description update.
- Trigger cue update.
- Anti-trigger addition.
- User-language example addition.
- `agents/openai.yaml` update.

## Interpretation Gap

The skill triggers, but the agent misunderstands what the user wants or how to classify the input.

Evidence patterns:

- The skill is mentioned, but the output solves a different problem.
- Agents ask avoidable clarifying questions despite sufficient inputs.
- Agents choose the wrong mode, workflow, or companion handoff.

Common fixes:

- Clarify purpose.
- Add input classification rules.
- Add mode or decision rules.
- Add positive and negative examples.

## Workflow Gap

The skill triggers, but agents skip, weaken, or misorder required steps.

Evidence patterns:

- Required reads happen after conclusions.
- Validation is omitted or deferred.
- Evidence is mined but not interpreted before edits.
- Output format is inconsistent with the skill's report shape.

Common fixes:

- Revise workflow order.
- Add checkpoints.
- Add fallback rules.
- Add output checklist.
- Add validation requirements.

## Tooling Gap

The skill repeatedly uses fragile ad hoc commands or lacks deterministic helpers.

Evidence patterns:

- Similar shell pipelines recur across sessions.
- Agents hand-write brittle queries that a small helper could scaffold.
- Script behavior is undocumented or unvalidated.

Common fixes:

- Add or revise scripts.
- Document command usage.
- Add representative sample runs.

Do not add scripts for judgment-heavy work. Scripts should scaffold, validate, or transform deterministic inputs; the skill should retain diagnosis and decision-making.

## Resource Gap

The skill needs reusable reference material or static assets.

Evidence patterns:

- `SKILL.md` duplicates long guidance that should be canonical elsewhere.
- Multiple sessions require the same template, taxonomy, checklist, or prompt probes.
- Agents overlook reusable guidance because it is buried in a long skill body.

Common fixes:

- Add or update `references/`.
- Add `assets/` only for reusable static assets.
- Move long reusable guidance out of `SKILL.md`.
- Keep `SKILL.md` focused on routing and execution.

## Validation Gap

The skill lacks a clear proof path or agents claim validation without running it.

Evidence patterns:

- Applied edits lack `quick_validate` output.
- Script changes lack sample runs.
- Shared assumptions change without multi-skill validation.
- Required validator assets are unavailable but the report implies success.

Common fixes:

- Add explicit `quick_validate` requirement.
- Add script sample commands.
- Run `scripts/validate-changed-skills` when shared assumptions or multiple skills change.
- Add concrete success criteria.
- State blocked validation honestly when `.system/skill-creator` assets are unavailable.

## Metadata Gap

Skill metadata no longer matches behavior or actual use.

Evidence patterns:

- Frontmatter trigger text differs from the skill body.
- `agents/openai.yaml` default prompt omits a key boundary or mode gate.
- Display metadata suggests broader or narrower behavior than the skill performs.

Common fixes:

- Update frontmatter description.
- Update or regenerate `agents/openai.yaml`.
- Align display name, short description, and default prompt.

## Boundary Gap

The skill overlaps with another skill or has weak handoff rules.

Evidence patterns:

- Agents use this skill where `$seq`, `$refine`, `$ms`, `$ship`, or `$land` should own the turn.
- A complete edit brief is re-diagnosed unnecessarily.
- A diagnostic request triggers file edits prematurely.

Common fixes:

- Add non-goals.
- Add anti-triggers.
- Clarify companion-skill routing.
- Tighten handoff rules.
- Add mode precedence rules.

## Evidence Thresholds

Strong evidence can justify applied refinement when the apply gate is satisfied. Weak-only evidence usually supports audit-only or proposal-only.

Default thresholds:

- `repeated_session_evidence`: same gap appears in at least 3 relevant sessions, or at least 2 independent sessions plus explicit user feedback.
- `repeated_manual_workaround`: substantially similar workaround appears in at least 3 sessions or across at least 2 target skills.
- `low_activation_count`: fewer than 3 relevant activations in the selected time window.
- `single_ambiguous_session`: one session with unclear intent, incomplete trace, or no explicit outcome signal.
- `clear_routing_failure`: user asked for the skill's owned work and a different skill or no skill handled the core workflow.
- `historical_skill_regression`: behavior changed after a material skill-block, trigger, metadata, or workflow update.

Explicit current-turn user feedback can be strong evidence for narrow local changes. It should not justify broad redesign without corroborating evidence.


## Source-Scope Gap

The skill chooses the wrong evidence source or treats one source as proving more than it can.

Evidence patterns:

- A current-conversation issue triggers unnecessary historical mining.
- A request for arbitrary history silently falls back to a 90-day default.
- Current-turn feedback is used to claim historical recurrence.
- Historical evidence is used to ignore direct current user feedback.

Common fixes:

- Add evidence-source selection rules.
- Add source descriptors to the brief and report.
- Separate in-flight, historical, provided, and worktree evidence in the ledger.
- Add counterevidence and source-limit fields.
