# Mesh Batch Result Contract

`$mesh` uses `spawn_agents_on_csv` as a batch runner. The authoritative worker output is the
worker-only `report_agent_job_result` call.

## Core Rule

Each worker must call `report_agent_job_result` exactly once with:

- `job_id`
- `item_id`
- `result`: a JSON object

Missing reports are failures.

## Result Shape

Keep `result` small, stable, and useful downstream.

Recommended fields:

- `id`: stable row identifier when useful
- `status`: short machine-friendly outcome such as `ok`, `skip`, or `error`
- row-specific fields you actually need later
- `summary`: optional short human-readable summary
- `error`: optional concise failure detail

Avoid giant blobs, raw transcripts, or patch payloads unless the batch genuinely needs them.

## `output_schema`

If you pass `output_schema` to `spawn_agents_on_csv`, make it describe only the fields you plan to
consume later. Keep it minimal and aligned with the actual result keys.

Example schema:

```json
{
  "type": "object",
  "required": ["id", "status", "summary"],
  "properties": {
    "id": { "type": "string" },
    "status": { "type": "string" },
    "summary": { "type": "string" },
    "path": { "type": "string" }
  },
  "additionalProperties": false
}
```

Example result:

```json
{
  "id": "file-17",
  "status": "ok",
  "summary": "Uses deprecated API in one helper",
  "path": "src/helpers/api.ts"
}
```

## Notes

- Narrative assistant text is non-authoritative compared with the structured result.
- Use `stop: true` only when one worker has discovered a job-wide reason to stop future items.
- If you need multi-step coordination between rows, the task is probably not a good fit for `$mesh`.
