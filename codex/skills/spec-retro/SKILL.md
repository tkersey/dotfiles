---
name: spec-retro
description: "Historical learning skill for the specification system. Mine multiple prior specs, SGR-v2 receipts, plans, sessions, reports, and churn evidence into concrete updates to `$spec-pipeline` contracts, tools, subagent policy, exemplars, and measurement. Use for `$spec-retro`, improve my spec process from history, analyze spec usage reports, mine plan churn, missing phase impact, repeated gate/challenge/lint failures, or report-to-automation work. Do not use for producing or linting one current spec."
metadata:
  version: "2.0.0"
  activation_cost: medium
  default_depth: balanced
---

# Spec Retro

## Mission

`$spec-retro` improves the specification system from observed practice.

It is separate from `$spec-pipeline` because it operates across:

- multiple prior sessions;
- multiple prior specs;
- plans and execution outcomes;
- governance receipts;
- reports and telemetry;
- exemplar libraries;
- repeated failure patterns.

Its output is not a current implementation spec.

Its highest-value output is a small set of:

- pipeline gate-rule updates;
- challenge-rule updates;
- fresh-eyes updates;
- lint-rule updates;
- mode-routing updates;
- governance-receipt updates;
- tool updates;
- subagent-policy updates;
- exemplar updates;
- measurement updates.

Do not produce more process prose without an actionable rule or measurement.

## Trigger policy

Use when any are true:

- 5 or more full `$spec-pipeline` runs since the last retro;
- 2 or more repeated gate/challenge/fresh-eyes/lint failures;
- a report shows phase impact is invisible;
- execution started before readiness;
- plan or objective churn recurs;
- no-grill justifications are repeatedly generic;
- subagent fanout repeatedly has no impact;
- strictness profiles are repeatedly mismatched;
- current reports cannot distinguish pass-no-delta from route-changing phases.

Do not run after every spec.

## Inputs

Use any available:

- `spec_governance_receipt` / SGR-v2 records;
- full spec outputs;
- plan artifacts;
- `$grill-me` snapshots;
- execution outcomes;
- `$spec-pipeline` reports;
- session history;
- `seq` results;
- `.learnings.jsonl`;
- user-supplied retrospective reports.

## Evidence discipline

Separate:

```yaml
retro_evidence:
  observed_pattern:
  supporting_sources: []
  counterevidence: []
  confidence:
  proposed_automation:
  expected_metric_change:
```

Do not infer a system-wide rule from one ambiguous session.

## Churn detection

When given multiple plan/spec files, run:

```bash
python codex/skills/spec-retro/scripts/spec_churn_detect.py <files...>
```

The helper is heuristic. The model still judges whether churn is material.

## Output

Emit one compact object:

```yaml
spec_retro_update:
  update_version: SRETRO-v2
  report_window: "..."
  trigger:
    reason: "..."
    evidence_refs: []
  observed_patterns:
    - pattern: "..."
      confidence: high | medium | low
      counterevidence: []
  pipeline_updates:
    mode_routing: []
    gate_contract: []
    challenge_contract: []
    fresh_eyes_contract: []
    lint_contract: []
    governance_receipt: []
    output_templates: []
  tool_updates:
    spec_gate: []
    spec_lint: []
    sgr_gate: []
    churn_detector: []
  subagent_policy_updates: []
  exemplar_updates: []
  measurement_updates:
    - metric: "..."
      baseline: "..."
      expected_change: "..."
      next_report_query: "..."
  recommendations:
    keep: []
    revise: []
    retire: []
  apply_now: yes | no
  next_owner: spec-pipeline | spec-retro | tune | seq | user | none
```

## Decision standard

A proposed change is useful only if it can later be graded.

Every recommendation must specify:

```text
hypothesis
expected behavioral change
metric
next report query
keep/revise/retire condition
```

## Subagent use

Preferred historical worker:

```text
spec_retro_miner
```

Use it only when evidence spans enough artifacts to benefit from a separate historical pass.

The root owns synthesis and recommendation.

## Guardrails

- Do not create a current implementation spec.
- Do not lint or challenge one current spec as the primary task.
- Do not mutate skill files unless explicitly asked.
- Do not chase old standalone companion-skill activation counts.
- Do not turn phase pass-no-delta into success theatre.
- Do not propose a process rule with no future measurement.
- Do not run as per-spec ceremony.

## Resources

- [trigger-policy.md](references/trigger-policy.md)
- [retro-update-schema.md](references/retro-update-schema.md)
- [measurement-contract.md](references/measurement-contract.md)
- [exemplar-contract.md](references/exemplar-contract.md)
