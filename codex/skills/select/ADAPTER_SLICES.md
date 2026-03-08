# Select adapter: SLICES.md (schema_version: 1)

## Scope
- Source file is repo-root `SLICES.md`.
- This adapter is read-only (no edits to `SLICES.md`).

## Mode handling
- `mode: triage`: run triage; emit recommendations; do not select new work.
- `mode: new`: skip triage; still warn if any slice is `in_progress`; select new work.
- `mode: both` (default): triage first; if triage selects `continue`, keep that slice selected and continue selecting additional disjoint ready work. Only stop immediately if `max_tasks: 1` or no other safe ready work exists.

## Parse + model
- Parse each slice YAML mapping.
- Required: `id`, `title`.
- Optional: `status`, `issue_type`, `priority`, `parent_id`, `dependencies`, `scope`, `location`, `verification`, `description`.

Status normalization (before triage/selection):
- Trim + lowercase.
- Map `in progress` and `in-progress` to `in_progress`.

## Schema drift detectors (warn-only; keep selecting)
- Duplicate `id` values.
- Missing/empty `id` or `title`.
- Unknown `status` values after normalization (treat as not-closed and not-in-progress).
- Unknown `issue_type` values (treat as workable unless it is exactly `epic`).
- `parent_id` points to an unknown `id` (treat as top-level; warn).
- `dependencies` entries missing `type` or `depends_on_id` (treat as unmet blocks; warn).
- `subtasks` contains values that look like slice IDs (e.g. `sl-...`): warn that subtasks may be overloaded; this adapter still treats `subtasks` as a checklist.

## Hierarchy
- The slice tree is defined only by `parent_id`.
- A slice is **non-leaf** if any other slice has `parent_id: <this id>`.
- Ignore `subtasks` for hierarchy; treat it as a checklist field.

## Workable slices
- Never schedule `issue_type: epic`.
- Only schedule **leaf** slices.

## Dependencies + derived readiness
- Only `dependencies[].type == blocks` gates readiness.
- Map non-`blocks` dependency entries into task `related_to` links (soft ordering/context; non-gating).
- A leaf slice is **ready** iff every `blocks` dep points to a known slice with `status: closed`.
- Unknown dep IDs: treat the slice as blocked; warn only after auto-remediation; keep selecting other work.
- If `status` disagrees with derived readiness, warn and use derived readiness for selection.

## In-progress triage (must run first)
Goal: if any **leaf** slice is `status: in_progress` (after normalization), decide whether to continue it, recommend closing it, or recommend reopening it.

Best-effort proofs (read-only checks allowed; stable order; stop at first strong signal):

- Completion proof ("exists == done"):
  1. If the slice has explicit, safe, non-interactive `verification` commands, run them; success is completion proof.
  2. Otherwise, check for concrete existence of the primary artifacts named by the slice (files, CLI subcommands, flags, modules). If the artifacts exist and are not obvious stubs, treat as completion proof.

- Active proof:
  1. GitHub: open PRs whose title/body/branch mentions the slice `id`.
  2. Git: local branches whose name contains the slice `id`.
  3. Git: recent commits whose message contains the slice `id`.
  4. Git: working-tree changes *and* the current branch/last commit clearly ties to the slice `id`.

Decision (plan-only; no writeback):
- If completion proof exists: recommend closing it; then proceed to select new work.
- Else if active proof exists: keep this slice selected as carry-forward work, then continue selecting additional disjoint ready slices up to the resolved `max_tasks` or wave cap.
- Else (no active proof): recommend reopening it (set back to `open`); then proceed to select new work.

Staleness policy:
- "No ACTIVE proof" is sufficient to treat `in_progress` as stale (no time window).

## Selecting new work
New-work candidates:
- Leaf + workable + derived-ready
- Status is not `closed` and not `in_progress` (after normalization)

Respect `max_tasks`:
- Default for `slices` is `max_tasks: auto` unless explicitly overridden.
- `auto` means: claim the full first safe wave after triage, dependency, and scope checks, even when one carried-forward `in_progress` slice remains selected.
- If `max_tasks` is a number, select at most that many tasks (in stable source order after tie-breaks).

If no ready new-work candidates exist:
- Select an unblocker: a workable leaf slice that is closest to ready.
- Prefer: fewest unmet `blocks` deps, then highest unlock count (direct+indirect), then highest priority, then stable order.
- If the only blockers are schema/graph integrity issues (unknown dep IDs, cycles, malformed entries), emit a synthetic task `repair-slices` with `scope: ["SLICES.md"]` and explain what to fix.

## Parallelism
- SLICES tasks often omit `scope`; try safe scope inference before falling back to sequential scheduling.
- Infer from explicit `scope` first, then `location`, `verification`, and path-bearing text in `id`/`title`/`subtasks`.
- Prefer file or module globs over directory-root locks when inference is possible.
- If `scope` can be inferred by auto-remediation, use it and suppress the missing-scope warning.
- Only schedule sequentially when no defensible narrow scope can be derived.
- If a slice provides a `scope` list, pass it through to the OrchPlan task.
- Keep soft dependency intent in `related_to`; do not convert it into blocking edges.
- If a slice provides `verification`, map it to the OrchPlan task's `validation` (best-effort):
  - If `verification` is a YAML list, use it as-is.
  - If `verification` is a string, split into non-empty lines; trim leading `-` bullet markers.

## Decision Trace notes
- `counts` should be computed from derived readiness (not raw `status`).
- `pick` reason should name the winning tie-break (priority/unlocks/fewest unmet blocks).
- `fanout_possible` should count the maximum safe first-wave width after triage, dependency, and scope checks.
- `fanout_selected` is the number of tasks actually placed into `waves[0]`.
- `fanout_left_on_table` is `fanout_possible - fanout_selected`; it should be `0` unless `max_tasks` was explicitly capped or unresolved overlap remains.
