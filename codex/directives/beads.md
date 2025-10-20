# beads Agent Directive

**Mission**  
Use the `bd` CLI to own the single canonical workstream. Keep every task, blocker, and follow-up inside Beads so humans never have to reconcile Markdown lists again. v0.9.x expects a single active stream—finish or close the current one before spawning a new track. Default to the `bd` binary with `--json`; only reach for the MCP server when you are certain it targets this repo.

## Daily Loop
- Start: `bd list --status in_progress --json` to resume anything mid-flight. If nothing is active, run `bd ready --json` and pick the highest-priority issue.
- Inspect context with `bd show <id> --json`. Relay the key details back to the user before acting.
- Claim work by moving it to in-progress: `bd update <id> --status in_progress --json`. Always reflect blockers or progress changes immediately.

## Working Issues
- While implementing, log meaningful breadcrumbs: `bd comments add <id> "what changed / what's next"` so the next session can continue smoothly.
- If you discover a blocker, mark the current issue blocked (`bd update <id> --status blocked --json`), create the blocker issue (see below), and link them before doing anything else.
- Wrap up with `bd close <id> --reason "Short, user-facing result" --json`. If work is incomplete, reset to open and leave a comment explaining why.

## Creating & Linking Work
- New work you discover: `bd create "Title" -t bug|task|feature -p 0-4 --deps discovered-from:<current-id> --json`. Include enough description for an offline human review.
- To express hard dependencies after the fact: `bd dep add <child> <parent> --type blocks`. Use `discovered-from` for lateral context and `parent-child` for epic/subtask relationships.
- Keep priorities honest: 0 = critical, 1 = high, 2 = normal, 3 = low polish, 4 = backlog. Default to 2 if unsure.
- Use labels sparingly but consistently: `bd label add <id> backend`, `bd label remove <id> legacy`.

## Sync & Hygiene
- Auto import/export keeps `.beads/issues.jsonl` in sync; no manual `bd export` needed unless you want an ad-hoc snapshot, and never hand-edit the JSONL or SQLite files directly.
- If you touched the repo outside `bd` (e.g., git pull with issue changes), run `bd sync --dry-run` to preview and resolve collisions before pushing.
- When the daemon auto-starts, let it run. Only fall back to `--no-daemon` if you see repeated connection failures.

## When Unsure
- `bd quickstart` gives the official tutorial; skim it whenever the workflow feels fuzzy.
- `bd ready --limit 5 --json` surfaces the short list of unblocked issues; use it whenever you lose the plot.
- Ask the user before renumbering, renaming prefixes, or running destructive imports. These commands mutate IDs and should never be surprise operations.

Stay disciplined: every piece of work goes into Beads, every state change is explicit, and every session ends with no stray in-progress issues unless intentionally paused with a comment.
