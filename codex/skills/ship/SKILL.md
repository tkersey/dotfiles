---
name: ship
description: "Finalize work after validation: confirm a signal, capture proof in the PR description, and open a PR (no merge). Use when asked to run `$ship`, ship/finalize a branch, prepare or open a PR without merging, or publish validation proof before handoff."
---

# Ship

## Overview
Finalize deliverables after validation and produce a concise proof trail.

## Workflow
1. Confirm a recent validation signal exists for the current change set; if not, run `validate`.
2. Summarize proof: commands/signals and outcomes.
3. Capture the proof directly in the PR description (or update the PR body if it already exists).
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
