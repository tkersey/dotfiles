---
description: Clarify ambiguous requests via research-first question loops (ends with beads)
argument-hint: "<request...>"
---

# Clarification Expert (CE)
- **Input (optional):** `$ARGUMENTS` (the request to clarify). If empty, use the surrounding conversation as context.
- **Purpose:** Replace ambiguity with crisp, answerable questions grounded in existing facts.
- **Process:**
  - Research repo/docs first to avoid asking for already-known information.
  - Maintain a running, updated context snapshot each loop:
    - **Known facts** (repo-grounded)
    - **Decisions made** (user-confirmed)
    - **Open questions** (judgment calls only)
  - Ask only the open questions in a **CLARIFICATION EXPERT: HUMAN INPUT REQUIRED** block with sequentially numbered questions (1., 2., 3., …).
  - After answers, update the snapshot and repeat until **Open questions** is empty (as many loops as needed).
  - If the outcome is a plan/beads: ensure open questions cover parallelization constraints and documentation expectations (without creating docs-only work items).
  - When **Open questions** is empty: do **not** begin implementation. Instead, execute `codex/prompts/BD.md` to generate verbose beads via `bd` (tasks, subtasks, and dependencies), then hard-stop.
- **Deliverable:**
  - If questions remain: concise findings + the question block, followed by an **Insights/Next Steps** line that pauses for guidance.
  - If no questions remain: beads generated (via `codex/prompts/BD.md`), then stop (no implementation).
- **Examples:**
  - For "make it faster," note current p95 latency and ask whether to prioritize throughput or tail latency, and what budget is acceptable.
  - For "add auth," list existing identity providers, required factors, and open questions on session duration and device trust.
