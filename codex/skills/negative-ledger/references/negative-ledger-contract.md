# Negative Ledger Contract

A Negative Evidence Ledger records witnessed disconfirmation and current applicability. It prunes repeated dead ends without converting historical failure into permanent dogma.

## Entry Validity

An entry may affect routing only when all are true:

- narrow hypothesis;
- named attempted change or decision;
- concrete inspectable witness;
- stated observed outcome;
- failure classification;
- explicit scope and applicability conditions;
- status decided against current artifact state;
- narrow exclusion rule;
- explicit reopening criteria.

If any condition is missing, use `capture_candidate`, `need-evidence`, `unknown`, or `stale`; do not block.

## NER-v2 Record

```yaml
negative_evidence_record:
  record_version: NER-v2
  neg_id: NEG-000001
  status: capture_candidate | need-evidence | unknown | active | accepted_risk | stale | reopened | superseded
  kind: realization_route | authority_model | kernel_distinction | proof_pattern
  route_or_model_id:
  route_id:
  cluster_id:
  artifact_state_id:
  hypothesis:
  attempted_change:
  observed_outcome:
  failure_class: no-effect | local-regression | global-regression | unsound | too-complex | stale | unknown
  source_refs: []
  falsifying_evidence: []
  exclusion_scope: exact | route | route_family | cluster | authority_model | distinction_pattern | proof_pattern
  exclusion_rule:
  applicability_conditions: []
  reopening_criteria: []
  confidence: high | medium | low | unknown
  next_search_hint:
```

## Blocking Rule

Only `active` records may block. They require witness evidence, valid applicability, and exact matching appropriate to `exclusion_scope`.

Cluster identity alone is not exclusion. A new helper name does not create a new route. Fuzzy overlap is suggest-only.

## Reopening

A reopened route needs positive proof that at least one reopening criterion is satisfied. Reopening creates a proof obligation, not a green light.

## Memory Projection

Memory admission is a projection of ledger truth, not a second ledger. The projection embeds complete source refs, applicability conditions, exclusion rule, reopening criteria, source event count, and projection fingerprint. Phase 2 may compile it into memory, but route blocking continues to consult `.ledger/negative-ledger.jsonl`.
