# Spec 04 — `seq review-compiler-audit` projection

Order: 4 of 4.
Depends on: Specs 01–03.

## Purpose

Make `$resolve` authority transfer auditable from local session/controller
forensics. If `seq` cannot see the authority chain, future maintainers cannot
depend on it.

## Required summary fields

`seq review-compiler-audit --mode summary --format json` should expose:

```text
candidate_sessions
true_resolve_sessions
tuple_closed_sessions
terminal_closed_sessions
material_runs_total
material_runs_with_rac
material_runs_with_mutation_gate
material_runs_with_closure_gate
uncompiled_review_text_mutations
raw_delivery_mutations_while_active
state_only_apply_violations
state_only_commit_violations
state_only_push_violations
semantic_surface_before
semantic_surface_after
semantic_surface_delta
orphan_code_constructs
unmapped_proof_actions
wound_specific_tests
```

## Required run fields

`seq review-compiler-audit --mode runs --format jsonl` should expose one row per
candidate/material run with:

```text
session_id
run_id
repo
protocol
material
c3_required
c3_entered
c3_closed
delivery_closed
terminal_closed
compression_state
batches_total
kernel.accepted
potential.strict_progress
semantic_surface_delta
ac_rebased
rac.total
rac.valid
rac.mutation_allowed
mutation_gate.status
closure_gate.status
orphan_code_constructs
unmapped_proof_actions
wound_specific_tests
wound_specific_tests_class_mapped
```

## Falsifier query

Find a material run row in the target window with:

```text
c3_required=true
c3_entered=true
c3_closed=true
compression_state != NONE
batches_total > 0
kernel.accepted=true
potential.strict_progress > 0
delivery_closed=true
terminal_closed=true
closure_gate.status=passed
```

If no such row exists, report:

```text
no mechanically closed material resolve run found
```

## Contamination policy

Exclude current audit prompts, generated reports, quoted examples, and skill-body
schema examples from positive workflow evidence. Preserve projection limitations
separately from controller failures.
