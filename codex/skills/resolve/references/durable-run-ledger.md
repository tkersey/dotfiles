# Durable Resolve Run Ledger

Use a local non-committed ledger for long or mutating `$resolve` runs.

Recommended location:

```text
~/.codex/resolve/runs/<repo-name>/<timestamp-or-branch>/
```

Recommended files:

```text
resolve-state.json
review-*.json
adjudication-ledger.jsonl
abstraction-route-ledger.jsonl
implementation-handoff-ledger.jsonl
pr-comment-ledger.jsonl
validation-ledger.jsonl
parallel-task-ledger.jsonl
```

## Rules

- Do not commit the ledger.
- Include enough state to resume or audit after context loss.
- Record every review receipt path or normalized result.
- Record every adjudication route and warrant consumed.
- Record every abstraction ladder receipt.
- Record every implementation handoff to `$fixed-point-driver`.
- Record every validation command and result.
- Record PR sweep inventory status.
- Final report should include the ledger path when created.
