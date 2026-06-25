# st JSONL Format (v3/v4)

## Record lanes

`st` uses an in-place rewritten JSONL stream; each line is one v3 or v4 record.

- Shared fields: `v` (`3`), `ts` (UTC ISO-8601), `seq` (non-negative integer), `lane` (`event` or `checkpoint`)
- `event` lane: requires `op`
- `checkpoint` lane: requires full `items` snapshot
- Optional event/checkpoint metadata envelope: `mutation` (writer audit details such as policy flag/actor/session)

```json
{"v":3,"ts":"2026-02-09T20:02:00Z","seq":42,"lane":"event","op":"replace","items":[{"id":"st-001","step":"Reproduce issue","status":"completed","priority":"medium","in_plan":false,"deps":[],"notes":"","comments":[]}],"mutation":{"allow_multiple_in_progress":false,"actor":"tk","pid":12345}}
{"v":3,"ts":"2026-02-09T20:02:00Z","seq":42,"lane":"checkpoint","items":[{"id":"st-001","step":"Reproduce issue","status":"completed","priority":"medium","in_plan":false,"deps":[],"notes":"","comments":[]}],"mutation":{"allow_multiple_in_progress":false,"actor":"tk","pid":12345}}
```

## v4 graph envelope

v3 files remain readable. Graph mode activates on the first graph mutation and writes v4 records with a durable graph envelope:

```json
{
  "v": 4,
  "ts": "2026-06-03T00:00:00Z",
  "seq": 42,
  "lane": "checkpoint",
  "graph": {
    "version": 1,
    "policy": {
      "completion_requires_proof": true,
      "implementation_ready_required": true,
      "default_projection_strategy": "aperture-score",
      "default_gate": "implementation-ready",
      "max_aperture_items": 7
    },
    "intent": [],
    "waivers": [],
    "polish": {"session_id": "", "passes": []},
    "fingerprints": {"structure": "", "contract": "", "coverage": "", "execution": ""}
  },
  "items": []
}
```

The v4 envelope is durable-only. It never appears inside `plan_sync.codex.plan` or `plan_sync.opencode.todos`.

## Graph policy

- `completion_requires_proof`: graph-mode completion requires proof receipts unless explicitly waived.
- `implementation_ready_required`: aperture eligibility requires implementation-ready item structure.
- `default_projection_strategy`: default graph projection ranking, normally `aperture-score`.
- `default_gate`: default graph compiler gate, normally `implementation-ready`.
- `max_aperture_items`: default bounded native projection size.

## Intent atoms

Intent atom shape:

```json
{
  "id": "intent-001",
  "source": {"kind": "markdown", "locator": "docs/plan.md", "anchor": "Authentication"},
  "text": "OAuth login must support Google and GitHub providers.",
  "category": "requirement",
  "disposition": "covered",
  "reason": ""
}
```

Allowed categories include `requirement`, `constraint`, `non-goal`, `risk`, `compatibility`, `migration`, `test-expectation`, `user-behavior`, `architecture`, `performance`, `security`, `accessibility`, `observability`, and `documentation`. Covered intent must be referenced by at least one item; non-covered dispositions require a reason or waiver.

## Waivers

Waivers are first-class graph objects:

```json
{
  "id": "waiver-001",
  "gate": "implementation-ready",
  "code": "missing-e2e-validation",
  "target": "st-014",
  "reason": "Unit and CLI integration tests are the accepted proof surface.",
  "expires": "on-next-touch",
  "created_at": "2026-06-03T00:00:00Z",
  "created_by": "codex"
}
```

MVP expiry values are `never` and `on-next-touch`. A waiver suppresses only the exact `gate + code + target` finding.

## Polish passes and fingerprints

`graph.polish.passes[]` stores fixed-point snapshots:

```json
{
  "pass": 1,
  "seq": 14,
  "created_at": "2026-06-03T00:00:00Z",
  "structure_fingerprint": "sha256:...",
  "contract_fingerprint": "sha256:...",
  "coverage_fingerprint": "sha256:...",
  "execution_fingerprint": "sha256:...",
  "audit_gate": "implementation-ready",
  "hard_failures": 0,
  "warnings": 0,
  "delta": {"items_added": 0, "items_removed": 0, "items_split": 0, "deps_changed": 0, "contracts_changed": 0, "intent_coverage_changed": 0}
}
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
- Optional graph capsule fields:
  - `item_type`: `epic`, `feature`, `task`, `bug`, `test`, `verification`, `docs`, `chore`, `research`, `spike`, or `decision`
  - `parent_id`: hierarchy only
  - `links`: nonblocking graph links such as `{id,type,reason?}`
  - `intent_refs`: covered intent IDs
  - `acceptance`: user-visible done criteria
  - `contract`: structured objective/background/approach/success criteria/proof obligations/risks
  - `labels`, `lock_roots`, `uncertainty`, `non_goals`

## Graph patch output lines

`st graph apply` and compile wrappers mutate graph state atomically. On success they emit:

```text
plan_sync: {...}
graph_delta: {"version":1,"seq_before":41,"seq_after":42,"items_added":["st-014"],"items_removed":[],"items_changed":[],"intent_coverage_changed":["intent-001"]}
audit_summary: {"gate":"implementation-ready","ok":true,"errors":0,"warnings":0,"top_findings":[]}
```

Patch ops include intent upserts, item upserts/removals, status/priority/contract/acceptance/validation/location/scope/labels/lock-root updates, dependency/link updates, reparenting, comments, and audit waivers.

## Audit output shape

`st graph audit --format json` emits:

```json
{
  "version": 1,
  "gate": "implementation-ready",
  "ok": true,
  "summary": {"items": 1, "open": 1, "ready": 1, "blocked": 0, "terminal": 0, "intent": 1, "covered_intent": 1, "waived_intent": 0, "unknown_intent": 0, "errors": 0, "warnings": 0},
  "findings": [],
  "waivers": [],
  "fingerprints": {"structure": "sha256:...", "contract": "sha256:...", "coverage": "sha256:...", "execution": "sha256:..."}
}
```

Finding shape is `{code,severity,target,message,waived,waiver_id}`.

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
- Repair path: `st doctor --file .ledger/st/st-plan.jsonl --repair-seq` rewrites a canonical replace+checkpoint stream at the current watermark

## Plan-file storage policy

- The JSONL format is the same whether `.ledger/st/st-plan.jsonl` is repo-tracked or locally ignored
- On first use in a repo, ask which policy should govern `.ledger/st/st-plan.jsonl` unless the repo already makes the choice obvious
- Shared mode: keep `.ledger/st/st-plan.jsonl` tracked and ignore only the lock sidecar
- Local mode: add both `.ledger/st/st-plan.jsonl` and `.ledger/st/st-plan.jsonl.lock` to `.git/info/exclude`

## Lock sidecar policy

- Mutation paths acquire a sidecar file lock at `<plan-file>.lock` (for example `.ledger/st/st-plan.jsonl.lock`)
- In git worktrees, mutating commands require that sidecar path to be ignored (`git check-ignore`) before writes proceed
- Use `.gitignore` for the sidecar in shared mode, or `.git/info/exclude` for both plan and sidecar in local-only mode

## Translation contract to native runtime mirrors

- `prime` and mutating commands emit `plan_sync`:

```json
{
  "version": 3,
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
      {"step": "[st-003] Document v3 protocol", "status": "pending"}
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
- `items` preserves optional execution metadata when present so reconciliation does not lose claim/runtime/proof state
- `codex.plan` and `opencode.todos` include only projection-eligible items with `in_plan=true`
- In graph mode, `st prime --mode aperture` selects a bounded executable aperture before emitting the same projection-only `plan_sync` shape
- Hook-managed SessionStart hydration must short-circuit when `codex.plan` would be empty after terminal-state demotion or backlog-only filtering
- Codex status mapping: `in_progress` -> `in_progress`, `completed` -> `completed`, `pending` -> `pending`, `blocked` -> `pending`, `deferred` -> `pending`, `canceled` -> `pending`
- OpenCode status mapping: `in_progress` -> `in_progress`, `completed` -> `completed`, `pending` -> `pending`, `blocked` -> `pending`, `deferred` -> `pending`, `canceled` -> `cancelled`
- OpenCode todo mapping: `content = step`, `priority = priority`
- Guardrail: if `dep_state == "waiting_on_deps"`, translated status must never be `in_progress` (force `pending`)
- Guardrail: multiple mirrored `in_progress` items are valid only when the underlying durable items prove a safe parallel wave via held non-overlapping claims
- Reverse sync is projection-only through `reconcile-codex --transcript-path`; it must preserve durable-only metadata.

## Selection semantics

- `add --backlog-only` and `import-plan --backlog-only` write items with `in_plan=false`
- `select` matches exact IDs plus simple `status` / `priority` filters and auto-includes unresolved dependency closure
- Completed dependencies do not get pulled back into the mirrored plan
- `deselect` rejects if it would leave a still-selected item depending on a backlog-only unresolved task
