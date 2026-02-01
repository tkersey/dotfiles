# Select adapter: bd (beads)

## When available
- Only use this adapter when `.beads/` exists and `bd` works.

## Mode handling
- `mode: triage`: triage any `in_progress`, then stop.
- `mode: new`: skip triage; still warn if any bead is `in_progress`; select new work.
- `mode: both` (default): triage first; if triage selects `continue`, stop; otherwise select new work.

## Read-only commands
- Active work: `bd list --status in_progress --limit 50`
- Ready work: `bd ready`
- Inspect: `bd show <id>`

## Mapping
- Map bead -> task:
  - `id`: bead id
  - `title`: bead title
  - `depends_on`: bead `blocks` dependencies
  - `scope`: usually unknown (expect sequential scheduling)

## In-progress triage (skeptical)
If any bead is `in_progress`:
- Completion proof ("exists == done"): you can point to concrete existence evidence that the bead's acceptance/verification is satisfied in the current codebase.
- Active proof: you can point to concrete evidence of ongoing WIP tied to the bead id (PR/branch/commit/diff).

Decision (plan-only; no writeback):
- If completion proof exists: recommend closing it; then proceed to select new work.
- Else if active proof exists: select it as the only task to work on; stop.
- Else (no active proof): recommend reopening it; then proceed to select new work.

## Selection
- Prefer tasks returned by `bd ready`.
- If `bd ready` is empty, pick an unblocker from blocked tasks (fewest unmet blocks, highest unlock count).

Respect `max_tasks`:
- Default for `beads` is `max_tasks: 1` unless explicitly overridden.

## Schema drift detectors (warn-only; keep selecting)
- Bead referenced by `blocks` dep is missing/unreadable: treat as unmet dep; warn.

## Guardrails
- Never run mutating bd commands from `$select` (`bd update`, `bd close`, `bd dep add`, comments, etc.).
