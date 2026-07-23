---
name: opt
description: "Orchestrate evidence-backed optimization of user-owned Codex skills through $seq or $shadow evidence, $tune diagnosis, and $refine package editing and outcome observation. Use for explicit skill audits, missed/false/ceremonial activation, decision-contract tuning, regression repair, or authorized skill edits. Not for application-code optimization or autonomous portfolio mutation."
---

# opt

## Mission

Coordinate the user-owned skill-improvement loop without blurring authority:

```text
$seq      historical and session evidence
$shadow   one watched-session delta
$tune     diagnosis and expected decision delta
$refine   sole skill-package writer
$opt      orchestration and final synthesis
```

Core question:

```text
What is the smallest evidence-backed change that improves future decisions,
execution, evidence quality, or orchestration?
```

## Activation boundary

`$opt` is explicit-intent. Generic uses of “optimize,” “improve,” or “tune” for application code do not activate it.

Skill-package mutation requires explicit edit authority. Ambiguous improvement requests default to proposal-only.

## Modes

Choose exactly one:

```text
audit
propose
tune
shadow-diagnose
apply
regression
goal-loop
```

Defaults:

```text
ambiguous optimize -> propose
edit authority      -> absent
```

## Target type

Carry one type through the workflow:

```text
decision
execution
evidence
orchestration
mixed
```

Evaluate the type with its relevant evidence:

- decision: route influence, clause compliance, rejected alternatives, downstream outcome;
- execution: handoff fidelity, surface budget, proof, rework;
- evidence: coverage, precision, provenance, false results;
- orchestration: phase correctness, handoff completeness, terminal state, loop efficiency.

## Evidence routing

### Historical or multi-session evidence

Prefer:

```bash
seq skill-decision-audit \
  --skill <skill> \
  --last 30d \
  --exclude-current \
  --mode tune-packet \
  --format json
```

Pass `STE-v1` to `$tune`.

### One watched session

Use `$shadow` over exactly one target skill, one root session, and one cursor. Pass `GSD-v2` or watched-session `STE-v1` to `$tune`. Do not infer recurrence from one session.

### Direct user feedback

Use current-turn evidence first. Do not mine history to overrule an explicit correction.

## Workflow

### Audit

1. Identify the target and target type.
2. Read the target package and decision contract when present.
3. Gather the least evidence needed.
4. Use read-only specialists only for unresolved route-changing uncertainty.
5. Return findings; do not edit.

Optional read-only roles:

```text
skill_contract_modeler
skill_decision_provenance_auditor
skill_outcome_skeptic
```

### Propose

1. Produce or consume `STE-v1`.
2. Invoke `$tune` in proposal mode.
3. Select one dominant `SDC-v2` delta or a terminal no-action state.
4. Include the exact outcome-observation query.
5. Stop without editing.

### Apply

Use only with explicit edit authorization and a complete `REFINE-SKILL-v3` brief.

`$refine` owns:

```text
target-package inspection
one dominant intervention
authorized edits
stable contract preservation
outcome-observation query
SRR-v1
```

The root owns final synthesis. Custom agents do not write skill packages.

### Regression

Bind the repair to:

```text
observed episode
trigger / clause / route
prior bad behavior
expected future behavior
reproduction query
```

Apply the smallest intervention that addresses the behavioral failure rather than changed wording.

### Goal loop

When `$cas` owns continuation:

```text
new evidence
-> tune delta
-> refine action
-> outcome observation
-> parent goal decision
```

No evidence delta means no repeated full optimization cycle.

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
  outcome_observation:
```

Rules:

- preserve stable clause IDs;
- do not reinterpret the evidence packet;
- do not broaden allowed files;
- select one dominant intervention;
- do not commit or push without explicit delegation;
- require `SRR-v1`.

## Completion bar

Optimization is complete only when:

- target and type are explicit;
- evidence source and denominator are explicit;
- expected delta is explicit;
- `$tune` selected one bounded route;
- `$refine` stayed inside the authorized package surface;
- stable contract IDs were preserved;
- the outcome claim is bounded by current evidence;
- an exact future observation query is retained when current evidence cannot show the effect;
- `SRR-v1` was emitted;
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
- Outcome observation:
- SRR-v1:
- Parent goal status:
- Remaining uncertainty:
- Next action:
```

## Hard rules

- `$seq` owns historical/session evidence.
- `$shadow` owns one-session monitoring.
- `$tune` owns diagnosis.
- `$refine` is the sole skill-package writer.
- `$opt` owns orchestration and final synthesis.
- No raw mention inflation.
- No causal claim from co-occurrence.
- No edit from weak evidence.
- No broad scan without a target.
- No repeated cycle without evidence delta.
- No apply without a complete refine brief and explicit edit authority.
