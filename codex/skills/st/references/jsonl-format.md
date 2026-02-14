# st JSONL Format (v3)

## Record lanes

`st` uses an append-only JSONL stream; each line is one v3 record.

- Shared fields: `v` (`3`), `ts` (UTC ISO-8601), `seq` (non-negative integer), `lane` (`event` or `checkpoint`)
- `event` lane: requires `op`
- `checkpoint` lane: requires full `items` snapshot
- Optional event/checkpoint metadata envelope: `mutation` (writer audit details such as policy flag/actor/session)

```json
{"v":3,"ts":"2026-02-09T20:00:00Z","seq":41,"lane":"event","op":"set_status","id":"st-002","status":"in_progress"}
{"v":3,"ts":"2026-02-09T20:01:00Z","seq":41,"lane":"checkpoint","items":[{"id":"st-001","step":"Reproduce issue","status":"completed","deps":[],"notes":"","comments":[]}]}
{"v":3,"ts":"2026-02-09T20:02:00Z","seq":42,"lane":"event","op":"set_status","id":"st-003","status":"in_progress","mutation":{"allow_multiple_in_progress":false,"actor":"tk","pid":12345}}
```

## Event ops

- `init`
- `replace`: reset materialized state to `items` (`replace_all` accepted for compatibility)
- `upsert`: create/update one item from `item` (`upsert_item` accepted for compatibility)
- `set_status`: update `status` for `id`
- `set_deps`: update typed `deps` for `id`
- `set_notes`: update `notes` for `id`
- `add_comment`: append one `comment` for `id`
- `remove`: remove item by `id`

## Item shape

```json
{
  "id": "st-003",
  "step": "Document v3 protocol",
  "status": "pending",
  "deps": [{"id": "st-002", "type": "blocks"}],
  "notes": "Capture rollout caveats",
  "comments": [{"ts": "2026-02-09T20:02:00Z", "author": "tk", "text": "Needs review"}]
}
```

- `deps` is required and is an array of edge objects
- Edge object shape: `{ "id": "<item-id>", "type": "<edge-type>" }`
- `type` is kebab-case; missing/empty normalizes to `blocks`
- `notes` is a string (default `""`)
- `comments` is an array of `{ts,author,text}` objects (default `[]`)

## Read-view derived fields

`show --format json` enriches each item with:

- `dep_state`: `ready`, `waiting_on_deps`, `blocked_manual`, or `n/a`
- `waiting_on`: unresolved dependency IDs

## Checkpoint cadence and seq watermark

- Seq watermark is the largest `seq` present in the stream
- New event writes use `seq = watermark + 1`
- Checkpoints persist full `items` at the current watermark `seq`
- Trigger checkpoint compaction when trailing events since the last checkpoint reach the configured interval (`needs_checkpoint(records, interval)`)
- Checkpoint seq rule: each checkpoint `seq` must equal the watermark immediately before that checkpoint record
- Trailing seq rule: records after the latest checkpoint must be strictly increasing (`seq` monotonic + unique)
- Replay contract: latest checkpoint + records with `seq` greater than checkpoint `seq` must equal full replay
- Repair path: `uv run ~/.dotfiles/codex/skills/st/scripts/st_plan.py doctor --file .step/st-plan.jsonl --repair-seq` appends a canonical checkpoint at the current watermark to seal historical collisions

## Lock sidecar policy

- Mutation paths acquire a sidecar file lock at `<plan-file>.lock` (for example `.step/st-plan.jsonl.lock`)
- In git worktrees, mutating commands require that sidecar path to be ignored (`git check-ignore`) before writes proceed

## Translation contract to `update_plan`

- Preserve `$st show --format json` item order
- Status mapping: `in_progress` -> `in_progress`, `completed` -> `completed`, `pending` -> `pending`, `blocked` -> `pending`, `deferred` -> `pending`, `canceled` -> `pending`
- Guardrail: if `dep_state == "waiting_on_deps"`, translated status must never be `in_progress` (force `pending`)
