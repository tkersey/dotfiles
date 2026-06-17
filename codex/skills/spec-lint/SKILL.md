---
name: spec-lint
description: "Lint generated implementation specs/proposed plans for missing non-goals, weak proof, unmapped requirements, absent rollback/abort criteria, unresolved material questions, missing primary invariant, missing receipts, unaccounted subagents, skipped challenge/fresh-eyes pass, oversized audit prose, plan churn, or missing spec_governance_receipt. Use for `$spec-lint`, lint this spec, implementation-ready plan checks, proof/rollback/traceability checks, SLINT-v1, or is this more plan or better plan."
metadata:
  version: "1.3.0"
---

# Spec Lint

## Mission

Decide whether a generated spec is ready for implementation handoff.

A spec is ready only if two competent implementers would produce materially similar solutions and know how to prove completion.

## Required checks

Fail if any are missing or vague:

- Objective
- Context / Current State
- Locked Decisions
- Scope
- Non-Goals
- Requirements
- Design / Implementation Approach
- Dependency-Ordered Implementation Sequence
- Requirement-to-Test Traceability
- Proof Commands
- Risks and Edge Cases
- Rollback / Abort Criteria
- Binary Done-State
- Invariant Challenge for balanced, strict, or campaign work
- Fresh-Eyes Pass for balanced, strict, or campaign work
- Spec Pipeline Receipt when linting `$spec-pipeline` output
- Spec Governance Receipt when linting a complete `$spec-pipeline` handoff

## Semantic lint rules

Fail or warn when:

- major requirement lacks a test, check, demo, benchmark, trace, or review proof;
- rollback says only "revert" without naming trigger or blast radius;
- open questions are material and lack owner/default/consequence;
- spec creates a second source of truth;
- plan changes objective in `Round Delta`;
- audit sections repeat rationale without changing implementer behavior;
- strictness profile is too weak for public API, migration, security, performance, or multi-wave campaigns;
- proof is scaffold-only when runtime behavior is the success criterion;
- `grill_rounds: 0` but no-grill justification is empty or generic;
- subagent budget or accounting is missing after fan-out;
- `blocked` appears without `blocked_receipt`;
- output permits mutation before gate, challenge, fresh-eyes, lint, and governance receipt pass.

## Output

```text
SPEC_READY: true|false
blocking_errors:
material_risks:
preferences:
missing_sections:
unmapped_requirements:
rollback_gaps:
proof_gaps:
receipt_gaps:
subagent_gaps:
churn_signals:
recommended_next_action: proceed_to_plan | return_to_grill | revise_spec | run_spec_challenge | campaign_checkpoint
```

Also emit:

```yaml
spec_lint_receipt:
  receipt_version: SLINT-v1
  verdict: pass | fail | skipped
  script_lint: passed | failed | skipped
  semantic_lint: passed | failed
  changed_spec: yes | no
  blocked_handoff: yes | no
  proof_gaps_found: []
  rollback_gaps_found: []
  unmapped_requirements_found: []
  receipt_gaps_found: []
  pass_no_delta: yes | no
```

## Script helper

```bash
python codex/skills/spec-lint/scripts/spec_lint.py --strict-receipts path/to/spec.md
```

The helper is structural. The model must still judge semantic quality.

## Hard rules

- Do not pass a complete `$spec-pipeline` handoff without `spec_governance_receipt`.
- Do not treat script pass as semantic pass.
- Do not call a spec ready if mutation would require unresolved decisions.
- Do not let lint become a long essay; emit receipt fields.
