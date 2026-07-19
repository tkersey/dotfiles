---
name: review-fold
description: "Classify and quotient review findings, failing tests, production incidents, user-reported bugs, migration or compatibility failures, and other witnessed falsifiers against accepted intent and the current construction. Use before review resolution to author counterexample-set/v1 for artifact-kernel goals: separate facts from suggested repairs, reject non-liabilities with evidence, assign stable law-and-boundary class identity, and emit no mutation authority. Read RF-v2 only for explicitly marked legacy goals."
---

# Review Fold

## Mission

Turn review pressure into pure classified evidence.

~~~text
review or failure evidence + Goal Contract + current Construction Contract
-> Counterexample Set
-> no-code disposition or successor-Construction input
~~~

`$review-fold` owns classification and quotienting. It does not choose a
construction, count clean attempts, grant mutation, publish, or decide closure.

## Minimal law

~~~text
claim != observed fact
observed fact != liability
liability != accepted scope
accepted scope != selected repair
Counterexample Set != mutation authority
~~~

Keep suggested repairs in their source evidence. Never copy a suggestion into
`observed_facts`, `witness`, `quotient_basis`, or another field that presents it
as fact.

## Counterexample Set v1

For a goal marked `protocol: artifact-kernel-v1`, author this immutable
artifact:

~~~yaml
artifact:
  schema: counterexample-set/v1
  artifact_id: sha256:<content-addressed-id>
  goal_id:
  semantic_author: review-fold
  created_at:
  predecessor_refs: []
  supporting_refs:
    - review-attempt-event-or-failure-evidence-ref

  payload:
    subject:
      construction_ref:
      repository:
      artifact_digest:
      review_contract_digest:

    classes:
      - class_id:
        boundary_key:
        law_ref:
        discrepancy: excess | deficit | incoherence | partiality | misbinding
        owner_boundary:
        severity: critical | high | medium | low
        status: accepted | rejected | blocked | follow-up
        observed_facts: []
        evidence_refs: []
        finding_refs: []
        witness:
        falsifier_ref:
        applicability:
        quotient_basis:
~~~

Use canonical JSON for materialization. Compute `artifact_id` from the canonical
artifact bytes with `artifact_id` excluded, following the common artifact
envelope contract. Unknown fields fail closed unless a versioned extension
allows them.

A clean source may yield no classes. Review events, not this artifact, own
attempt history and clean credit.

## Class identity and statuses

Define one class as one stable counterexample to one governing law at one owner
boundary:

~~~text
class identity = governing law + semantic boundary + discrepancy + applicability
~~~

Use `quotient_basis` to state why the grouped findings witness that same class.
Do not derive class identity from filenames, commits, attempt IDs, request IDs,
publication epochs, or a proposed patch. A class may recur across construction
successors while its finding and evidence references change.

- `accepted`: evidence establishes an in-scope counterexample. Require a
  successor Construction Contract before mutation.
- `rejected`: evidence establishes that the claim is false, stale, already
  satisfied, preference-only, unrelated, or a duplicate already represented by
  another class. Record the rejection evidence.
- `blocked`: validity, ownership, subject binding, law binding, or evidence is
  insufficient. Do not infer the missing fact.
- `follow-up`: the counterexample is valid but outside the current Goal
  Contract. Preserve it without expanding current authority.

An accepted class requires nonempty observed facts, witness, evidence,
falsifier, law, boundary, applicability, and quotient basis. A rejected class
requires evidence that establishes the rejection. Duplicate findings normally
collapse into one class rather than producing one class per comment.

## Procedure

Before the first Ledger command in the workflow, load `$ledger` and complete
`$ledger ensure`.

1. Read the immutable goal protocol marker. Never mix legacy and artifact-kernel
   semantics within one goal.
2. Bind the source to the current Goal Contract, Construction Contract, subject
   digest, repository, and static Review Contract digest.
3. Separate each claim, observed fact, and suggested repair. Retain the
   suggestion only in source evidence.
4. Determine the governing law, owner boundary, discrepancy, applicability,
   witness, falsifier, evidence, severity, and status.
5. Quotient duplicate and same-class findings using semantic identity rather
   than implementation coordinates.
6. Require evidence for every accepted or rejected class. Leave uncertainty
   `blocked`.
7. Materialize canonical `counterexample-set/v1` JSON and validate it with
   `ledger validate counterexample-set --input <counterexample-set-json-file>`.
8. Register the validated artifact in the Evidence Ledger when the current
   artifact-kernel workflow calls for it.
9. Hand accepted classes to `$actuating` as successor Construction Contract
   inputs. Never choose or authorize the repair.

Use
[counterexample-set.valid.example.json](assets/counterexample-set.valid.example.json)
as a shape example, not as reusable evidence or authority.

## Legacy compatibility

Read or author RF-v2 only when the canonical Evidence Ledger admits the current
goal as `legacy-actuating-v1` and it remains inside its compatibility window.
Production Phase 3 blocks new artifact-kernel admission pending the complete
historical custom-store inventory; never infer protocol from a nearby artifact
or selected legacy path. Preserve the frozen legacy shape and validate it with
`ledger validate review-fold`; do not convert an in-flight goal, attach a
Counterexample Set to it, or emit RF-v2 for an artifact-kernel goal. Historical
RF-v2 remains evidence, not Counterexample Set identity or authority.

Use [review-fold.valid.example.json](assets/review-fold.valid.example.json) only
as a frozen legacy shape example. It is not current evidence or authority.

## Guardrails

- Do not select a repair, architecture candidate, work node, or operation plan.
- Do not emit clean-streak, request-state, publication, or closure state.
- Do not grant mutation; a validated Counterexample Set grants none.
- Do not turn style, speculation, or a suggested patch into a witnessed fact.
- Do not accept scope expansion without source authority.
- Do not use review prose, commits, or attempt IDs as class identity.
- Do not omit rejection evidence.
- Preserve source identity, current construction binding, and current subject
  binding.
- Treat Ledger validation as pure structural evidence. It neither establishes
  semantic truth nor authorizes execution.
