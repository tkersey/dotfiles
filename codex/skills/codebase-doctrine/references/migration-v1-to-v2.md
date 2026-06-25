# Migration from v1

## Intent

Replace:

```text
primary_invariant
```

with:

```text
primary_correctness_question
primary_risk_or_priority
user_supplied_invariant_hypotheses
```

Regenerate CDI-v2 from DIG-v2 with `intent_compile.py`.

## Doctrine

Reconstruct the CBD-v2 graph rather than renaming the version field.

Required changes include:

- artifact-state diff and intent digests;
- complete search-question/evidence reverse links;
- complete evidence/claim reverse links;
- doctrine status and normative authority on authorities, laws, invariants, and boundaries;
- proof-surface IDs and verification receipts;
- negative-route lifecycle and canonical ledger provenance;
- one primary route for every durable active claim;
- optional root skill;
- evidence-bearing candidacy;
- relational saturation.

## Specialists

Create CBDA-v1 assignments and regenerate worker packets as CBDP-v2.

## Skill creation

Regenerate an explicitly authorized CBSH-v2 against a valid CBD-v2 before
calling `$ms`.
