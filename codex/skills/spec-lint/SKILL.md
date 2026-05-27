---
name: spec-lint
description: "Lint generated implementation specs/proposed plans for missing non-goals, weak proof, unmapped requirements, absent rollback/abort criteria, unresolved material questions, missing primary invariant, oversized audit prose, or plan churn. Use for `$spec-lint`, lint this spec, implementation-ready plan checks, proof/rollback/traceability checks, or is this more plan or better plan."
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

## Semantic lint rules

Fail or warn when:

- a major requirement lacks a test, check, demo, benchmark, trace, or review proof;
- rollback says only "revert" without naming trigger or blast radius;
- open questions are material and lack owner/default/consequence;
- the spec creates a second source of truth;
- the plan changes objective in `Round Delta`;
- audit sections repeat rationale without changing implementer behavior;
- strictness profile is too weak for public API, migration, security, performance, or multi-wave campaigns;
- proof is scaffold-only when runtime behavior is the success criterion.

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
churn_signals:
recommended_next_action: proceed_to_execution | return_to_grill | revise_spec | run_spec_challenge
```

## Script helper

```bash
python codex/skills/spec-lint/scripts/spec_lint.py path/to/spec.md
```

The helper is structural. The model must still judge semantic quality.
