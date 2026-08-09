---
name: refine
description: "Own and apply bounded, evidence-backed optimization of an existing Codex skill. Use after `$tune` supplies STE-v1/SDC-v2 or a complete REFINE-SKILL-v3 brief; inspect the target package, select the weakest valid intervention supportable by current evidence, realize it with the smallest authorized diff, preserve stable decision-contract IDs, and retain the named behavioral `$seq` observation query. Not for broad historical diagnosis or system-managed skill optimization."
---

# Refine

## Mission

`$refine` is the user-owned skill optimizer.

```text
$seq    gathers evidence
$tune   diagnoses the gap and expected decision delta
$refine owns package optimization and editing
```

Do not delegate optimization to a system-managed `skill-optimizer`.

`$refine` may use read-only evidence/modeling subagents supplied by the parent, but root owns all skill-package edits.

Keep two optimization questions separate:

```text
semantic selection   -> weakest valid intervention supportable by evidence
physical realization -> smallest authorized diff
```

A short edit can impose a strong, overfitted policy. A longer edit can preserve more lawful future behavior. Never use physical size as a proxy for semantic generality.

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
regression
```

### inspect

Inspect the target package against an already supplied brief.

Return the weakest viable intervention and outcome-observation plan.

No edits.

### apply

Default when explicit edit authority and a complete brief exist.

Inspect, select one weakest valid intervention, realize it minimally, and retain the outcome-observation query.

### regression

Repair a previously observed skill failure and install the weakest reproducible guard that excludes the witnessed failure class without unnecessarily constraining neighboring valid behavior.

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
    regression

  source_evidence:
    packet: STE-v1 | GSD-v2 | user-feedback | observed-behavior
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
  outcome_observation:
    query:
    evidence_limits: []
```

`smallest_change_hint` is advisory about physical implementation cost. It does not establish semantic weakness and cannot select the intervention.

Fail closed when the brief does not identify an expected delta and authorized surface.

## Package inspection

Read only:

```text
SKILL.md
agents/openai.yaml
references/decision-contract.json
brief-authorized references/
brief-authorized scripts/
brief-authorized assets/
```

Read `references/weakness-selection.md` whenever candidate interventions differ in semantic scope, a short edit would introduce a broad rule, or a regression guard risks overfitting one episode.

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
decision observability
duplication/deletion
semantic specificity and future-behavior extension
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
observability_refinement
consolidate_or_delete
blocked
```

A route may touch several files only when they form one coherent intervention, such as:

```text
SKILL.md rule
+ matching decision-contract clause
+ matching agent prompt
```

Do not combine unrelated improvements into one refinement.

## Weakness-first selection standard

Select by semantic weakness, then realize by physical minimality.

A candidate intervention is valid only when all hold:

- it produces the expected delta on the supplied evidence;
- it preserves protected contracts and known valid near-miss behavior;
- it stays inside the authorized package and intervention budget;
- it introduces no known contradiction, prohibited route, or unowned authority;
- its claimed effect remains observable through the named outcome query.

For a valid candidate `c`, let `E(c)` denote the future target-skill decision episodes still permitted by `c`, restricted by the protected contracts and available evidence. The paper defines weakness by extension cardinality, but `$refine` usually cannot enumerate all future episodes and must not fabricate a numeric weakness score. It therefore uses set-inclusion dominance as a conservative proof rule: candidate `a` is **provably weaker** than candidate `b` when `E(b)` is a proper subset of `E(a)`. Everything `b` permits remains permitted by `a`, while `a` avoids at least one additional restriction.

Among valid candidates, reject a semantically stronger candidate when a provably weaker valid candidate exists. When neither extension contains the other, preserve the candidates as incomparable unless bounded evidence or an explicit domain prior discriminates them; do not claim a globally weakest candidate. Never infer weakness from prose length, diff size, file count, clause count, or the route list order.

When exact extensions cannot be enumerated, use these operational tests:

- bind the rule to the witnessed trigger, clause, route, phase, or owner rather than a broader category;
- preserve behavior the evidence does not require changing;
- test protected near misses and counterexamples, not only the triggering episode;
- prefer a causal condition at the owning decision point over a blanket downstream prohibition;
- avoid exact wording, sequencing, or artifact requirements when a weaker outcome relation suffices;
- treat `always`, `never`, unconditional activation, and global bans as strong hypotheses requiring explicit evidence;
- identify incomparable candidates instead of manufacturing a total order;
- use an evidenced domain prior when future episodes are not plausibly uniform, and state that prior in the receipt.

The cited weakness result is conditional on a finite representational language, a well-defined extension, and a uniform task distribution. `$refine` uses it as a semantic-dominance discipline, not as proof that future skill invocations are uniformly distributed or that unenumerated extension sizes are known. See `references/weakness-selection.md`.

After semantic selection, use physical cost only to realize the selected rule or break a genuine semantic tie:

```text
1. no edit, when the current package already satisfies the brief or no mutation is justified within the supplied evidence and authority
2. delete or consolidate
3. clarify an existing trigger, rule, route, or stop condition
4. repair an existing artifact or operational surface
5. add one narrowly scoped reference
6. add a substantive operation
7. add a new decision-contract clause or receipt
```

Do not add observability merely because it is possible.

Do not add a script that merely grades skill prose.

## Stable contract preservation

When `references/decision-contract.json` exists:

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
- Prefer surgical replacements after semantic selection.
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
observed episode
trigger/clause/route involved
prior bad behavior
expected future behavior
reproduction query
```

The intervention should address the observed skill failure, not merely change wording. Constrain the witnessed failure class; do not install a broader ban unless the evidence and protected contracts require it.

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

## Outcome observation

Run the exact named `$seq` query when supported.

Historical sessions do not retroactively change. Retain the future live query
and do not claim that a text edit has already improved behavior.

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
  selection_basis:
    validity_gate:
    semantic_weakness:
    stronger_candidates_rejected: []
    incomparable_candidates: []
    domain_prior:
    physical_tie_breaker:
  files_inspected: []
  files_changed: []
  clauses_changed: []
  metadata_disposition:
    regenerated |
    updated |
    verified_unchanged |
    not_present
  outcome_observation:
    current_evidence:
    future_query:
  residual_uncertainty: []
  boundary:
    within_boundary: yes | no
    expected_delta_addressed: yes | no
```

Keep `selection_basis` compact. A single-candidate refinement may state why that candidate is valid and why no broader rule is required; do not invent ceremonial alternatives.

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

Selection:
- Weakness basis:
- Stronger candidates rejected:
- Incomparables / domain prior:
- Physical tie-breaker:

Changed:
- Files:
- Clauses:
- Metadata:

Outcome observation:
- Current evidence:
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
- Select the weakest valid intervention; use the smallest diff only after semantic selection.
- Do not equate short prose, few lines, or broad universal rules with semantic weakness.
- Preserve unrelated work.
- Preserve stable contract IDs.
- No observability artifact without a concrete need.
- Behavioral claims require behavioral evidence.
- Future observation must be named, not implied.
