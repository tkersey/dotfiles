---
name: plan
description: "Synthesize accepted intent or a $spec-pipeline PSC-v1 source contract into one source-bound, architecture-aware EPG-v1 plan with a stable plan_id. Use for $plan, spec-to-plan lowering, adaptive probes, stabilization plans, and plan revision. Preserve source authority; never mutate implementation state, author runtime state, grant mutation, require another architecture skill, or silently select an existing plan."
---
# Plan

## Mission

Compile accepted intent into one canonical architecture-aware execution policy.
Architecture is part of the policy, not a review added after actions are chosen.

## Common path

1. Start from direct accepted intent, a valid PSC-v1 handoff, or an explicit
   revision request for one known plan identity.
2. Preserve source-owned semantics, scope, non-goals, compatibility, proof bar,
   and source-fixed architecture.
3. Classify architecture seams as source-fixed, source-bounded, or plan-local.
4. Synthesize architecture, observations, guarded actions, proof, rollback, and
   terminal states together.
5. Refine until no source-authorized policy or architecture improvement remains.
6. Emit one EPG-v1 with a stable plan identity.
7. Validate its structure through Plan's passive Ledger definition when
   persistence is useful.
8. Stop before execution.

Plan owns no runtime state, implementation mutation, decision receipt,
transition receipt, or consumer selection.

## Artifact economy

When persisted, the sole authoritative Plan artifact is
`.ledger/plan/<plan-id>/policy.json`. Human prose is an on-demand projection,
not a second plan. A materially different objective receives a new identity.

## Conditional disclosure

The complete pre-split contract is preserved byte-for-byte in
[FULL_CONTRACT.md](FULL_CONTRACT.md). Do not load it for a simple direct plan.
Load it only for exact PSC-v1 admission fields, EPG-v1 schema and revision
semantics, planning-regime detail, Ledger commands, full output requirements, or
an unported edge route. Its frontmatter is archived source, not a second skill
definition.

## Output

Return one proposed-plan block whose prose projects exactly one fenced EPG-v1
JSON object. Do not emit a separate gate, handoff, receipt, runtime-state, or
decision artifact.
