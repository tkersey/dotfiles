# `.ledger/` Storage Policy

`.ledger/` is the sole new artifact namespace.

## Shared mode

Potentially tracked:

```text
.ledger/st/workspace.jsonl
.ledger/st/plans/*/plan.jsonl
selected durable proof receipts
migration receipts
```

Always ignored:

```text
.ledger/st/locks/
.ledger/st/runtime/
.ledger/st/transactions/
.ledger/st/worktrees/
.ledger/st/integration/scratch/
```

Suggested ignore entries:

```gitignore
.ledger/st/locks/
.ledger/st/runtime/
.ledger/st/transactions/
.ledger/st/worktrees/
.ledger/st/integration/scratch/
```

## Local mode

Ignore:

```gitignore
.ledger/st/
```

## Mixed mode

Track graph contracts but keep proof logs local.

Proof receipts may reference local evidence paths; reviewers must know whether
the underlying evidence is portable.

## Rule

The workspace must record its storage mode. It must never silently switch
between shared and local operation.
