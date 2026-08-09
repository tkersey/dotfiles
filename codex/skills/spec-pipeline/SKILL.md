---
name: spec-pipeline
description: "Turn ambiguous project, architecture, implementation, or product requests into decision-complete current specs whose consequential architecture is explicit, authority-bound, and proof-linked. Use full, gate-only, challenge-only, or repair mode; default complete full-mode work to spec_to_plan and tail-call $plan only when the governed handoff authorizes it. Never implement or emit a proposed_plan block."
metadata:
  version: "2.3.0"
  activation_cost: adaptive
  default_depth: balanced
  requires_explicit_invocation: false
---
# Spec Pipeline

## Mission

Compile accepted intent into one decision-complete implementation specification,
then transfer planning authority only when the final governance state permits it.

## Mode and lane

Choose one mode before deep work:

```text
full            create or materially reconstruct the spec
gate-only       decide readiness without generating a spec or plan
challenge-only  return one strongest invariant pressure test
repair          change only implicated sections, then rerun downstream phases
```

For `full`, default the lane to `spec_to_plan`. Use `spec_only` only for an
explicit no-plan request or a material blocker.

## Common path

1. Research available artifacts before asking questions.
2. Bind the authoritative target, scope, non-goals, compatibility, proof bar,
   rollout/rollback posture, and public behavior boundary.
3. Ask only for material judgment or unavailable context; otherwise emit a
   no-grill justification.
4. Recover an Architectonic Thread for every consequential seam:
   authority class, owner, candidate, law, falsifier, compatibility, proof, and
   invalidators.
5. Compile the decision packet and run the pre-spec gate.
6. Emit the implementation spec.
7. Run one strongest invariant challenge and one fresh-eyes pass.
8. Repair only invalidated sections and their downstream consequences.
9. Produce the governed terminal state.
10. Tail-call `$plan` in the same turn only when status, lane, gate, handoff,
    next owner, and do-not-execute conditions all authorize it.

A consequential obstructed seam is valid documentation of a blocker, never
planning readiness.

## Authority boundary

`$spec-pipeline` owns accepted specification semantics and
specification-local architectonic decisions. `$plan` owns execution-policy
synthesis. This skill does not mutate repository product files, grant execution,
or select an implementation consumer.

## Conditional disclosure

The complete pre-split contract is preserved byte-for-byte in
[FULL_CONTRACT.md](FULL_CONTRACT.md). Do not load it for gate-only or a narrow
challenge.

Load it only for:

- profile budgets and full phase mechanics;
- exact Evidence Brief, decision-packet, implementation-spec, SGR-v2, or PSC-v1
  schemas;
- Architectonic Thread and specification-square calculus;
- Ledger validation commands and definition digests;
- repair propagation, governance, or automatic plan-handoff detail;
- an unported edge route.

Its frontmatter is archived source, not a second skill definition.

## Guardrails

- Never ask for discoverable facts.
- Never drift target, scope, authority, compatibility, proof, or non-goals
  without explicit approval.
- Never use a phase pass with no decision delta as success theater.
- Never silently convert an eligible `spec_to_plan` result to `spec_only`.
- Never implement.
