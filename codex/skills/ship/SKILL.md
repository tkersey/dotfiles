---
name: ship
description: "Finalize work after validation: confirm a signal, capture proof in PR description and bead comment (if beads), and open a PR (no merge). Use when asked to ship, finish, or open a PR."
---

# Ship

## Overview
Finalize deliverables after validation and produce a concise proof trail.

## Workflow
1. Confirm a recent validation signal exists for the current change set; if not, run `validate`.
2. Summarize proof: commands/signals and outcomes.
3. If beads are used, comment on the active bead with the proof (only if `.beads` exists: `rg --files -g '.beads/**' --hidden --no-ignore`).
4. Open a PR (do not merge), using `gh` where applicable.
5. Report PR status and any remaining follow-ups.

## Guardrails
- Never ship without a signal.
- Keep proof concise and scoped to this change.
- If PR creation is blocked (auth/remote), state the exact blocker and next command.

## Output
- Proof summary (signals + results).
- PR creation status.
- Next steps if any.
