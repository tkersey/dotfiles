---
name: refine
description: "Own and apply bounded, evidence-backed optimization of an existing Codex skill. Use after `$tune` supplies STE-v1/SDC-v2 or a complete REFINE-SKILL-v3 brief; inspect the target package, select one smallest intervention, edit only authorized files, preserve stable decision-contract IDs, and validate static structure, contract consistency, and the named behavioral `$seq` query. Not for broad historical diagnosis or system-managed skill optimization."
---

# Refine

## Mission

`$refine` is the user-owned skill optimizer.

```text
$seq    gathers evidence
$tune   diagnoses the gap and expected decision delta
$refine owns package optimization, editing, and validation
```

Do not delegate optimization to a system-managed `skill-optimizer`.

`$refine` may use read-only evidence/modeling subagents supplied by the parent, but root owns all skill-package edits.

## Activation boundary

Use `$refine` when the user explicitly authorizes skill changes and one of these exists:

```text
STE-v1 + SDC-v2
REFINE-SKILL-v3 brief
explicit current-turn defect with a complete edit boundary
```

Do not use `$refine` to decide whether a skill should change.

Return to `$tune` when:

- the gap is not established;
- the expected decision/execution delta is unclear;
- the target skill or allowed files are unknown;
- historical evidence still needs interpretation;
- the request is proposal-only.

## Modes

Choose exactly one:

```text
inspect
apply
validate
regression
```

### inspect

Inspect the target package against an already supplied brief.

Return the smallest viable intervention and validation plan.

No edits.

### apply

Default when explicit edit authority and a complete brief exist.

Inspect, select one intervention, edit, and validate.

### validate

Run static, decision-contract, script/test, and behavioral validation without changing files.

### regression

Repair a previously observed skill failure and install the smallest reproducible guard.

## Required input

Preferred:

```yaml
refine_brief:
  brief_version: REFINE-SKILL-v3
  target_skill:
  target_kind:
    decision |
    execution |
    evidence |
    orchestration |
    mixed
  mode:
    inspect |
    apply |
    validate |
    regression

  source_evidence:
    packet: STE-v1 | GSD-v2 | user-feedback | validation
    refs: []

  gap:
    signature:
    type:
    clause_refs: []
    evidence_strength:
    recurrence:

  expected_delta:
    from:
    to:

  optimization_boundary:
    allowed_files: []
    forbidden_files: []
    protected_contracts: []
    intervention_budget:
      max_files:
      max_new_scripts:
      max_new_references:
      max_new_contract_clauses:
    forbidden_changes: []

  smallest_change_hint:
  validation:
    static: []
    contract: []
    scripts_or_tests: []
    behavioral_query:
    success_criteria: []
```

Fail closed when the brief does not identify an expected delta and authorized surface.

## Package inspection

Read only:

```text
SKILL.md
agents/openai.yaml
references/decision-contract.yaml
brief-authorized references/
brief-authorized scripts/
brief-authorized assets/
brief-authorized tests/
```

Also inspect repository-local skill conventions required for validation.

Check the worktree before mutation.

Do not mine broad historical sessions inside `$refine`.

## Optimization dimensions

Evaluate only dimensions relevant to the brief:

```text
trigger precision
non-trigger boundary
decision rule
route ownership
mode routing
stop/terminal state
required artifact or receipt
handoff contract
tooling surface
reference/resource placement
metadata/default prompt
validation probe
decision observability
duplication/deletion
```

Do not optimize for prose elegance alone.

## Intervention routes

Select exactly one dominant route:

```text
no_change
trigger_refinement
boundary_refinement
decision_rule_refinement
routing_refinement
workflow_refinement
artifact_refinement
tooling_refinement
resource_refinement
metadata_refinement
validation_refinement
observability_refinement
consolidate_or_delete
blocked
```

A route may touch several files only when they form one coherent intervention, such as:

```text
SKILL.md rule
+ matching decision-contract clause
+ matching agent prompt
+ one regression fixture
```

Do not combine unrelated improvements into one refinement.

## Selection standard

Choose the smallest route that can plausibly produce the expected delta.

Compare candidate interventions in this order:

```text
1. no edit
2. delete or consolidate
3. clarify existing trigger/rule/route
4. repair an existing artifact or validation surface
5. add one narrowly scoped reference/probe
6. add a deterministic script
7. add a new decision-contract clause or receipt
```

Do not add observability merely because it is possible.

Do not add a script for behavior that clear prose plus existing validation can govern.

## Stable contract preservation

When `references/decision-contract.yaml` exists:

- preserve trigger, route, and clause IDs;
- never renumber for formatting;
- update only brief-named clauses or clauses necessarily changed by the intervention;
- keep expected/prohibited routes synchronized with `SKILL.md`;
- preserve superseded IDs when historical evidence depends on them;
- change `source_fingerprint` after the final package state is known when the local convention supports it.

When no contract exists:

- do not add one by default;
- add SKDC-v1 only when the brief identifies a decision-contract or observability gap;
- keep the contract small and consequential.

## Editing policy

- Edit only allowed files.
- Preserve unrelated user changes.
- Prefer surgical replacements.
- Keep `SKILL.md` under 500 lines.
- Move schemas and long examples to references/assets.
- Keep frontmatter minimal and valid.
- Keep `agents/openai.yaml` aligned with the final trigger and mission.
- Do not add README/INSTALL/CHANGELOG files inside a skill package.
- Do not add network dependencies, secrets, hidden global state, or nondeterminism.
- Do not commit or push unless explicitly delegated.

## Regression policy

For a known failure, bind:

```text
observed episode or fixture
trigger/clause/route involved
prior bad behavior
expected future behavior
reproduction query or test
```

The regression guard should catch the skill failure, not merely detect changed wording.

Examples:

```text
trigger-present but missed activation
prohibited route selected
repeated no-visible-delta ceremony
wrong terminal state
missing required artifact
manual workaround repeated
```

## Decision receipt instrumentation

A decision-oriented skill may emit:

```text
skill_decision_receipt / SDR-v1
```

Add or require it only when:

- the skill makes a consequential route decision;
- current traces cannot recover the decision reliably;
- the receipt records selected and rejected alternatives;
- the output cost is proportionate;
- the brief identifies observability as the gap.

An SDR receipt is not proof of a good outcome.

## Validation stack

### Static package validation

Always run after edits:

```bash
uv run --with pyyaml -- python3 \
  codex/skills/.system/skill-creator/scripts/quick_validate.py \
  codex/skills/<skill>
```

### Decision-contract validation

When SKDC-v1 exists:

```bash
python3 codex/skills/tune/tools/decision_contract_lint.py \
  codex/skills/<skill>/references/decision-contract.yaml
```

### Script/test validation

Run every brief-authorized changed script or fixture.

Use representative positive and negative cases.

### Behavioral validation

Run the exact named `$seq` query when supported.

Historical sessions do not retroactively change. Behavioral validation may therefore be:

```text
fixture validation now
future live-query retained
```

Do not claim future behavior already improved.

## Skill Refinement Receipt

Every apply/regression run emits:

```yaml
skill_refinement_receipt:
  receipt_version: SRR-v1
  target_skill:
  target_kind:
  source_evidence:
  gap_signature:
  expected_delta:
    from:
    to:
  selected_route:
  alternatives_rejected: []
  files_inspected: []
  files_changed: []
  clauses_changed: []
  metadata_disposition:
    regenerated |
    updated |
    verified_unchanged |
    not_present
  validation:
    static:
    contract:
    scripts_or_tests:
    behavioral:
  future_validation_query:
  residual_uncertainty: []
  gate:
    within_boundary: yes | no
    expected_delta_addressed: yes | no
    validation_passed: yes | no
```

Do not emit `validation_passed: yes` when future live evidence is still required. Use:

```text
static_and_fixture_passed; future_behavior_pending
```

in the validation detail and preserve the query.

## Optional read-only subagents

The parent may supply:

```text
skill_contract_modeler
skill_decision_provenance_auditor
skill_outcome_skeptic
```

They provide evidence or skepticism only.

They do not edit files.

`$refine` root remains the sole writer.

## Output

```text
Refined:
- Target:
- Target kind:
- Mode:
- Gap signature:
- Expected delta:
- Selected route:

Changed:
- Files:
- Clauses:
- Metadata:

Validation:
- Static:
- Contract:
- Scripts/tests:
- Behavioral:
- Future query:

Receipt:
- SRR-v1:

Residual uncertainty:
```

## Hard rules

- `$tune` diagnoses; `$refine` optimizes.
- Do not use or modify a system-managed `skill-optimizer`.
- Root owns all edits.
- No complete brief, no mutation.
- One dominant intervention per refinement.
- Minimal diff.
- Preserve unrelated work.
- Preserve stable contract IDs.
- No observability artifact without a concrete need.
- Static validation is mandatory.
- Behavioral claims require behavioral evidence.
- Future validation must be named, not implied.
