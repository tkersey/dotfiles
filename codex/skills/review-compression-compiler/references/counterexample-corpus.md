# Counterexample Corpus

Review findings are normalized into counterexamples.

## Row shape

```yaml
review_counterexample:
  id:
  source: cas | native-review | pr-comment | validation | human
  observed_bad_state_or_gap:
  expected_contract:
  producer_candidate:
  transition_candidate:
  validator_candidate:
  consumer_or_proof_surface:
  owner_candidate:
  related_prior_findings: []
  evidence_ref:
  confidence: high | medium | low
```

## What counts as a counterexample

- bad state admitted;
- missing rejection;
- authority boundary bypassed;
- wrong owner mutating or validating;
- proof gap exposed by review;
- duplicate/shadow surface contradiction;
- downstream tolerance hiding producer defect;
- test fixture admits impossible production state.

## What is not enough

- "Reviewer dislikes this" without a concrete contract gap.
- Style comments unless they imply incorrect behavior or hidden complexity.
- A vague concern with no owner/proof surface.

Unclear comments should route to `blocked` or `needs_context`, not mutation.
