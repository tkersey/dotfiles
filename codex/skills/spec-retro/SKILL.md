---
name: spec-retro
description: "Mine historical Codex sessions, plans, reports, and workflows to improve future spec automation. Use for `$spec-retro`, learn from my past planning, mine plan churn, update exemplar library, derive automation from past practice, spec telemetry, receipt metrics, or which historical sessions should tune this spec workflow."
metadata:
  version: "1.2.0"
  base_file_sha: "1249f5ef7d867665da13d4d3fdbb30e6ffeaf8d9"
---

# Spec Retro

## Mission

Drive future automation from observed practice instead of generic process advice.

The highest-value retrospective output is not more process language. It is a small set of gate rules, lint rules, receipt fields, churn triggers, and exemplar patterns that can be encoded into skills/scripts.

## Inputs

Use any available:

- session JSONL;
- plan artifacts;
- `$grill-me` snapshots;
- `$plan` outputs;
- `$spec-pipeline` outputs;
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
- question types that actually unlocked planning;
- no-grill paths that were justified vs. premature;
- subagent fan-out that produced value vs. noise;
- blocked states that have or lack taxonomy;
- mutation before gate/challenge/lint.

## Exemplar library shape

```yaml
spec_exemplars:
  - id:
    label: ordinary_clean_spec | ambition_escalation | invariant_challenge | plan_churn_warning | mode_boundary | no_grill_fast_path | subagent_fanout_warning
    source:
    trigger:
    good_pattern:
    failure_pattern:
    reusable_gate:
    suggested_skill_update:
```

## Churn detector

If given plan files or session excerpts, use:

```bash
python codex/skills/spec-retro/scripts/spec_churn_detect.py plan-*.md
```

The script looks for title drift, repeated replacement language, high iteration markers, many open questions, objective-changing Round Delta text, repeated blocked states, high subagent counts, and campaign-mode triggers.

## Output

```text
SPEC RETRO
positive_exemplars:
warning_exemplars:
automation_rules:
gate_updates:
lint_updates:
receipt_updates:
subagent_budget_updates:
question_generator_updates:
next_measurement_plan:
```

Do not mutate skill files unless the user explicitly asks for edits.
