# st JSONL Format (v3)

## Record lanes

`st` uses an in-place rewritten JSONL stream; each line is one v3 record.

- Shared fields: `v` (`3`), `ts` (UTC ISO-8601), `seq` (non-negative integer), `lane` (`event` or `checkpoint`)
- `event` lane: requires `op`
- `checkpoint` lane: requires full `items` snapshot
- Optional event/checkpoint metadata envelope: `mutation` (writer audit details such as policy flag/actor/session)

```json
{"v":3,"ts":"2026-02-09T20:02:00Z","seq":42,"lane":"event","op":"replace","items":[{"id":"st-001","step":"Reproduce issue","status":"completed","priority":"medium","in_plan":false,"deps":[],"notes":"","comments":[]}],"mutation":{"allow_multiple_in_progress":false,"actor":"tk","pid":12345}}
{"v":3,"ts":"2026-02-09T20:02:00Z","seq":42,"lane":"checkpoint","items":[{"id":"st-001","step":"Reproduce issue","status":"completed","priority":"medium","in_plan":false,"deps":[],"notes":"","comments":[]}],"mutation":{"allow_multiple_in_progress":false,"actor":"tk","pid":12345}}
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
  "priority": "medium",
  "in_plan": true,
  "deps": [{"id": "st-002", "type": "blocks"}],
  "notes": "Capture rollout caveats",
  "comments": [{"ts": "2026-02-09T20:02:00Z", "author": "tk", "text": "Needs review"}]
}
```

- `deps` is required and is an array of edge objects
- Edge object shape: `{ "id": "<item-id>", "type": "<edge-type>" }`
- `type` is kebab-case; missing/empty normalizes to `blocks`
- `priority` is `high`, `medium`, or `low`; missing values normalize to `medium` on read/import, and canonical writes always emit it
- `in_plan` controls whether the item projects into `codex.plan` / `opencode.todos`; missing legacy values normalize to `true`
- Terminal statuses (`completed`, `deferred`, `canceled`) normalize to `in_plan=false`
- `notes` is a string (default `""`)
- `comments` is an array of `{ts,author,text}` objects (default `[]`)
- Optional orchestration fields:
  - `related_to: ["<item-id>"]` for soft context/order only
  - `scope`, `location`, `validation`: string arrays carried from OrchPlan/task shaping
  - `agent`, `role`: shaping metadata for execution handoff
  - `source: {kind, locator, source_task_id?, wave_id?}`
  - `claim: {state, owner?, executor?, wave_id?, lock_roots?, claimed_at?, lease_seconds, lease_expires_at?, heartbeat_at?, attempts}`
  - `runtime: {substrate, thread_id?, agent_id?, row_id?, output_ref?, last_event?}`
  - `proof: {state, command?, evidence_ref?, last_run_at?}`

## Read-view derived fields

`show --format json` enriches each item with:

- `dep_state`: `ready`, `waiting_on_deps`, `blocked_manual`, or `n/a`
- `waiting_on`: unresolved dependency IDs
- `in_plan`: normalized mirrored-plan membership after terminal-state demotion
- `claim_state`: effective claim state (`none|held|stale|released`)
- `claim_stale`: derived stale flag from lease state
- `lock_roots`: canonical lock roots used for wave safety checks
- `executor_state`: `idle|claimed|running|stale|released`

## In-Place Rewrite and Seq Watermark

- Seq watermark is the largest `seq` present in the stream
- Each mutation computes `seq = watermark + 1` and rewrites the file atomically
- Canonical rewrite shape is two records: one `event` (`op=replace`) and one `checkpoint`, both at the new watermark
- Checkpoint seq rule: each checkpoint `seq` must equal the watermark immediately before that checkpoint record
- Replay contract: latest checkpoint + records with `seq` greater than checkpoint `seq` must equal full replay
- Repair path: `st doctor --file .step/st-plan.jsonl --repair-seq` rewrites a canonical replace+checkpoint stream at the current watermark

## Plan-file storage policy

- The JSONL format is the same whether `.step/st-plan.jsonl` is repo-tracked or locally ignored
- On first use in a repo, ask which policy should govern `.step/st-plan.jsonl` unless the repo already makes the choice obvious
- Shared mode: keep `.step/st-plan.jsonl` tracked and ignore only the lock sidecar
- Local mode: add both `.step/st-plan.jsonl` and `.step/st-plan.jsonl.lock` to `.git/info/exclude`

## Lock sidecar policy

- Mutation paths acquire a sidecar file lock at `<plan-file>.lock` (for example `.step/st-plan.jsonl.lock`)
- In git worktrees, mutating commands require that sidecar path to be ignored (`git check-ignore`) before writes proceed
- Use `.gitignore` for the sidecar in shared mode, or `.git/info/exclude` for both plan and sidecar in local-only mode

## Translation contract to native runtime mirrors

- `emit-plan-sync` emits:

```json
{
  "version": 1,
  "items": [
    {
      "id": "st-003",
      "step": "Document v3 protocol",
      "status": "pending",
      "priority": "medium",
      "in_plan": true,
      "deps": [{"id": "st-002", "type": "blocks"}],
      "notes": "Capture rollout caveats",
      "comments": [],
      "dep_state": "ready",
      "waiting_on": []
    }
  ],
  "codex": {
    "plan": [
      {"step": "Document v3 protocol", "status": "pending"}
    ]
  },
  "opencode": {
    "todos": [
      {"content": "Document v3 protocol", "status": "pending", "priority": "medium"}
    ]
  }
}
```

- `items` is the full durable inventory in `$st` order
- `items` preserves optional orchestration metadata when present so teams/mesh reconciliation does not lose claim/runtime/proof state
- `codex.plan`, `opencode.todos`, and legacy `emit-update-plan` emit only items with `in_plan=true`
- Codex status mapping: `in_progress` -> `in_progress`, `completed` -> `completed`, `pending` -> `pending`, `blocked` -> `pending`, `deferred` -> `pending`, `canceled` -> `pending`
- OpenCode status mapping: `in_progress` -> `in_progress`, `completed` -> `completed`, `pending` -> `pending`, `blocked` -> `pending`, `deferred` -> `pending`, `canceled` -> `cancelled`
- OpenCode todo mapping: `content = step`, `priority = priority`
- Guardrail: if `dep_state == "waiting_on_deps"`, translated status must never be `in_progress` (force `pending`)
- Guardrail: multiple mirrored `in_progress` items are valid only when the underlying durable items prove a safe parallel wave via held non-overlapping claims
- Compatibility: mutation commands also print a legacy `update_plan:` line, and `emit-update-plan` still emits `{"plan":[...]}` for older Codex-only callers

## Selection semantics

- `add --backlog-only` and `import-plan --backlog-only` write items with `in_plan=false`
- `select` matches exact IDs plus simple `status` / `priority` filters and auto-includes unresolved dependency closure
- Completed dependencies do not get pulled back into the mirrored plan
- `deselect` rejects if it would leave a still-selected item depending on a backlog-only unresolved task
