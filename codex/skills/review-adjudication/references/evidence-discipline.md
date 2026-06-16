# Evidence Discipline for Review Adjudication

Every review item should separate fact, claim, proposal, and uncertainty before route selection.

```yaml
evidence_discipline:
  observed_fact: "What is directly true in the current artifact?"
  review_claim: "What the reviewer/CAS/PR comment claims follows from the fact."
  proposed_change: "What the review item implies should change."
  uncertainty: "What is unknown, inferred, stale, or disputed."
  scope_basis: "Why this evidence justifies the proposed scope."
```

If evidence is ambiguous and mutation would result, prefer `validate-only`, `blocked`, or narrower proof before code mutation.
