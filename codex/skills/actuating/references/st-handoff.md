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
st complete --file .step/st-plan.jsonl --id <st-id> --command "<validation command>" --evidence-ref <proof-log>
st assert-projection --file .step/st-plan.jsonl
```

## Fallback when intake/graph commands are missing

- Probe capability once.
- Use the fallback path from `$st`.
- Record graph debt.
- Continue with the best durable representation available.
- Never pretend prose or chat state is durable `$st` graph state.
