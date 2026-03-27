---
name: mesh
description: "Use `$mesh` only for homogeneous leaf-batch execution over `spawn_agents_on_csv`: once planning has shaped repeated independent units, prefer one substantive row per unit with structured results and explicit concurrency."
---

# mesh

## Intent

`$mesh` is the high-fanout batch-execution path for Codex once repeated leaf work has been shaped.

It is for already-shaped leaf work, not for planning or decomposition.

Use it when:

- the user explicitly asks for `$mesh`, or repeated leaf work is already clearly row-shaped
- the workload is row-shaped and homogeneous
- each row can be processed independently
- each row represents one substantive unit with a unique scope and acceptance target
- you want structured per-row results exported to CSV
- planning is complete and the remaining work is leaf execution

Do not use it when:

- the work is research, review, debate, or design
- the task still needs decomposition or shared judgment
- tasks share context or depend on one another
- multiple workers would touch the same mutable scope
- `$teams` or local execution is clearer

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
- execute one disjoint implementation unit per row after `$select` or `$teams` has already shaped the wave

If the work is heterogeneous, use `$teams` or local execution instead.

## Composite vs Leaf Fit

Use `$mesh` only when every row is already a leaf task:

- clear inputs from CSV columns
- one instruction template for every row
- no cross-row coordination
- one structured result per row

If you still need to decide the row schema, challenge the approach, or compare strategies, do that work before `$mesh`, usually with `$teams` or locally.

## Substantive-unit rule

- One row should represent one unique work unit with one unique write or read scope and one acceptance target.
- Do not multiply rows over the same scope merely to create more lanes, more evidence, or a higher concurrency number.
- Treat a clean primary row as sufficient evidence for that unit.
- Only add secondary review, coder, fixer, prover, or integration rows when a prior row reports a concrete blocker, a failed proof, or a non-trivial diff that needs another pass.
- Deprecated shims (`reducer`, `mentor`, `locksmith`, `applier`) are never valid fresh rows.

## Recommended Flow

1. Confirm planning is complete and the rows are truly homogeneous and independent.
2. Durable `$st` is the default handoff for non-trivial OrchPlan execution: import and claim the selected wave before building the CSV.
3. Do not preserve a public same-turn non-`$st` handoff. If a helper still exists, it must auto-route into the same durable path internally.
4. Build a CSV with stable headers and, when useful, a stable `id_column`; keep one row per substantive unit.
   - Prefer `task_id` as the stable row id when the batch came from an OrchPlan or `$st` claim set.
5. Write one instruction template using `{column}` placeholders and one primary deliverable per row.
6. Choose only the controls you need: `output_schema`, `output_csv_path`, `max_concurrency`, `max_runtime_seconds`; set `max_concurrency` to the safe row count unless a lower cap is required.
7. Run `spawn_agents_on_csv`.
8. Only queue secondary rows for units that reported a concrete blocker, a failed proof, or a non-trivial diff needing another pass.
9. Review the exported CSV and do any integration or follow-up work locally or with `$teams`.
   - If `$st` owns execution state, reconcile the export with `st import-mesh-results --input <output.csv>` before closing the wave.

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

### Example 4: Disjoint implementation units

Goal:

> Execute the first safe implementation wave from an OrchPlan where each task already owns a disjoint scope.

Good `$mesh` setup:

- CSV columns such as `id,objective,write_scope,proof_command`
- one primary row per implementation unit, not one row per reviewer lane
- `max_concurrency` set to the number of safe disjoint units
- follow-up prover or fixer rows added only for units that failed proof or reported blockers

Why `$mesh`:

- the work is repeated leaf execution after planning is complete
- each row owns a unique scope and has a concrete acceptance target
- the batch gets real fanout without inventing synthetic evidence lanes

### Counterexample: one feature across shared code

Do not use `$mesh` for:

> Add a feature that changes shared parser logic, server behavior, and the UI.

Why not:

- the work still needs decomposition and coordination
- the rows would not be independent
- shared mutable files make `$teams` or local execution the safer path

## Row Design Rules

- Keep each row objective concrete and bounded.
- Make each row one substantive unit with a unique scope and acceptance target.
- Keep `write_scope` aligned with the canonical lock-root contract in `codex/skills/select/references/lock-roots.md`.
- Prefer read-only work or disjoint write scopes.
- Keep result objects structured and comparable across rows.
- Use stable row ids when you will reconcile outputs later.
- Do not multiply rows by role or lane on the same scope unless a blocker or failed proof justifies the follow-up.
- If you need reduction thinking, keep it inside `coder` by setting `approach=reduce`; do not resurrect `reducer` as a new row type.
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
- launching a synthetic evidence wave after the substantive work is already done
- multiplying coder/fixer/prover/integrator rows over the same scope without a blocker-triggered reason
- routing fresh work through deprecated shims instead of the live core roles
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
