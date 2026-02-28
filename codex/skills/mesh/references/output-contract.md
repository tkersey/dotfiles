# Mesh Output Contract (Strict Mode)

Mesh runs fail fast when worker results are ambiguous.

When using `spawn_agents_on_csv` (Codex agent jobs), the canonical output channel is the
worker-only tool `report_agent_job_result`, not free-form text.

## Required Reporting Mechanism

Every worker MUST call `report_agent_job_result` exactly once with:

- `job_id`: the Job ID provided in the worker prompt
- `item_id`: the Item ID provided in the worker prompt
- `result`: a JSON object containing the unit result (see required keys below)

If a worker finishes without calling `report_agent_job_result`, the item is marked failed with
`last_error` like `worker finished without calling report_agent_job_result`.

Important:

- `report_agent_job_result` is a worker-only tool. Non-agent-job threads typically do not have it.
- Even if the tool exists, results are only accepted when reported from the worker thread that
  owns that job item; wrong-thread calls return `accepted: false` and the item will still fail.

## Required `result` Keys

Mesh expects these fields inside the `result` JSON object (they will be exported under the
`result_json` column in the output CSV):

- `id`: unit id (string; should match the CSV row id)
- `candidate_id`: unique candidate id for the lane row (string)
- `triplet_index`: candidate index within the lane cohort (`1..3`)
- `decision`: `accept` | `reject` | `no_diff`
- `proof_status`: `pass` | `fail` | `skipped`

If a lane is intentionally collapsed, still report `candidate_id` and set `triplet_index` to `1`.

Recommended optional keys:

- `failure_code`: one of the Mesh failure taxonomy codes (only when `decision != accept`)
- `blockers`: array of blocker labels that force reject semantics
- `challenge_findings`: peer-review findings (required for coder triplet lanes)
- `patch`: an `apply_patch`-format patch string (when proposing changes)
- `notes`: short explanation; for no-change use `NO_DIFF:<reason>`

Examples:

Coder lane (propose patch, no proof):

```json
{
  "id": "u-001",
  "candidate_id": "u-001-coder-1",
  "triplet_index": 1,
  "decision": "accept",
  "proof_status": "skipped",
  "challenge_findings": [
    "Peer candidate 2 omits CSRF coverage on mutating route",
    "Peer candidate 3 broadens scope beyond unit boundary"
  ],
  "patch": "*** Begin Patch\n*** Update File: src/foo.txt\n@@\n-Old\n+New\n*** End Patch\n",
  "notes": "Proposed minimal patch; proof deferred to integrator."
}
```

No-diff lane:

```json
{
  "id": "u-002",
  "candidate_id": "u-002-fixer-2",
  "triplet_index": 2,
  "decision": "no_diff",
  "proof_status": "skipped",
  "notes": "NO_DIFF: already satisfies acceptance criteria"
}
```

If `result_json` is missing, not a JSON object, or cannot be parsed, classify as
`invalid_output_schema`.

## Early Stop (Cancel Remaining Items)

If a worker encounters a global blocker and wants to stop the job early, it may include
`stop: true` in the `report_agent_job_result` call.

Effect:

- The job is marked `Cancelled`.
- Remaining items stay `pending` (no worker runs) and their `result_json` stays empty.

Use `stop: true` only for global blockers (missing dependency, invalid spec, dangerous invariant
break) where completing remaining items would be wasted work.

## Recommended `output_schema`

`spawn_agents_on_csv` can be given an `output_schema` (not runtime-validated) which is shown to
workers as guidance. For mesh, prefer a JSON Schema object like:

```json
{
  "type": "object",
  "required": ["id", "candidate_id", "triplet_index", "decision", "proof_status"],
  "properties": {
    "id": {"type": "string"},
    "candidate_id": {"type": "string"},
    "triplet_index": {"type": "integer", "minimum": 1, "maximum": 3},
    "decision": {"type": "string", "enum": ["accept", "reject", "no_diff"]},
    "proof_status": {"type": "string", "enum": ["pass", "fail", "skipped"]},
    "failure_code": {"type": "string"},
    "blockers": {"type": "array", "items": {"type": "string"}},
    "challenge_findings": {"type": "array", "items": {"type": "string"}},
    "patch": {"type": "string"},
    "notes": {"type": "string"}
  }
}
```
