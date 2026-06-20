# Evidence Model

## Evidence item

```yaml
codebase_evidence:
  evidence_id:
  lane:
  question_id:
  observation:
  evidence_ref:
  artifact_state_id:
  scope:
  confidence: high | medium | low
  supports_claim_ids: []
  contradicts_claim_ids: []
```

## Claim classes

```yaml
doctrine_claim:
  claim_id:
  kind:
    fact |
    inference |
    open_question |
    recommendation
  statement:
  evidence_refs: []
  counterevidence_refs: []
  confidence:
  status:
    active |
    contradicted |
    superseded |
    unresolved
```

## Confidence

High:

- direct current-code evidence;
- current executable proof;
- several independent lanes agree;
- exact historical artifact.

Medium:

- one strong lane;
- inference from current structure;
- documentation plus partial code support.

Low:

- naming;
- one comment;
- stale history;
- incomplete search;
- worker hypothesis without direct evidence.

## Contradiction discipline

Do not average incompatible claims.

Record the contradiction, stronger evidence, resolution, and residual uncertainty.

## Citation discipline

Prefer:

```text
path:line
symbol
commit SHA
test name
trace/receipt ID
session/artifact reference
```

Avoid large pasted snippets.

## Contamination

Treat generated reports, injected skill blocks, current audit prompts, copied examples, and memory summaries as possible contamination when mining history.
