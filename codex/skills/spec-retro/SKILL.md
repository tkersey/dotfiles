---
name: spec-retro
description: >
  Mine historical Codex sessions, plans, reports, and prior workflows to improve future spec automation. Use when prompts say "$spec-retro", "learn from my past planning", "mine plan churn", "update exemplar library", "derive automation from past practice", or "which historical sessions should tune this spec workflow".
---

# Spec Retro

## Mission

Drive future automation from observed practice instead of generic process advice.

## Inputs

Use any available:

- session JSONL;
- plan artifacts;
- `$grill-me` snapshots;
- `$plan` outputs;
- reports about prior usage;
- `.learnings.jsonl`;
- `seq` query results.

## Mine for these signals

- clean pipeline examples;
- plan-churn loops;
- post-plan invariant challenges that improved architecture;
- oversized specs with duplicate audit prose;
- handoff packets with enough locked decisions;
- lints that would have blocked bad plans;
- size profile boundaries;
- question types that actually unlocked planning.

## Exemplar library shape

```yaml
spec_exemplars:
  - id:
    label: ordinary_clean_spec | ambition_escalation | invariant_challenge | plan_churn_warning | mode_boundary
    source:
    trigger:
    good_pattern:
    failure_pattern:
    reusable_gate:
    suggested_skill_update:
```

## Churn detector

If given plan files, use:

```bash
python codex/skills/spec-retro/scripts/spec_churn_detect.py plan-*.md
```

The script looks for title drift, repeated replacement language, high iteration markers, many open questions, and objective-changing Round Delta text.

## Output

```text
SPEC RETRO
positive_exemplars:
warning_exemplars:
automation_rules:
gate_updates:
lint_updates:
question_generator_updates:
```

Do not mutate skill files unless the user explicitly asks for edits.
