---
name: mesh
description: "Use `$mesh` for homogeneous leaf-batch execution over `spawn_agents_on_csv`: CSV or file-list fanout, repeated audits, structured extraction, or other one-row-per-worker jobs after planning is done. This is a narrow batch adapter, not the default orchestration workflow."
---

# mesh

## Intent

`$mesh` is the narrow batch-execution path for Codex.

It is for already-shaped leaf work, not for planning or decomposition.

Use it when:

- the user explicitly asks for `$mesh`
- the workload is row-shaped and homogeneous
- each row can be processed independently
- you want structured per-row results exported to CSV
- planning is complete and the remaining work is leaf execution

Do not use it when:

- the work is research, review, debate, or design
- the task still needs decomposition or shared judgment
- tasks share context or depend on one another
- multiple workers would touch the same mutable scope
- direct `spawn_agent` delegation or local execution is clearer

## Native Architecture Fit

- `$mesh` maps to `spawn_agents_on_csv`, not a separate runtime protocol.
- The batch job spawns one worker sub-agent per CSV row.
- The main call blocks until the batch finishes.
- Each worker must call `report_agent_job_result` exactly once.
- Results are exported to `output_csv_path` or a default output CSV.
- Planning happens before the batch starts; `$mesh` executes the already-shaped rows.

## Recommended Uses

- audit one file per row
- classify one ticket, log chunk, or document per row
- extract structured fields from many inputs
- run the same bounded transformation over a file list with disjoint outputs

If the work is heterogeneous, use `$teams` or direct `spawn_agent` instead.

## Composite vs Leaf Fit

Use `$mesh` only when every row is already a leaf task:

- clear inputs from CSV columns
- one instruction template for every row
- no cross-row coordination
- one structured result per row

If you still need to decide the row schema, challenge the approach, or compare strategies, do that work before `$mesh`, usually with `$teams` or locally.

## Recommended Flow

1. Confirm planning is complete and the rows are truly homogeneous and independent.
2. Build a CSV with stable headers and, when useful, a stable `id_column`.
3. Write one instruction template using `{column}` placeholders.
4. Choose only the controls you need: `output_schema`, `output_csv_path`, `max_concurrency`, `max_runtime_seconds`.
5. Run `spawn_agents_on_csv`.
6. Review the exported CSV and do any integration or follow-up work locally or with `$teams`.

## Concrete Examples

### Example 1: Audit one file per row

Goal:

> Check every markdown file for required frontmatter keys and export one result row per file.

Example CSV:

```csv
id,path
1,docs/intro.md
2,docs/setup.md
```

Example instruction template:

```text
Inspect {path}. Report whether the required frontmatter keys exist and list any missing keys.
```

Why `$mesh`:

- every row uses the same template
- every row is independent
- the result can be captured as one structured object per file

### Example 2: Classify support tickets

Goal:

> Classify 2,000 support tickets by product area and urgency, then export the labels to CSV.

Example CSV:

```csv
ticket_id,text
T-1001,"Billing page shows a 500 error"
T-1002,"How do I rotate an API key?"
```

Example output schema:

```json
{
  "type": "object",
  "properties": {
    "area": { "type": "string" },
    "urgency": { "type": "string" },
    "needs_human": { "type": "boolean" }
  },
  "required": ["area", "urgency", "needs_human"]
}
```

Why `$mesh`:

- this is repeated, read-only classification work
- the schema makes the per-row output easy to compare and post-process

### Example 3: Disjoint file transformation

Goal:

> Rewrite a large set of generated summaries, one output file per input file, with no shared destinations.

Good `$mesh` setup:

- CSV columns such as `id,input_path,output_path`
- one instruction template that reads `{input_path}` and writes only `{output_path}`
- one JSON result confirming whether the row succeeded

Why `$mesh`:

- the write scopes are disjoint
- the same bounded transformation repeats for every row

### Counterexample: one feature across shared code

Do not use `$mesh` for:

> Add a feature that changes shared parser logic, server behavior, and the UI.

Why not:

- the work still needs decomposition and coordination
- the rows would not be independent
- shared mutable files make `$teams` or local execution the safer path

## Row Design Rules

- Keep each row objective concrete and bounded.
- Prefer read-only work or disjoint write scopes.
- Keep result objects structured and comparable across rows.
- Use stable row ids when you will reconcile outputs later.
- If rows need shared mutable state, stop and switch away from `$mesh`.
- If a row still needs planning, stop and finish decomposition before running the batch.

## Result Contract

- Every worker must report exactly one JSON result via `report_agent_job_result`.
- Missing reports are failures.
- Narrative text is non-authoritative; the structured result is what matters.
- If you provide an `output_schema`, keep it minimal and aligned with the fields you actually need.

See `references/output-contract.md`.

## Anti-patterns

- using `$mesh` as a general replacement for `$teams`
- doing recursive planning or debate inside the batch workers
- splitting one tightly coupled implementation across dependent rows
- overlapping write scopes across rows
- relying on free-form text instead of structured result fields
- reusing the same path for `csv_path` and `output_csv_path`

See `references/orchestration-anti-patterns.md`.

## Final Response

When mesh actually ran, include a short `Orchestration Ledger` in prose.

Good fields:

- `Skills used`
- `Subagents`
- `Artifacts produced`
- `Cleanup status`

Omit the section entirely when no orchestration ran.

## Handoff From `$teams`

If `$teams` hands work to `$mesh`, the handoff should include:

- confirmation that planning is complete and only leaf execution remains
- the CSV or row schema
- the instruction template
- the expected output fields
- any concurrency or timeout assumptions

Do not add extra lane, quorum, or state-machine protocols unless the runtime actually provides them.
