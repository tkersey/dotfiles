---
name: review-fold
description: "Classify and quotient review findings, failing tests, incidents, bug reports, migration failures, and other witnessed falsifiers against accepted intent and the current Construction. Author counterexample-set/v1 without selecting repairs, counting review credit, or granting mutation."
---

# Review Fold

## Mission

Turn witnessed falsification pressure into one immutable classified-bug
artifact.

~~~text
review or failure source + Goal Contract + current Construction
-> counterexample-set/v1
-> no mutation authority
~~~

`$review-fold` owns fact classification, disposition, and quotienting.
`$actuating` owns evaluation against the current Construction, successor
selection, orchestration, review credit, and closure. The source owner retains
its own receipt semantics.

## Minimal law

~~~text
claim != observed fact
observed fact != liability
liability != accepted scope
accepted scope != selected repair
Counterexample Set != mutation authority
~~~

## Counterexample Set

~~~yaml
artifact:
  schema: counterexample-set/v1
  artifact_id:
  goal_id:
  semantic_author: review-fold
  created_at:
  predecessor_refs: []
  supporting_refs:
    - review-attempt-or-failure-evidence-ref
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

A current clean source may produce an empty `classes` list. One class represents
one stable Counterexample to one governing law at one boundary. Review attempt
IDs, commits, publication epochs, filenames, and proposed patches are
provenance, not class identity.

For CAS evidence, each `finding_refs` entry is the `sha256:` digest of the
exact canonical CAS finding-row bytes. Preserve CAS `findingId` and the
best-effort `findingFingerprint` inside cited provenance; neither defines the
Counterexample class or substitutes for the canonical-row digest.

## Dispositions

- `accepted`: current evidence establishes an in-scope falsification.
- `rejected`: evidence shows the claim is false, stale, already satisfied,
  preference-only, or not a liability.
- `blocked`: validity, ownership, applicability, or current subject identity
  remains unknown.
- `follow-up`: valid evidence lies outside the accepted Goal.

Rejected classes require rejection evidence. Accepted classes require
Actuating to evaluate the current Construction before mutation. A suggested
repair remains source prose and never enters the selected construction merely
because a reviewer proposed it.

## Procedure

Before the first native Ledger command in this workflow, load `$ledger` and
complete `$ledger ensure` once. Reuse Actuating's current adapter gate. When
invoked standalone, require `ledger --version` to be at least `0.11.0` and
verify that `ledger --source actuation --help` exposes only
`append|prepare|state|project|doctor|path` before materialization.

1. Bind the source to the current Goal, Construction, subject digest, and
   source-owner receipt.
2. Separate each claim, observed fact, and suggested repair.
3. Decide whether the fact is a current liability under an accepted Goal law.
4. Identify the governing law, stable boundary, discrepancy, owner, witness,
   falsifier, applicability, and evidence.
5. Quotient duplicate and same-class findings. One class may cite many finding
   rows and may recur across Construction successors.
6. Assign exactly one disposition to every class.
7. Materialize canonical JSON with the current six-command artifact adapter:

   ~~~bash
   ledger --source actuation --repo <repo> --goal <goal-id> \
     append --input <counterexample-set.json>
   ~~~

8. Return the materialized Counterexample Set to Actuating. Do not propose or
   execute a repair.

Use [review-fold.valid.example.json](assets/review-fold.valid.example.json) as
a shape example, never as evidence or authority.

## Guardrails

- Do not choose the review backend, lens, architecture, repair, work node, or
  next action.
- Do not count clean attempts or decide review convergence or closure.
- Do not turn style, speculation, or suggested patches into code.
- Do not accept scope expansion without source authority.
- Do not define class identity from transient implementation or review IDs.
- Treat Ledger materialization and validation as structural artifact work only.
  A pass grants no mutation, repair selection, review credit, or completion.
