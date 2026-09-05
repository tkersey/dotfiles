---
name: review-fold
description: "Classify and quotient current review findings, tests, incidents, and other witnessed falsifiers while preserving original provenance. Decide current applicability and whether each proposed law is entailed by the accepted Goal, a strengthening, preference, new requirement, or underdetermined. With enclosing write authority, persist only accepted entailed witnesses in the Review Fold counterexample corpus; recompute classes, families, recurrence, architecture, and closure from current evidence."
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
-> accepted counterexample capture when authorized
-> no implementation mutation or architecture authority
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
  corpus_write_authorized: true | false # enclosing task; omitted means false
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

## Effect authority

`corpus_write_authorized` must follow the enclosing task's actual effect scope;
review pressure and corpus ownership cannot grant it. It is always false in
Actuating `analyze`. Adjudication and available read-only projection remain
permitted without capture. Do not repair bindings, provision a tool, or write a
source-memory note to evade that boundary. Return accepted in-context evidence
and empty `captured_ids` when writing is unauthorized; do not claim persistence
or block unrelated analysis solely because capture was intentionally skipped.

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
entailed + validated current, task-relevant falsifier
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

Reviewer consensus does not manufacture entailment. Adjudication never rewrites
an owner-issued `findings` verdict into `clean`.

Preserve a judgment challenge's positive claim, earliest failed premise, and
claim-strength consequence in the existing witness handoff. Distinguish an
observed behavior violation from an omitted coverage path or an unsupported
proof claim. Missing proof alone is not evidence that the behavior is false;
it may falsify an accepted evidence or truthfulness obligation. Apply the same
law-authority test before admission and let Actuating decide the response.
A workflow fingerprint binds identity, not reviewer access to parent-only
premises; preserve material evidence-access limitations in the existing horizon.
Do not infer a new correctness liability from an unavailable premise.

## Counterexample admission

An incoming finding is a proposed falsifier, not an established program fact.
A CAS receipt proves what the reviewer reported about its subject, not that the
allegation is true. Before admission, establish each witness independently:

1. **Obligation.** Cite the accepted outcome, compatibility contract, invariant,
   protocol, or mandatory verification condition and its required observation.
   Derived obligations need a traceable basis, not a verbatim user sentence;
   preferences and optional strengthening do not become laws through severity.
2. **Validity.** Trace the actual candidate, caller preconditions, permitted
   operations, environment, and observed consequence. Establish a feasible
   violation or the exact unmet mandatory proof obligation. Use the smallest
   decisive source trace, existing verifier result, or authorized reproduction.
   An expected result needs authority independent of the allegation: a test that
   merely asserts the reviewer's desired behavior is not an independent oracle.
3. **Relevance.** Bind that evidence to the current head and accepted Goal.
   Compare the base when delta causality matters. Neither an unchanged file nor
   a pre-existing defect is exempt when a Goal-wide obligation applies. Historical
   provenance alone establishes no current liability; require current applicability.
4. **Countercase.** Inspect the strongest readily available source evidence that
   could refute or narrow the finding: existing enforcement, actual call paths,
   companion changes, caller obligations, mitigations, or an applicable authorized
   exception. A named guard, opaque type, passing suite, or reviewer consensus is
   not a defense without showing how it defeats this witness. Equally, malformed
   input at a covered trust boundary is not out of scope merely because it is
   invalid; safe rejection may be the obligation. A rare but demonstrated
   violation remains real.

Settle the decisive premise, then stop. An obvious source trace can suffice;
do not require an executable reproduction, fabricate a defense, or demand proof
that no possible bug exists. Respect enclosing effect authority and frozen-head
rules. An unavailable or unsafe experiment leaves an evidence gap, not authority
to mutate the candidate or invent a result. Failed reproduction alone does not
refute a possible interleaving. Reuse an unchanged decision and its evidence;
reconsider only when material new evidence changes it. No extra reviewer, lane,
recursive challenge loop, mandatory report, acceptance quota, or rejection quota.

Admit only the supported claim after this examination. Separate established
validity, its consequence for a mandatory completion obligation, and any proposed
repair. A valid witness proves neither the suggested fix nor the whole causal
family. Validate members before grouping; one proven consequence cannot admit
an unvalidated sibling. Preserve the original allegation when accepting a
narrower claim. Do not manufacture a replacement finding to save a refuted one;
a genuinely new issue needs its own evidence and provenance.

Use existing dispositions: `accepted` for a validated relevant violation;
`rejected` for a refuted, already-satisfied, unrelated, or preference-only claim;
`follow-up` for an unrequired improvement or new requirement. Keep a material
unknown in `unresolved_questions`; use `blocked` only for the claim or action
whose required decision depends on it. Unknown is neither acceptance nor
exoneration, and an unmet mandatory verification condition is not downgraded
merely because no runtime failure was reproduced. Record the decisive evidence,
countercase result, and any limiting premise in the existing witness handoff,
not a second packet. An all-accepted wave is legitimate when every claim earns it.

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

## Procedure

1. Project the repository counterexample basis and preserve its exact IDs and
   source references. An absent local store is not proof of complete history.
2. Preserve every current and historical witness's original subject.
3. Separate reported claim, established fact, suggested repair, and transport
   status; do not copy an allegation into `observed_fact` as proof of itself.
4. Attribute the proposed law and classify its Goal authority.
5. Apply Counterexample admission to each proposed witness, establishing validity,
   current applicability, Goal relevance, and the decisive countercase result.
6. Assign disposition from that evidence; keep unresolved premises explicit.
7. Name detection boundaries and exact owner evidence supporting the disposition.
8. Quotient only independently adjudicated witnesses whose law, authority,
   applicability, discrepancy, and causal evidence agree.
9. Permit one class to span owner sites when distributed ownership may be the
   defect.
10. State the family only as a hypothesis. Distinguish predicted siblings from
    observed witnesses.
11. Compare exact prior owner evidence and projected counterexamples to classify
    recurrence. Incomplete history yields `unknown`, never `first-observed`.
12. If an eliminated claim is supplied, classify exact relation to its law,
    family, validity horizon, and reconsideration falsifier. Do not revoke or
    preserve the claim; Actuating owns that effect.
13. When `corpus_write_authorized` is true, capture each independent witness
    that passed Counterexample admission, whose current applicability is
    `still-present` or `transformed-applicable`, law authority is `entailed`, and
    disposition is `accepted`. Otherwise retain accepted evidence in context.
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
recorded Goal and subject. Re-evaluate validity and relevance before using it
against current code; a spurious historical admission gains no current authority.
Preserve the historical admission and provenance rather than rewriting them.

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
decisive admission or refutation evidence, evidence gaps, and unresolved
questions. Actuating decides what those facts require.
