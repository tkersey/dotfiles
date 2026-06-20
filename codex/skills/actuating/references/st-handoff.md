# $st Handoff

Use `$st` for all material plan intake and durable execution state.

## Preferred material-plan command trace

```bash
st intake plan --file .step/st-plan.jsonl --source <plan.md> --out .step/st-intake.md
st intake apply --file .step/st-plan.jsonl --input .step/st-intake.md --gate implementation-ready
st graph audit --file .step/st-plan.jsonl --gate implementation-ready --format markdown
st compile aperture --file .step/st-plan.jsonl --limit 7
```

## Completion trace

```bash
st proof record \
  --file .step/st-plan.jsonl \
  --id <st-id> \
  --obligation <proof-id> \
  --action <proof-action-id> \
  --command "<validation command>" \
  --evidence-ref <proof-log> \
  --artifact-ref "git:<sha-or-working-tree-fingerprint>"
st complete --file .step/st-plan.jsonl --id <st-id>
st assert-projection --file .step/st-plan.jsonl
```

If the installed `st` build rejects a documented proof flag combination, keep the graph status aligned with the smallest accepted `st complete` command and track the parser mismatch as a tool fix. Do not create sidecar proof state outside `$st`.

## Fallback when intake/graph commands are missing

- Probe capability once.
- Use the fallback path from `$st`.
- Record graph debt.
- Continue with the best durable representation available.
- Never pretend prose or chat state is durable `$st` graph state.
