---
name: review-fold
description: "Classify and quotient current review findings, failing tests, incidents, bug reports, migration failures, and other witnessed falsifiers against the exact current Goal and Git head. Separate facts from suggestions, distinguish law boundaries from detection surfaces, identify counterexample families and independent witnesses from available owner evidence, and return a Review Fold without selecting admission frontiers, repairs, architecture, review credit, or durable artifacts."
---

# Review Fold

## Mission

Turn current witnessed falsification pressure into one bounded analytical fold:

```text
owner-issued evidence
+ current Goal
+ exact Git head
-> classified facts, counterexample families, causal pressure, and blockers
-> no mutation authority
```

`$review-fold` owns evidence classification, quotienting, and family evidence.
`$actuating` owns admission-frontier analysis, semantic-hotspot judgment,
architecture evaluation, target selection, review credit, next action, and
closure. Source owners retain their receipts and durable history.

## Input

Require:

```yaml
review_fold_input:
  goal:
  repository:
  base:
  head:
  source_batches:
    - owner:
      exact_receipt_or_output:
      findings_or_failure:
  relevant_prior_owner_evidence: []
```

CAS-derived evidence must include the exact terminal CAS receipt. Tests,
incidents, provider review threads, migration failures, and compatibility
failures retain their native owner evidence.

Do not require an Actuating campaign event, Construction identifier,
Counterexample Set, hotspot registry, or Ledger record.

## Minimal law

```text
claim != observed fact
observed fact != current liability
current liability != accepted scope
accepted scope != counterexample family
counterexample family != admission frontier
admission frontier != selected repair
Review Fold != mutation authority
```

## Output

```yaml
review_fold:
  bound_head:
  evidence_horizon:
    complete_for_claims: true | false
    missing_sources: []
  classes:
    - class_id:
      law:
      law_boundary:
      semantic_owner:
      discrepancy: excess | deficit | incoherence | partiality | misbinding
      severity: critical | high | medium | low
      disposition: accepted | rejected | blocked | follow-up
      observed_facts: []
      evidence_refs: []
      witnesses:
        - observed_fact:
          detection_boundary:
          evidence_ref:
          independence_basis:
      applicability:
      family_basis:
      quotient_basis:
      recurrence:
        status: first-observed | recurring | unknown
        prior_evidence_refs: []
      causal_mechanism:
  unresolved_questions: []
  handoff:
```

Class IDs are stable semantic names within the available evidence horizon. They
derive from the governing law, law boundary, semantic owner, discrepancy, and
family basis—not attempt, thread, commit, filename, detection surface, campaign,
publication epoch, or proposed patch.

A class may contain witnesses detected at different boundaries. Review Fold
does not infer that a detection boundary is the admission frontier.

## Evidence horizon

Use every currently available owner source relevant to the Goal:

- exact CAS receipts and findings;
- unresolved provider review threads;
- current failing tests and verifier outputs;
- supplied incidents and bug reports;
- migration and compatibility failures;
- prior owner evidence explicitly available in the active context.

Do not maintain a parallel retained class or hotspot register.

When historical evidence needed to prove recurrence is unavailable:

```text
recurrence.status = unknown
```

Do not infer `first-observed` or `recurring` from memory or a previous summary.
Actuating may still address the current accepted fact, but recurrence-dependent
architecture laws remain unproved.

## Procedure

1. Bind every source batch to the exact current Goal and Git head.
2. Separate the source's claim, observed fact, suggested repair, and transport
   status.
3. Decide whether each fact is a current liability under an accepted Goal law.
4. For each witness, name the detection boundary and exact owner evidence.
5. For each candidate class, name the governing law, law boundary, semantic
   owner, discrepancy, applicability, and family basis.
6. Quotient duplicate rows and same-family observations only when the governing
   law and semantic basis agree.
7. Record why each witness is independent or mark the basis unknown.
8. Compare exact available prior owner evidence to classify recurrence and
   shared causal mechanisms.
9. Assign one disposition:
   - `accepted`: current in-scope falsification is established;
   - `rejected`: evidence establishes stale, false, already satisfied,
     preference-only, or non-liability pressure;
   - `blocked`: validity, applicability, ownership, family basis, or current
     identity remains unknown;
   - `follow-up`: valid pressure lies outside the current Goal.
10. Return the fold directly to Actuating.

A current clean source may return an empty `classes` list.

## Counterexample families

Group witnesses only when current evidence supports:

```text
same violated law
compatible applicability
same semantic owner
same law boundary
same causal mechanism or equivalent escape relation
```

Witness independence requires a material difference in input partition, state
or transition, call path, producer or consumer, external incident, generator,
or temporal trace.

Duplicate reports, copied tests, repeated reviewer prose, and multiple failures
from one root execution are not independent evidence.

File proximity is not a family basis. Different files may witness one family;
one file may contain several unrelated families.

Review Fold reports the family and causal evidence. Actuating combines that
evidence with the reconstructed incumbent to identify the admission frontier
and decide whether the family forms a semantic hotspot.

## Source revisions

When the accepted source changes, re-run the fold over every currently
available applicable owner source. Reclassify current applicability and
disposition under the new Goal.

Do not copy predecessor Sets or create carry-forward references. Missing owner
history is explicit uncertainty, not evidence erasure.

## Causal pressure

On a demonstrated recurrence, several independent same-family witnesses, or
several current defensive sites for one law, Actuating must reconsider whether
another pointwise realization repair is architecturally closed.

Review Fold reports the pressure. It does not choose the admission frontier,
repair locus, replacement architecture, or correctness delta.

## Guardrails

- Do not choose an admission frontier, architecture, repair, work node,
  operation, publication, next action, review credit, or closure.
- Do not turn suggested patches into accepted facts.
- Do not equate detection surface with law boundary or admission frontier.
- Do not create or register a Counterexample or hotspot artifact.
- Do not invoke Ledger.
- Do not claim historical continuity or witness independence without exact
  evidence.
- Do not broaden Goal scope.
- Do not treat CAS process exit as a semantic verdict.

## Handoff

Return the current Review Fold, exact source evidence references, accepted and
blocked classes, counterexample families, witness-independence bases, causal
groups, evidence-horizon gaps, and unresolved questions. Actuating decides what
those facts require.
