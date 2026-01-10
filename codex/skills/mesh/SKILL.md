---
name: mesh
description: Orchestrate multiple Codex sub-agents via cx to work beads in parallel and deliver PRs; use whenever a bead (or set of beads) is being worked and multi-agent coordination, dependency scheduling, or progress consolidation is needed.
---

# mesh

## Workflow
1. Confirm a beads repo by running `rg --files -g '.beads/**' --hidden --no-ignore`; if no matches, stop and ask for direction.
2. Identify the target beads (explicit IDs, or `bd ready`/`bd in-progress`) and confirm scope with the user.
3. Build a dependency-aware batch plan (ready now vs blocked) and list the first wave.
4. Decide concurrency and prioritization; if unspecified, ask for a cap and a priority rule.
5. Compose one agent prompt per bead using the template below.
6. Dispatch each agent with `codex/skills/cx/scripts/cx-exec.sh "..."` (or the user’s chosen Opencode equivalent).
7. Monitor updates and require each agent to post a bead comment with PR link + verification.
8. Consolidate a single status summary: completed PRs, active blockers, and the next wave.

## Agent Prompt Template
```
Work bead <ID>. Use skill <work|imp|resolve> as appropriate.
Restate done-means + acceptance criteria.
Keep diffs bead-scoped; open a PR when done.
Record verification and PR link in the bead comment.
If blocked, state why and what is needed.
```

## Coordination Guardrails
- Prefer one bead per agent to avoid overlapping diffs.
- Do not start blocked beads; queue them behind their prerequisites.
- Treat bead comments as the canonical progress log.
- If two beads touch the same files, serialize them or explicitly define the lock order.

## Status Summary Format
```
Wave 1: <IDs>
In progress: <ID → agent>
Blocked: <ID → reason>
PRs: <ID → link>
Next wave: <IDs>
```
