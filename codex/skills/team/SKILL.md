---
name: team
description: "Alias for `$teams`: use native Codex teammate orchestration for composite work, then hand only homogeneous leaf batches to `$mesh`."
---

# team

`$team` is a user-facing alias for `$teams`.

Use the same workflow and guardrails as `$teams`:

- plan and decompose first
- keep the immediate blocking step local
- use `spawn_agent` for heterogeneous leaf tasks
- use `explorer` for focused questions and `worker` for bounded execution
- hand off only already-shaped, homogeneous leaf batches to `$mesh`

Canonical name in policy text and examples: `$teams`.
