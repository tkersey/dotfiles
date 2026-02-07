# st JSONL Format

## Event model

`st_plan.py` stores an append-only JSONL stream where each line is one event object:

```json
{"v":1,"ts":"2026-02-07T20:00:00Z","op":"upsert","item":{"id":"st-001","step":"Reproduce issue","status":"pending"}}
```

Fields:

- `v`: schema version (`1`)
- `ts`: UTC timestamp (ISO-8601)
- `op`: one of `init`, `replace`, `upsert`, `set_status`, `remove`

## Ops

- `init`: initialization marker
- `replace`: reset materialized state to `items` array
- `upsert`: create/update one item from `item`
- `set_status`: update status for existing item (`id`, `status`)
- `remove`: remove item by `id`

## Materialized snapshot shape

Both `export` output and `import-plan` input support:

```json
{
  "items": [
    {"id":"st-001","step":"Reproduce issue","status":"pending"},
    {"id":"st-002","step":"Patch core logic","status":"in_progress"}
  ]
}
```

`import-plan` also accepts a top-level JSON array of item objects.

## Status vocabulary

Canonical statuses:

- `pending`
- `in_progress`
- `completed`
- `blocked`
- `deferred`
- `canceled`

Aliases normalized automatically:

- `open`, `queued` -> `pending`
- `active`, `doing`, `in-progress` -> `in_progress`
- `done`, `closed` -> `completed`
- `cancelled` -> `canceled`

## Invariants

- IDs must be non-empty strings.
- Step text must be non-empty.
- By default, exactly zero or one item may be `in_progress`.
- Use `--allow-multiple-in-progress` only when explicitly required.
