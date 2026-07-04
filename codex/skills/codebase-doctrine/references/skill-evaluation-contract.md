# Generated skill evaluation contract

A Codebase Doctrine skill handoff must include the criteria by which the generated
skill will be graded after real use. The contract is part of CBSH-v2 because `$ms`
needs the update policy when it creates the package; it is not enough to say that
`$seq`, `$tune`, or `$refine` will evaluate the skill later.

## Required fields

```yaml
evaluation_contract:
  evaluation_cadence:
  evaluator:
  decision_record:
  update_policy:
  evaluation_evidence: []
  quality_criteria:
    - criterion_id:
      question:
      pass_signals: []
      fail_signals: []
      evidence_refs: []
  update_triggers:
    - trigger_id:
      condition:
      required_update:
      evidence_refs: []
  retirement_criteria:
    - criterion_id:
      condition:
      evidence_refs: []
```

## Rules

- Grade the generated skill on decision quality, not raw activation or mention counts.
- Each quality criterion asks a concrete question about an empirical decision episode.
- Pass and fail signals must be observable from skill-decision audit evidence.
- Update triggers identify when `$tune`/`$refine` should change the package.
- Doctrine-changing triggers must return to `$codebase-doctrine refresh` before tuning.
- Retirement criteria state when the knowledge is better enforced by code, tests,
  tooling, CI, repository guidance, ADRs, or the negative ledger than by a skill.
- Evidence refs must resolve in the source CBD-v2 evidence index.
