# Recall Workflow

## Recall Workflow

```bash
ledger project \
  --definition "$learnings_definition" \
  --projection recall \
  --repo "<repo-root>" \
  --param "query=<focused component failure objective terms>" \
  --param "now=$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --param search_limit=5 \
  --param drop_superseded=true \
  --format json
```

Do not use `recall` as a substitute for current artifact inspection.
