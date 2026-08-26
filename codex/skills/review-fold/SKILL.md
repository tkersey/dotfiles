---
name: review-fold
description: "Classify and quotient current review findings, tests, incidents, and other witnessed falsifiers while preserving original provenance. Decide current applicability and whether each proposed law is entailed by the accepted Goal, a strengthening, preference, new requirement, or underdetermined. Persist only accepted entailed witnesses in the Review Fold counterexample corpus; recompute classes, families, recurrence, architecture, and closure from current evidence."
---

# Review Fold

## Mission

Turn owner-issued falsification evidence and durable admitted witnesses into one
bounded current analytical fold:

```text
current owner evidence
+ accepted Goal
+ exact current Git head
+ projected counterexample corpus
+ optional current elimination-claim excerpt
-> facts, law authority, applicability, observational classes, blockers
-> accepted counterexample capture
-> no mutation or architecture authority
```

`$review-fold` owns evidence classification, Goal-law relation, observational
quotienting, and semantic admission to the counterexample corpus. `$actuating`
owns final family synthesis, post-elimination revocation, construction selection,
mutation, review credit, and closure.

CAS, tests, verifiers, incidents, migrations, and providers remain authoritative
for what they observed. The corpus preserves only the narrower semantic fact
that an exact witness was accepted as falsifying an accepted law under an exact
Goal and original subject.

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
  projected_counterexamples: []
```

CAS-derived evidence requires the exact terminal CAS receipt. Historical tests,
incidents, and failures retain their original subjects. Project the Review Fold
counterexample basis before classification when available; do not treat stored
rows as currently applicable without re-evaluation.

Read [counterexample-corpus.md](references/counterexample-corpus.md) before the
first corpus projection or capture in a workflow.

## Minimal law

```text
claim != observed fact
observed fact != current liability
witness subject != current applicability subject
reviewer-desired property != accepted Goal law
current liability != observational class
observational class != final family
stored counterexample != current applicability
stored counterexample != current family or architecture
same-law after elimination != another patch instruction
Review Fold != mutation authority
```

## Law-authority classification

For every proposed governing law, choose:

```text
entailed
  exact evidence shows the property follows from accepted Goal authority

strengthening
  beneficial property not required by the current Goal

preference
  design preference without a current correctness obligation

new-requirement
  legitimate property requiring new source or user authority

underdetermined
  current Goal evidence cannot decide
```

Record an `entailment_basis` or `non_entailment_basis`.

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

Reviewer consensus does not manufacture entailment.

## Output

```yaml
review_fold:
  current_head:
  evidence_horizon:
    complete_for_claims: true | false
    missing_sources: []
  counterexample_corpus:
    projected_ids: []
    captured_ids: []
    blocked_sources: []
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

Class IDs derive from law, boundary, discrepancy, and supported family
hypothesis—not attempt, thread, file, reviewer, current owner, or proposed patch.
Counterexample IDs derive from repository, Goal digest, accepted law, original
witness subject, and observed fact.

## Procedure

1. Project the repository counterexample basis and preserve its exact IDs and
   source references. An absent local store is not proof of complete history.
2. Preserve every current and historical witness's original subject.
3. Judge current applicability separately against the current Goal and head.
4. Separate claim, observed fact, suggested repair, and transport status.
5. Attribute the proposed law and classify its Goal authority.
6. Assign disposition from authority plus current applicability.
7. Name detection boundaries and exact owner evidence.
8. Quotient duplicates only when law, authority, applicability, discrepancy, and
   causal evidence agree.
9. Permit one class to span owner sites when distributed ownership may be the
   defect.
10. State the family only as a hypothesis. Distinguish predicted siblings from
    observed witnesses.
11. Compare exact prior owner evidence and projected counterexamples to classify
    recurrence. Incomplete history yields `unknown`, never `first-observed`.
12. If an eliminated claim is supplied, classify exact relation to its law,
    family, validity horizon, and reconsideration falsifier. Do not revoke or
    preserve the claim; Actuating owns that effect.
13. Capture each independent witness whose current applicability is
    `still-present` or `transformed-applicable`, law authority is `entailed`, and
    disposition is `accepted`.
14. Return the fold and corpus IDs directly.

A clean source may return an empty `classes` list and performs no capture.

## Counterexample corpus boundary

The owner definition is:

```text
review-fold/counterexample-corpus
```

The repo-local append-only store is:

```text
.ledger/review-fold/counterexamples/events.jsonl
```

Persist only immutable semantic admissions and provenance:

```text
repository and Goal digest
accepted law and authority basis
source-owner references
original witness subject
observed fact and detection boundary
evidence and independence basis
```

Never persist as authority:

```text
current applicability
observational class or final family
causal generator or recurrence status
canonical owner, cut, carrier, or repair
review credit, candidate state, or closure
```

These are current projections. Duplicate reviewer reports of one semantic
witness do not become independent counterexamples. Store bounded summaries and
exact references, not transcripts, logs, credentials, secrets, or suggested
patches.

A capture failure does not rewrite the source evidence or make the current fold
false. Report it as an incomplete historical horizon. Actuating may not use
absence from that horizon to claim first occurrence, disjointness, or
elimination.

## Current applicability

Only `still-present` and `transformed-applicable` establish current pressure.
`already-excluded` is historical explanation. `not-comparable` and `unknown`
cannot establish current recurrence, family coverage, or a post-elimination
falsifier.

A corpus row proves only that its original witness was admitted under its
recorded Goal and subject. Re-evaluate it before using it against current code.

## Evidence horizon

Use every currently available owner source relevant to the Goal, including the
counterexample basis projection. When evidence needed to distinguish first
occurrence from recurrence is unavailable:

```text
recurrence.status = unknown
```

Do not infer `first-observed`, `recurring`, disjointness, or family completeness
from absence in an incomplete corpus, memory, or summary.

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

Independent witnesses differ materially in input partition, state or
transition, admission path, producer or consumer, external incident, generator,
or temporal trace. Duplicate reports, copied tests, repeated prose, and several
failures from one root execution are not independent.

## Post-elimination relation

When the input supplies an active `eliminated` claim:

```text
same accepted law, inside the validity horizon, with exact evidence that the
witness belongs to the claimed family or satisfies its reconsideration falsifier
  -> same-claim

same accepted law and horizon, with exact disjoint-family evidence
  -> same-law-different-family

same accepted law outside the horizon
  -> outside-horizon

different accepted law
  -> different-law

insufficient authority, applicability, family, or horizon evidence
  -> unknown or non-current
```

A strengthening or preference does not falsify the current Goal's claim. A new
requirement reopens Goal authority rather than retroactively falsifying the old
Goal.

Review Fold reports the relation. Actuating revokes and adjudicates only a
current `entailed` `same-claim` falsifier.

## Guardrails

- Do not choose a final family, frontier, cut, owner, carrier, repair,
  architecture, next action, review credit, publication, or closure.
- Do not turn suggested patches into facts.
- Do not treat reviewer consensus as Goal authority.
- Do not broaden the Goal or label strengthening as a current blocker.
- Do not rewrite historical provenance.
- Do not define a family as its observed examples.
- Do not infer recurrence or post-elimination relation without exact evidence.
- Do not persist a Review Fold, class registry, family registry, or current
  applicability state.
- Do not copy full CAS receipts; retain exact source references.
- Do not treat process exit as a semantic verdict.

## Handoff

Return exact evidence references, corpus IDs, law-authority classifications,
current applicability, observational classes, post-elimination relations,
family hypotheses, sibling predictions when evidenced, recurrence status,
evidence gaps, and unresolved questions. Actuating decides what those facts
require.
