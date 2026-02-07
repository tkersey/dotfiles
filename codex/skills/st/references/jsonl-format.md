# st JSONL Format

## Event model

`st_plan.py` stores an append-only JSONL stream where each line is one event object:

```json
{"v":2,"ts":"2026-02-07T20:00:00Z","op":"upsert","item":{"id":"st-001","step":"Reproduce issue","status":"pending","deps":[]}}
```

Fields:

- `v`: schema version (`2`)
- `ts`: UTC timestamp (ISO-8601)
- `op`: one of `init`, `replace`, `upsert`, `set_status`, `set_deps`, `remove`

## Ops

- `init`: initialization marker
- `replace`: reset materialized state to `items` array
- `upsert`: create/update one item from `item`
- `set_status`: update status for existing item (`id`, `status`)
- `set_deps`: update dependencies for existing item (`id`, `deps`)
- `remove`: remove item by `id`

## Materialized snapshot shape

Both `export` output and `import-plan` input support:

```json
{
  "items": [
    {"id":"st-001","step":"Reproduce issue","status":"pending","deps":[]},
    {"id":"st-002","step":"Patch core logic","status":"in_progress","deps":["st-001"]}
  ]
}
```

`import-plan` also accepts a top-level JSON array of item objects.

`show --format json` adds derived fields per item:

- `dep_state`: one of `ready`, `waiting_on_deps`, `blocked_manual`, `n/a`
- `waiting_on`: unresolved dependency IDs

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

## Dependency-state vocabulary

Dependency state is derived from `status` + `deps` (not stored as a primary field in events):

- `ready`: item can run now (`pending`/`in_progress` with all deps complete)
- `waiting_on_deps`: `pending` with unresolved dependencies
- `blocked_manual`: explicitly marked `blocked`
- `n/a`: terminal/non-execution statuses (`completed`, `deferred`, `canceled`)

## Invariants

- IDs must be non-empty strings.
- Step text must be non-empty.
- `deps` is required and must be an array (use `[]` when no dependencies exist).
- Dependency IDs must be non-empty strings and unique per item.
- Dependencies must reference existing item IDs in the current state.
- Self-dependencies are invalid.
- Dependency cycles are invalid.
- Items cannot be `in_progress` or `completed` while any dependency is unresolved.
- By default, exactly zero or one item may be `in_progress`.
- Use `--allow-multiple-in-progress` only when explicitly required.
