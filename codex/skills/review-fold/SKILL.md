---
name: review-fold
description: "Classify and quotient current review findings, tests, incidents, and other witnessed falsifiers while preserving original provenance. Decide current applicability and whether each proposed law is entailed by the accepted Goal, a strengthening, preference, new requirement, or underdetermined. With enclosing write authority, persist only accepted entailed witnesses in the Review Fold counterexample corpus; recompute current applicability, observational classes, recurrence, and family hypotheses from current evidence; Actuating owns architecture, repair, review credit, and closure."
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

Read [the canonical admission reference](references/admission.md#law-authority-classification)
before classifying a proposed law. It owns the authority categories and their
entailed, optional, or unresolved consequences.

## Counterexample admission

Apply [the canonical Counterexample admission standard](references/admission.md#counterexample-admission)
to every proposed witness before admission or capture. The same owner reference
can be reused read-only by an enclosing workflow without invoking this workflow;
this entrypoint still owns full Review Fold inputs, procedure, and effects.

## Output

Return the disposition, law-authority basis, decisive evidence and countercase,
original witness subject, current applicability, unresolved premises, and exact
projected/captured corpus IDs. Keep allegations separate from established facts:

```yaml
reported_claim:
observed_fact: # established only; omit when unresolved
admission_basis: # decisive evidence, countercase result, limiting premise
```

For a judgment challenge retain `challenged_judgment`, `earliest_failed_premise`,
and `claim_strength_consequence`. Read [fold-output.md](references/fold-output.md)
when the caller requires the full structured handoff. A concise return preserves
all decision-relevant evidence without populating inapplicable schema fields.

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

The [corpus owner reference](references/counterexample-corpus.md) defines storage,
projection, capture, immutable fields, and semantic identity. Project the available
basis before classification under the existing Input and Effect authority rules.
Persist only independent accepted, current, entailed witnesses with original
subject and provenance; never persist current applicability, class/family, owner,
repair, review credit, or closure as authority. Capture failure leaves the current
evidence intact but makes dependent historical claims incomplete.

## History and classes

Re-evaluate every historical witness against the current Goal and head. Only
`still-present` and `transformed-applicable` establish current pressure;
`already-excluded` is historical, and unknown or incomparable evidence cannot
establish recurrence or a post-elimination falsifier. An incomplete history yields
`recurrence.status = unknown`, never first occurrence or family completeness.
Duplicate reports are not independent witnesses; grouping requires compatible law,
authority, applicability, discrepancy, and supported causal evidence. Classes and
family hypotheses do not select architecture or define a family's whole extension.

Class IDs derive from law, boundary, discrepancy, and supported family
hypothesis—not attempt, thread, file, reviewer, current owner, or proposed patch.
This semantic identity rule applies to concise and structured folds alike.

Read [history-and-classes.md](references/history-and-classes.md) before grouping
whose causal identity is uncertain, asserting recurrence or first occurrence, or
relating evidence to an active eliminated claim. Actuating owns revocation,
architecture, and closure; Review Fold reports the supported relation only.

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
