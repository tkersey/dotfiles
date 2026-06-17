---
name: spec-retro
description: "Mine historical Codex sessions, specs, plans, reports, and workflows to improve spec automation. Use for `$spec-retro`, past-planning lessons, plan churn, exemplar libraries, automation from past practice, spec telemetry, receipt metrics, invisible companion phases, report-to-automation bridge, or choosing sessions to tune spec workflows."
metadata:
  version: "1.3.0"
---

# Spec Retro

## Mission

Drive future automation from observed practice instead of generic process advice.

The highest-value retrospective output is not more process language. It is a small set of gate rules, lint rules, receipt fields, churn triggers, and exemplar patterns that can be encoded into skills/scripts.

## Trigger policy

Do not run `$spec-retro` after every spec.

Trigger when one of these is true:

- 5 or more `$spec-pipeline` sessions since last retro;
- 2 or more repeated gate/lint/challenge gaps;
- a report shows companion phases are invisible;
- execution started before gate/challenge/lint/governance readiness;
- `$plan` or `update_plan` churn recurs;
- repeated no-grill justifications are generic;
- subagent fanout repeatedly produces no route impact;
- pipeline reports cannot distinguish companion mentions from phase impact.

## Inputs

Use any available:

- session JSONL;
- spec outputs;
- plan artifacts;
- `$grill-me` snapshots;
- `$plan` outputs;
- `$spec-pipeline` outputs;
- spec governance receipts;
- reports about prior usage;
- `.learnings.jsonl`;
- `seq` query results.

## Mine for these signals

- clean pipeline examples;
- missing `spec_governance_receipt`;
- gate/challenge/lint/fresh-eyes phases that changed the spec;
- gate/challenge/lint/fresh-eyes phases that were pass-no-delta;
- plan-churn loops;
- post-plan invariant challenges that improved architecture;
- oversized specs with duplicate audit prose;
- handoff packets with enough locked decisions;
- lints that would have blocked bad plans;
- size profile boundaries;
- question types that actually unlocked planning;
- no-grill paths that were justified vs. premature;
- subagent fanout that produced value vs. noise;
- blocked states that have or lack taxonomy;
- mutation before gate/challenge/lint/governance readiness.

## Exemplar library shape

```yaml
spec_exemplars:
  - id:
    label: ordinary_clean_spec | ambition_escalation | invariant_challenge | plan_churn_warning | mode_boundary | no_grill_fast_path | subagent_fanout_warning | governance_receipt_good | governance_receipt_missing
    source:
    trigger:
    good_pattern:
    failure_pattern:
    reusable_gate:
    suggested_skill_update:
```

## Retro update output

Emit a compact update, not a long essay:

```yaml
spec_retro_update:
  update_version: SRETRO-v1
  report_window: "..."
  trigger:
    reason: "..."
    evidence_refs: []
  observed_pattern: "..."
  automation_rules: []
  gate_updates: []
  lint_updates: []
  challenge_updates: []
  receipt_updates: []
  subagent_budget_updates: []
  question_generator_updates: []
  exemplar_updates: []
  next_measurement_plan:
    metric: "..."
    expected_change: "..."
  apply_now: yes | no
  suggested_owner: spec-pipeline | spec-gate | spec-challenge | spec-lint | spec-retro | seq | tune | none
```

If no actionable automation rule exists, say so and retire the retro finding.

## Churn detector

If given plan files or session excerpts, use:

```bash
python codex/skills/spec-retro/scripts/spec_churn_detect.py plan-*.md
```

The script looks for title drift, repeated replacement language, high iteration markers, many open questions, objective-changing Round Delta text, repeated blocked states, high subagent counts, and campaign-mode triggers.

## Standard output

```text
SPEC RETRO
positive_exemplars:
warning_exemplars:
automation_rules:
gate_updates:
lint_updates:
challenge_updates:
receipt_updates:
subagent_budget_updates:
question_generator_updates:
next_measurement_plan:
```

Also emit `spec_retro_update`.

## Guardrails

- Do not mutate skill files unless the user explicitly asks for edits.
- Do not create process language with no automation rule.
- Do not count companion mentions as phase impact.
- Do not recommend standalone companion invocations merely to improve usage counts.
- Do not run as per-spec ceremony.
