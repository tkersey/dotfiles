---
name: review-fold
description: "Classify and quotient current review findings, tests, incidents, and other witnessed falsifiers while preserving original provenance. Decide current applicability and whether each proposed law is entailed by the accepted Goal, an optional strengthening, a preference, a new requirement, or underdetermined. Return observational same-law classes and post-elimination relations without selecting repairs, architecture, review credit, or durable artifacts."
---

# Review Fold

## Mission

Turn owner-issued falsification evidence into one bounded analytical fold:

```text
owner evidence
+ accepted Goal
+ exact current Git head
+ optional current elimination-lease excerpt
-> facts, law authority, applicability, observational classes, blockers
-> no mutation authority
```

`$review-fold` owns evidence classification, Goal-law relation, quotienting, and
observational-class evidence. `$actuating` owns family finalization,
post-elimination revocation, architecture selection, next action, and closure.

## Input

```yaml
review_fold_input:
  goal:
  repository:
  base:
  current_head:
  current_elimination_claim: null | {
    law:
    family:
    validity_horizon:
    reconsideration_falsifier:
    disposition: eliminated
    issued_head:
  }
  source_batches:
    - owner:
      exact_receipt_or_output:
      findings_or_failure:
      witness_subject:
        repository:
        git_head_or_build:
        schema_or_environment:
        input_state_or_trace:
  relevant_prior_owner_evidence: []
```

CAS-derived evidence requires the exact terminal CAS receipt. Historical tests,
incidents, and failures retain their original subjects.

Do not require an Actuating event, Construction identifier, Counterexample Set,
hotspot registry, or Ledger record.

## Minimal law

```text
claim != observed fact
observed fact != current liability
witness subject != current applicability subject
reviewer-desired property != accepted Goal law
current liability != observational class
observational class != final family
same-law after elimination != another patch instruction
Review Fold != mutation authority
```

## Law-authority classification

For every proposed governing law, choose:

```text
entailed
  exact evidence shows the property follows from accepted Goal authority

strengthening
  property is beneficial but not required by the current Goal

preference
  property is a design preference without a current correctness obligation

new-requirement
  property is legitimate but requires new source/user authority

underdetermined
  current Goal evidence cannot decide
```

Record an `entailment_basis` or `non_entailment_basis`.

Mapping to current disposition:

```text
entailed + current falsifier
  -> accepted

strengthening
  -> follow-up, non-blocking

preference
  -> rejected

new-requirement
  -> follow-up with authority_action: reopen-goal

underdetermined
  -> blocked with authority_action: seek-authority
```

Do not infer entailment merely because several reviewers agree or because the
property sounds safer.

## Output

```yaml
review_fold:
  current_head:
  evidence_horizon:
    complete_for_claims: true | false
    missing_sources: []
  classes:
    - class_id:
      class_kind: observational
      law:
      law_provenance: goal | public-contract | type-invariant | protocol |
        test-law | derived | hypothesized
      law_authority: entailed | strengthening | preference |
        new-requirement | underdetermined
      authority_basis:
      authority_action: none | follow-up | reject | reopen-goal | seek-authority
      law_boundary:
      current_owner_set: []
      owner_status: canonical | distributed | absent | contested | unknown
      discrepancy: excess | deficit | incoherence | partiality | misbinding
      severity: critical | high | medium | low
      disposition: accepted | rejected | blocked | follow-up
      post_elimination_relation: none | same-claim |
        same-law-different-family | outside-horizon | different-law | unknown
      post_elimination_basis:
      witnesses:
        - observed_fact:
          witness_subject:
            repository:
            git_head_or_build:
            schema_or_environment:
            input_state_or_trace:
          detection_boundary:
          evidence_ref:
          current_applicability:
            subject_head:
            status: still-present | transformed-applicable | already-excluded |
              not-comparable | unknown
            basis:
          independence_basis:
      family_hypothesis:
        predicate_or_generator:
        domain:
        predicted_sibling_classes: []
        prediction_basis:
        claim_strength: proved | exhaustive-finite | bounded |
          property-tested | sampled | hypothesized | unknown
        family_basis:
      quotient_basis:
      recurrence:
        status: first-observed | recurring | unknown
        prior_evidence_refs: []
      causal_hypothesis:
  unresolved_questions: []
  handoff:
```

Class IDs derive from the law, boundary, discrepancy, and family hypothesis—not
attempt, thread, file, reviewer, current owner, or proposed patch.

## Procedure

1. Preserve every witness's original subject.
2. Judge current applicability separately against the current Goal/head.
3. Separate claim, observed fact, suggested repair, and transport status.
4. Attribute the proposed law and classify its Goal authority.
5. Assign disposition from authority plus current applicability.
6. Name detection boundaries and exact evidence.
7. Quotient duplicates only when law, authority, applicability, discrepancy,
   and causal evidence agree.
8. Permit one class to span current owner sites when distributed ownership may
   be the defect.
9. State the family only as a hypothesis. Include predicted siblings when
   current evidence supports them; otherwise mark prediction unknown.
10. Compare exact prior owner evidence to classify recurrence. When the evidence
    horizon is incomplete for that distinction, report `unknown`, never
    `first-observed`.
11. When an active eliminated claim is supplied, classify whether an accepted
    class falsifies that exact claim, concerns a different family or law, lies
    outside its validity horizon, or remains unknown. Do not revoke or retain
    the claim; Actuating owns that effect.
12. Return the fold directly.

A clean source may return an empty `classes` list.

## Current applicability

Only `still-present` and `transformed-applicable` witnesses establish current
pressure. `already-excluded` is historical explanation. `not-comparable` and
`unknown` cannot establish current recurrence, family coverage, or a
post-elimination falsifier.

## Evidence horizon

Use every currently available owner source relevant to the Goal. When the
historical evidence needed to distinguish first occurrence from recurrence is
unavailable:

```text
recurrence.status = unknown
```

Do not infer `first-observed` or `recurring` from absence in an incomplete
evidence horizon, memory, or a prior summary.

## Observational classes

Group witnesses only when evidence supports:

```text
same proposed law
same law-authority classification
compatible applicability and discrepancy
plausible shared causal relation
```

Observed witnesses support a family hypothesis; they do not define its complete
extension.

Independent witnesses differ materially in input partition, state/transition,
admission path, producer/consumer, external incident, generator, or temporal
trace. Duplicate reports, copied tests, repeated prose, and multiple failures
from one root execution are not independent.

## Post-elimination relation

When the input supplies an active `eliminated` claim:

```text
same accepted law, inside the claim's validity horizon, with exact evidence
that the witness belongs to the claimed family or satisfies its reconsideration
falsifier
  -> post_elimination_relation: same-claim

same accepted law and validity horizon, but exact evidence establishes a
disjoint family
  -> same-law-different-family

same accepted law but outside the declared validity horizon
  -> outside-horizon; the witness may remain a current counterexample but does
     not falsify the scoped elimination claim

different accepted law
  -> different-law

authority, applicability, family relation, or horizon evidence insufficient
  -> unknown or non-current disposition
```

A strengthening or preference does not falsify the current Goal's elimination
claim. A new requirement reopens Goal authority rather than retroactively
falsifying the old Goal.

Review Fold reports the relation. Actuating must revoke and adjudicate only a
current `entailed` `same-claim` falsifier before mutation.

## Guardrails

- Do not choose a final family, frontier, cut, owner, repair, architecture, next
  action, review credit, publication, or closure.
- Do not turn suggested patches into facts.
- Do not treat reviewer consensus as Goal authority.
- Do not broaden the Goal.
- Do not label a strengthening as a current blocker.
- Do not rewrite historical provenance.
- Do not define a family as observed examples.
- Do not infer recurrence or post-elimination relation without exact evidence.
- Do not create a Counterexample/hotspot artifact or invoke Ledger.
- Do not treat process exit as a semantic verdict.

## Handoff

Return exact evidence references, law-authority classifications, applicability,
observational classes, post-elimination relations, family hypotheses, sibling
predictions when evidenced, recurrence status, evidence gaps, and unresolved
questions. Actuating decides what those facts require.
