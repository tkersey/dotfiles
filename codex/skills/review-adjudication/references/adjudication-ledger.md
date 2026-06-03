# Adjudication Ledger

Use one row per review comment. For real PR comments, the Surface-Budgeted v6
ledger is mandatory and must preserve raw identity, input inventory,
artifact-state identity, decision tests, adversarial action coverage, warrants,
surface budgets, and evidence references.

## Comment Inventory schema

```md
## Comment Inventory

- input_comment_count:
- ledger_row_count:
- input_comment_ids:
- ledger_comment_ids:
- missing_comment_ids:
- duplicate_comment_ids:
- synthesized_ids_for_real_comments: yes/no
```

## Compact Comment Ledger schema

```md
| id/thread | reviewer | location | excerpt | claim | concern validity | proposed fix validity | relevance | disposition | no-change status | invariant | evidence grade | evidence ref | handoff |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
```

## Decision Tests schema

```md
| id/thread | grounded | material | fresh | diagnosis | scope-fit | resolution value | no-change defeated | min evidence to change mind |
|---|---|---|---|---|---|---|---|---|
```

## Resolve Selection schema

```md
| id/thread | resolve decision | reason | proof ref | next | route rationale |
|---|---|---|---|---|---|
```

## Adversarial Action Matrix schema

```md
| id/thread | selected action | adversarial response required | adversary lane(s) | parallelism mode | strongest adversarial countercase | clearance | veto status | evidence ref | resulting route |
|---|---|---|---|---|---|---|---|---|---|
```

## Tail-weight requirement

The final visible section must collapse the ledger into the action buckets,
resolve selection, adversarial action matrix, warrants, gate, handoff agenda, and
bottom line.
