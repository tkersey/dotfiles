# Evidence Model v2

## Question

```yaml
search_question:
  question_id:
  question:
  why_it_matters:
  lanes: []
  search_methods: []
  evidence_found: []
  model_change:
  status: answered | no_evidence | open | blocked
```

Every evidence item references one existing question. The question's
`evidence_found` list must exactly match all evidence carrying that question ID.

## Evidence

```yaml
codebase_evidence:
  evidence_id:
  lane:
  question_id:
  observation:
  evidence_ref:
  artifact_state_id:
  scope:
  confidence: high | medium | low | unknown
  provenance:
  supports_claim_ids: []
  contradicts_claim_ids: []
```

Evidence and claim references are bidirectional. A support or contradiction edge
must appear on both nodes.

## Claim

```yaml
doctrine_claim:
  claim_id:
  kind: fact | inference | open_question | recommendation
  statement:
  evidence_refs: []
  counterevidence_refs: []
  confidence: high | medium | low | unknown
  status: active | contradicted | superseded | unresolved
  durable: yes | no
```

Every durable active claim receives exactly one primary knowledge route.

## Doctrine status

Authorities, laws, invariants, and boundaries carry:

```yaml
doctrine_status:
  observed_current |
  documented_intent |
  explicit_target |
  proposed |
  contradicted |
  retired
normative_authority:
current_evidence_refs: []
target_authority_refs: []
gap_statement:
```

Do not represent current behavior and desired behavior as one unlabeled row.

## Evidence hierarchy

Prefer:

1. current mutation, transition, and certificate paths;
2. current executable proof;
3. current runtime evidence;
4. several independent current lanes;
5. exact history;
6. current guidance;
7. naming and comments.

Generated reports, skill prompts, examples, and memory summaries are possible
contamination, not independent proof.
