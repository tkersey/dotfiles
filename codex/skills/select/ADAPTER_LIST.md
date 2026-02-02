# Select adapter: invocation list

## Detection
- Only treat an invocation task list as the source if the invocation text explicitly marks it (e.g. "Use $select" / "$select:") immediately before the list.
- If present, it is canonical: do not look at `SLICES.md`/`bd`/`plan-N.md`.

## Mode handling
- `mode` has no special meaning here; always treat list tasks as explicit work.
- Respect `max_tasks` when producing the final OrchPlan (limit total scheduled tasks, after dependency ordering).

## Task format
- Each top-level numbered/bulleted item is one task.
- Optional per-task metadata is parsed from indented `- key: value` lines.

Supported metadata (all optional):
- `id`: stable identifier (string; default `t-<n>`)
- `title`: override default title (string)
- `description`: additional detail for the worker (string)
- `agent`: `worker|orchestrator` (default `worker`)
- `scope`: list of exclusive-lock strings (paths/globs)
- `location`: list of navigation paths/globs (does not affect scheduling)
- `validation`: list of proof commands/checks (does not affect scheduling)
- `depends_on`: list of task IDs
- `subtasks`: list of tasks (only meaningful when `agent: orchestrator`)

Example:
```text
Use $select to plan:
1. Implement mol-mesh-run.
   - id: run
   - agent: worker
   - scope: ["codex/formulas/mol-mesh-run/**"]
2. Scripts workstream.
   - id: scripts
   - agent: orchestrator
   - scope: ["codex/scripts/mesh-*"]
   - subtasks:
     - Implement mesh-workspace.
       - id: ws
       - agent: worker
       - scope: ["codex/scripts/mesh-workspace"]
     - Implement mesh-gates.
       - id: gates
       - agent: worker
       - scope: ["codex/scripts/mesh-gates"]
```

## Normalization notes
- If `agent: orchestrator` but `subtasks` is missing/empty, downgrade to `worker` and warn.
- Missing `scope` means the task overlaps everything and should not be parallelized; warn unless auto-remediation infers scope.
- Unknown deps are treated as unmet blocks; warn only if auto-remediation cannot resolve them.
- If provided, pass `title`/`description`/`location`/`validation` through to the OrchPlan task.

## Schema drift detectors (warn-only; keep selecting)
- Duplicate `id` values.
- `depends_on` references an unknown id: treat as unmet dep for that task; warn only after auto-remediation; keep scheduling other tasks.
