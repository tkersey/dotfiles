---
name: opt
description: "Orchestrate user-owned skill optimization through `$seq` decision evidence, `$shadow` one-session deltas, `$tune` diagnosis, and `$refine` package optimization. Use for `$opt`, session-driven skill improvement, false/missed/ceremonial activation, decision-contract tuning, STE-v1 review, regression repair, or explicitly requested validated skill edits. Not for application-code optimization, system-managed optimizer modification, or autonomous ecosystem-wide scans."
---

# opt

## Mission

Coordinate the user-owned skill-improvement loop without blurring ownership.

```text
$seq      historical and session evidence
$shadow   one watched-session delta
$tune     diagnosis and expected decision delta
$refine   skill-package optimization, editing, and validation
$cas      optional parent goal lifecycle
```

Do not invoke, modify, or depend on a system-managed `skill-optimizer`.

## Core question

```text
What is the smallest evidence-backed skill change that improves future
decisions, execution, evidence quality, or orchestration?
```

## Modes

```text
audit
propose
tune
shadow-diagnose
apply
validate
regression
goal-loop
```

Ambiguous “optimize” defaults to:

```text
propose
no edit
```

## Target skill type

Carry one target type through the workflow:

```text
decision
execution
evidence
orchestration
mixed
```

Evaluate accordingly:

- decision -> route influence, clause compliance, outcome association;
- execution -> handoff fidelity, proof, rework, surface;
- evidence -> coverage, precision, provenance, false results;
- orchestration -> lifecycle, handoff, stop/terminal correctness;
- mixed -> name the applicable dimensions.

## Evidence routing

### Historical use

Prefer:

```bash
seq skill-decision-audit \
  --skill <skill> \
  --last 30d \
  --exclude-current \
  --mode tune-packet \
  --format json
```

Pass STE-v1 to `$tune`.

### One watched session

Use `$shadow` with:

```text
one root session
one target skill
one cursor
```

Pass GSD-v2 or watched-session STE-v1 to `$tune`.

### Direct user feedback

Use current-turn evidence first.

Do not mine history merely to overrule explicit feedback.

## Audit

1. Identify target and type.
2. Read the target package.
3. Gather the least evidence needed.
4. Use read-only specialists only when needed:
   ```text
   skill_contract_modeler
   skill_decision_provenance_auditor
   skill_outcome_skeptic
   ```
5. Return findings only.

No edits.

## Propose

1. Produce or consume STE-v1.
2. Run `$tune`.
3. Select one dominant SDC-v2 delta or terminal no-action state.
4. Include the exact validation query.
5. Stop at proposal.

No edits.

## Tune

1. Require:
   ```text
   target
   target kind
   evidence source
   mode
   apply policy
   ```
2. Use `$tune` for diagnosis.
3. Produce:
   ```text
   SDC-v2
   REFINE-SKILL-v3 brief
   terminal no-action/repeat state
   or seq special-spec handoff
   ```
4. Do not pass broad raw transcripts to `$refine` when STE-v1 exists.

## Shadow diagnose

1. Use `$shadow` on exactly one watched session.
2. Stop when no decision-relevant evidence changed.
3. Escalate to `$tune` only for a concrete gap.
4. Do not infer historical recurrence from one session.

## Apply

Use only with explicit edit authorization.

Require a complete:

```text
REFINE-SKILL-v3
```

Then invoke `$refine` in `apply` or `regression` mode.

`$refine` owns:

```text
target-package inspection
intervention selection
edits
contract preservation
static validation
script/fixture validation
behavioral validation query
SRR-v1
```

Root `$opt` owns orchestration and final synthesis.

## Validate

Ask `$refine` to validate:

```text
static package
decision contract
changed scripts/tests
behavioral query or future query
```

Historical behavior does not retroactively change.

Distinguish:

```text
validation passed now
future behavioral validation pending
```

## Regression

For a known skill failure:

1. identify the episode or fixture;
2. identify trigger/clause/route;
3. state prior bad behavior;
4. state expected future behavior;
5. produce a bounded REFINE-SKILL-v3 brief;
6. run `$refine regression`;
7. retain the exact recurrence query.

## Goal loop

When `/goal` or `$cas` owns continuation:

```text
new evidence
-> tune delta
-> refine action
-> validation
-> parent goal decision
```

No evidence delta means no full optimization cycle.

## Refine handoff

```yaml
refine_brief:
  brief_version: REFINE-SKILL-v3
  target_skill:
  target_kind:
  mode:
  source_evidence:
  gap:
  expected_delta:
  optimization_boundary:
    allowed_files: []
    forbidden_files: []
    protected_contracts: []
    intervention_budget:
    forbidden_changes: []
  smallest_change_hint:
  validation:
```

Rules:

- preserve stable clause IDs;
- do not reinterpret the evidence packet;
- do not broaden allowed files;
- one dominant intervention;
- no commit/push unless explicitly delegated;
- require SRR-v1.

## Subagents

### skill_contract_modeler

Read-only contract modeling.

### skill_decision_provenance_auditor

Read-only attribution and denominator audit.

### skill_outcome_skeptic

Read-only challenge to causal/outcome claims.

No workspace-writing optimization subagent is required.

`$refine` root is the sole skill-package writer.

## Completion bar

Do not call optimization complete until:

- target and type are explicit;
- evidence source and denominator are explicit;
- expected delta is explicit;
- `$tune` selected one bounded route;
- `$refine` stayed within the authorized package surface;
- stable contract IDs were preserved;
- static validation passed;
- contract validation passed when applicable;
- changed scripts/tests passed;
- behavioral validation passed or its exact future query is retained;
- SRR-v1 was emitted;
- residual uncertainty is stated.

## Output

```text
$opt result:
- Target:
- Target kind:
- Mode:
- Evidence packet:
- Tune delta:
- Refine route:
- Files changed:
- Static validation:
- Contract validation:
- Script/test validation:
- Behavioral validation:
- SRR-v1:
- Parent goal status:
- Remaining uncertainty:
- Next action:
```

## Hard rules

- `$seq` owns evidence.
- `$shadow` owns one-session monitoring.
- `$tune` owns diagnosis.
- `$refine` owns user skill optimization and edits.
- Do not modify or depend on system-managed optimization agents.
- No raw mention inflation.
- No causal claim from co-occurrence.
- No edit from weak evidence.
- No broad scan without a target.
- No repeated full cycle without evidence delta.
- No apply without a complete refine brief.
