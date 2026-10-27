# Structured Fold Output

Use when the caller requires the complete structured handoff. Preserve the
existing field meanings; the representation grants no additional effect authority.

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
        - reported_claim:
          observed_fact: # established only; omit when unresolved
          admission_basis: # decisive evidence, countercase result, limiting premise
          # Optional, only when the source challenges a positive judgment:
          challenged_judgment:
          earliest_failed_premise:
          claim_strength_consequence:
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
