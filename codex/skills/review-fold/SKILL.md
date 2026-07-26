---
name: review-fold
description: "Classify and quotient review findings, failing tests, incidents, bug reports, migration failures, and other witnessed falsifiers against the exact current Goal and Construction, including carrying unresolved classes across explicit source revisions. Author counterexample-set/v1 without selecting repairs, counting review credit, or granting mutation."
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
    - review-campaign-started-event-ref
    - review-attempt-or-failure-event-ref
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

For CAS-derived evidence, `supporting_refs` cites the current
`review_campaign_started` event and each exact terminal attempt or transport
event used by the Set. Actuating resolves those Evidence Ledger events and
requires their `campaign_id` and request identity to match the campaign derived
from this Set's existing subject tuple. Do not duplicate that derived campaign
identity as a fifth Counterexample subject field. A non-review falsifier needs
no campaign reference.

Every newly materialized Set binds the exact current Goal Contract through
`supporting_refs` as `goal-contract:<artifact_id>`. For an explicit source
revision with unresolved accepted or blocked classes, or one that brings a
`follow-up` class within the successor Goal's scope, use the carry-forward
transition:

- the successor Goal cites every Set carrying an unresolved accepted or blocked
  class, or a `follow-up` class brought into scope, as
  `counterexample-set:<artifact_id>`;
- the successor Set's `supporting_refs` contains
  `goal-contract:<successor-artifact-id>` and
  `counterexample-set:<artifact_id>` for every carried Set;
- `predecessor_refs` includes the most recent Set carrying each carried class;
- `subject.construction_ref` remains the exact predecessor Construction being
  evaluated; and
- every carried stable `class_id` appears exactly once with a current
  disposition under the successor Goal.

Missing or mismatched Goal identity, incomplete Set coverage, omitted classes,
or predecessor drift is `blocked`. The transition classifies evidence under new
source authority; it neither selects the successor Construction nor grants
mutation.

A current clean source may produce an empty `classes` list. One class represents
one stable Counterexample to one governing law at one boundary. Review attempt
IDs, commits, publication epochs, filenames, and proposed patches are
provenance, not class identity.

For CAS evidence, each `finding_refs` entry is the `sha256:` digest of the
exact canonical compact CAS finding-row bytes. Preserve the enclosing CAS
receipt as attempt, tuple, request, and verdict provenance; none of those
transient identities defines the Counterexample class or substitutes for the
canonical-row digest.

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

1. Bind the source to the exact current Goal artifact, Construction, subject
   digest, static Review Contract digest, and source-owner receipt. Put
   `goal-contract:<artifact_id>` in `supporting_refs`. A failing test, incident,
   compatibility failure, or other non-review falsifier requires no review
   campaign. A CAS-derived set additionally binds its originating campaign,
   whose Review Contract digest must match the static digest in the
   Counterexample subject. Never fabricate a campaign for local evidence or
   make `review_contract_digest` optional.
2. Separate each claim, observed fact, and suggested repair.
3. Decide whether the fact is a current liability under an accepted Goal law.
4. Identify the governing law, stable boundary, discrepancy, owner, witness,
   falsifier, applicability, and evidence.
5. Quotient duplicate and same-class findings. One class may cite many finding
   rows and may recur across Construction successors. When a class recurs, the
   new Set's `predecessor_refs` must include the prior Set that most recently
   carried that class.
6. For source-revision carry-forward, include unresolved accepted and blocked
   classes plus each `follow-up` class brought within the successor Goal's
   scope; verify successor Goal and carried-Set reference symmetry, preserve the
   predecessor Construction, and require total stable-class coverage.
7. Assign exactly one disposition to every class.
8. Materialize canonical JSON with the current six-command artifact adapter:

   ~~~bash
   ledger --source actuation --repo <repo> --goal <goal-id> \
     append --input <counterexample-set.json>
   ~~~

9. Return the materialized Counterexample Set to Actuating. Do not propose or
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
