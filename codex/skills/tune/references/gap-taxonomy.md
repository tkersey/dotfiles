# `$tune` Gap Taxonomy

## Activation Gap

The skill fails to trigger when it should, or triggers when it should not.

Common fixes:

- frontmatter description update,
- trigger cue update,
- anti-trigger addition,
- example addition,
- `agents/openai.yaml` update.

## Interpretation Gap

The skill triggers, but the agent misunderstands the task.

Common fixes:

- clarify purpose,
- add input classification,
- add decision rules,
- add positive and negative examples.

## Workflow Gap

The skill triggers, but agents skip, weaken, or misorder steps.

Common fixes:

- revise workflow order,
- add checkpoints,
- add fallback rules,
- add output checklist,
- add validation requirements.

## Tooling Gap

The skill repeatedly uses fragile ad hoc commands or lacks deterministic helpers.

Common fixes:

- add or revise scripts,
- document command usage,
- add representative sample runs.

Do not add scripts for judgment-heavy work.

## Resource Gap

The skill needs reusable reference material or static assets.

Common fixes:

- add `references/`,
- add `assets/`,
- move long reusable guidance out of `SKILL.md`.

## Validation Gap

The skill lacks a clear proof path.

Common fixes:

- add `quick_validate`,
- add script sample commands,
- run `scripts/validate-changed-skills` when shared assumptions or multiple skills change,
- add concrete success criteria.

## Metadata Gap

Skill metadata no longer matches behavior or actual use.

Common fixes:

- update frontmatter description,
- update `agents/openai.yaml`,
- align display name, short description, and default prompt.

## Boundary Gap

The skill overlaps with another skill or has weak handoff rules.

Common fixes:

- add non-goals,
- add anti-triggers,
- clarify companion-skill routing,
- tighten handoff rules.
