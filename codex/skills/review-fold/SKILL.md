---
name: review-fold
description: "Classify and quotient current review findings, failing tests, incidents, bug reports, migration failures, and other witnessed falsifiers against the exact current Goal and Git head. Separate facts from suggestions, identify stable law-and-boundary classes and causal recurrence from available owner evidence, and return a Review Fold without selecting repairs, granting mutation, counting review credit, or persisting a Counterexample artifact."
---

# Review Fold

## Mission

Turn current witnessed falsification pressure into one bounded analytical fold:

```text
owner-issued evidence
+ current Goal
+ exact Git head
-> classified facts, quotient classes, causal pressure, and blockers
-> no mutation authority
```

`$review-fold` owns evidence classification and quotienting. `$actuating` owns
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
Counterexample Set, or Ledger record.

## Minimal law

```text
claim != observed fact
observed fact != current liability
current liability != accepted scope
accepted scope != selected repair
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
      boundary:
      law:
      discrepancy: excess | deficit | incoherence | partiality | misbinding
      owner:
      severity: critical | high | medium | low
      disposition: accepted | rejected | blocked | follow-up
      observed_facts: []
      evidence_refs: []
      witnesses: []
      applicability:
      quotient_basis:
      recurrence:
        status: first-observed | recurring | unknown
        prior_evidence_refs: []
      causal_mechanism:
  unresolved_questions: []
  handoff:
```

Class IDs are stable semantic names within the available evidence horizon. They
derive from the governing law, boundary, discrepancy, and owner—not attempt,
thread, commit, filename, campaign, publication epoch, or proposed patch.

## Evidence horizon

Use every currently available owner source relevant to the Goal:

- exact CAS receipts and findings;
- unresolved provider review threads;
- current failing tests and verifier outputs;
- supplied incidents and bug reports;
- migration and compatibility failures;
- prior owner evidence explicitly available in the active context.

Do not maintain a parallel retained class register.

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
4. Name boundary, governing law, discrepancy, owner, witness, applicability,
   and evidence.
5. Quotient duplicate rows and same-class observations.
6. Compare exact available prior owner evidence to classify recurrence and
   shared causal mechanisms.
7. Assign one disposition:
   - `accepted`: current in-scope falsification is established;
   - `rejected`: evidence establishes stale, false, already satisfied,
     preference-only, or non-liability pressure;
   - `blocked`: validity, applicability, ownership, or current identity remains
     unknown;
   - `follow-up`: valid pressure lies outside the current Goal.
8. Return the fold directly to Actuating.

A current clean source may return an empty `classes` list.

## Source revisions

When the accepted source changes, re-run the fold over every currently
available applicable owner source. Reclassify current applicability and
disposition under the new Goal.

Do not copy predecessor Sets or create carry-forward references. Missing owner
history is explicit uncertainty, not evidence erasure.

## Causal pressure

Group accepted classes under one causal mechanism only when current evidence
supports a shared missing or falsified semantic law.

On a demonstrated recurrence or multiple accepted same-cause classes,
Actuating must reconsider whether another pointwise realization repair is
architecturally closed. Review Fold reports the causal evidence; it does not
choose the replacement architecture.

## Guardrails

- Do not choose architecture, repair, work node, operation, publication, next
  action, review credit, or closure.
- Do not turn suggested patches into accepted facts.
- Do not create or register a Counterexample artifact.
- Do not invoke Ledger.
- Do not claim historical continuity when owner evidence is unavailable.
- Do not broaden Goal scope.
- Do not treat CAS process exit as a semantic verdict.

## Handoff

Return the current Review Fold, exact source evidence references, accepted and
blocked classes, causal groups, evidence-horizon gaps, and unresolved
questions. Actuating decides what those facts require.
