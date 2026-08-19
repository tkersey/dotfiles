---
name: review-fold
description: "Classify and quotient current review findings, failing tests, incidents, bug reports, migration failures, and other witnessed falsifiers against the current Goal and Git head while preserving each witness's original subject. Separate facts from suggestions, distinguish law boundaries from detection surfaces, return observational same-law classes with owner sets, family hypotheses, current applicability, and independence evidence, and never select admission frontiers, repairs, architecture, review credit, or durable artifacts."
---

# Review Fold

## Mission

Turn current witnessed falsification pressure into one bounded analytical fold:

```text
owner-issued evidence
+ current Goal
+ exact current Git head
-> classified facts, observational classes, causal pressure, and blockers
-> no mutation authority
```

`$review-fold` owns evidence classification, quotienting, and observational
class evidence. `$actuating` owns family finalization, admission-frontier or cut
analysis, semantic-hotspot judgment, architecture evaluation, target selection,
review credit, next action, and closure. Source owners retain their receipts and
durable history.

## Input

Require:

```yaml
review_fold_input:
  goal:
  repository:
  base:
  current_head:
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

CAS-derived evidence must include the exact terminal CAS receipt. Tests,
incidents, provider review threads, migration failures, and compatibility
failures retain their native owner evidence and original subject.

Do not require an Actuating campaign event, Construction identifier,
Counterexample Set, hotspot registry, or Ledger record.

## Minimal law

```text
claim != observed fact
observed fact != current liability
witness subject != current applicability subject
current liability != accepted scope
accepted scope != observational class
observational class != predicate-defined family
family hypothesis != admission frontier or cut
admission frontier or cut != selected repair
Review Fold != mutation authority
```

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
      law_boundary:
      current_owner_set: []
      owner_status: canonical | distributed | absent | contested | unknown
      discrepancy: excess | deficit | incoherence | partiality | misbinding
      severity: critical | high | medium | low
      disposition: accepted | rejected | blocked | follow-up
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

Class IDs are stable semantic names within the available evidence horizon. They
derive from the governing law, law boundary, discrepancy, and family hypothesis
—not attempt, thread, commit, filename, detection surface, campaign,
publication epoch, current owner identity, or proposed patch.

A class may contain witnesses detected at different boundaries and implemented
by different current owner sites. Review Fold does not infer that a detection
boundary or law boundary is an admission frontier.

## Witness provenance and current applicability

Never bind a historical incident or failure to the current head as though it
occurred there.

For every witness retain:

```text
original witness subject
current applicability subject
applicability status
applicability basis
```

Only `still-present` and `transformed-applicable` witnesses establish current
liability. `already-excluded` may explain the repository but does not establish
current pressure. `not-comparable` and `unknown` cannot establish recurrence,
family coverage, or a current hotspot.

## Evidence horizon

Use every currently available owner source relevant to the Goal:

- exact CAS receipts and findings;
- unresolved provider review threads;
- current failing tests and verifier outputs;
- supplied incidents and bug reports with original subjects;
- migration and compatibility failures;
- prior owner evidence explicitly available in the active context.

Do not maintain a parallel retained class or hotspot register.

When historical evidence needed to prove recurrence is unavailable:

```text
recurrence.status = unknown
```

Do not infer `first-observed` or `recurring` from memory or a previous summary.

## Procedure

1. Preserve each source's original subject and bind the applicability judgment
   separately to the current Goal and head.
2. Separate claim, observed fact, suggested repair, and transport status.
3. Decide whether each fact is a current liability under an attributed Goal law.
4. For each witness, name the detection boundary, exact evidence, applicability
   status, and independence basis.
5. For each observational class, name law, provenance, law boundary, current
   owner set, owner status, discrepancy, applicability, and family hypothesis.
6. Quotient duplicate rows and same-law observations only when the semantic and
   applicability basis agree.
7. Permit a class to span several current owner sites when distributed ownership
   may itself be the defect.
8. State the family predicate or generator and domain as a hypothesis; use
   `unknown` when they cannot be stated honestly.
9. Compare exact available prior owner evidence to classify recurrence and
   causal hypotheses.
10. Assign one disposition:
    - `accepted`: current in-scope falsification is established;
    - `rejected`: evidence establishes stale, false, already satisfied,
      unsupported-path, preference-only, or non-liability pressure;
    - `blocked`: validity, applicability, law, class basis, provenance, or
      current identity remains unknown;
    - `follow-up`: valid pressure lies outside the current Goal.
11. Return the fold directly to Actuating.

A current clean source may return an empty `classes` list.

## Observational classes and family hypotheses

Group witnesses only when current evidence supports:

```text
same violated law
compatible current applicability
compatible discrepancy
plausible shared causal relation
```

Do not require the same current owner. Report the owner set and status.

A family hypothesis must state a predicate or generator, domain, and claim
strength. The observed witnesses support the hypothesis; they do not define its
complete extension.

Witness independence requires a material difference in input partition, state
or transition, call path, producer or consumer, external incident, generator,
or temporal trace.

Duplicate reports, copied tests, repeated reviewer prose, and multiple failures
from one root execution are not independent evidence.

File proximity is not a class basis. Different files may witness one class; one
file may contain several unrelated classes.

Review Fold reports the observational class and causal evidence. Actuating may
partition it by candidate admission frontiers, derive a minimal admission cut,
finalize a predicate-defined family, or leave the topology unresolved.

## Source revisions

When the accepted source changes, re-run the fold over every currently
available applicable owner source. Reclassify current applicability and
disposition under the new Goal without rewriting witness provenance.

Do not copy predecessor Sets or create carry-forward references. Missing owner
history is explicit uncertainty, not evidence erasure.

## Causal pressure

On a demonstrated recurrence, several independent same-law witnesses, a
distributed owner set, or several current compensating sites for one law,
Actuating must reconsider whether another pointwise realization repair is
architecturally closed.

Review Fold reports the pressure. It does not choose the family partition,
admission frontier, admission cut, candidate semantic owner, repair locus,
replacement architecture, or correctness delta.

## Guardrails

- Do not choose a family partition, admission frontier, admission cut,
  architecture, repair, work node, operation, publication, next action, review
  credit, or closure.
- Do not turn suggested patches into accepted facts.
- Do not equate detection surface with law boundary, frontier, or cut.
- Do not require one current owner when distributed ownership may be the defect.
- Do not define a family as only the witnesses observed.
- Do not rewrite historical witness provenance as current-head provenance.
- Do not create or register a Counterexample or hotspot artifact.
- Do not invoke Ledger.
- Do not claim historical continuity, current applicability, or witness
  independence without exact evidence.
- Do not broaden Goal scope.
- Do not treat CAS process exit as a semantic verdict.

## Handoff

Return the current Review Fold, exact source evidence references, accepted and
blocked observational classes, owner sets and statuses, family hypotheses,
witness provenance and current-applicability judgments, independence bases,
causal hypotheses, evidence-horizon gaps, and unresolved questions. Actuating
decides what those facts require.
