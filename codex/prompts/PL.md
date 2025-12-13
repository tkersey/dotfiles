---
description: Clarify a request, then generate dependency-aware beads (no execution)
argument-hint: "<planning request...>"
---

# Plan (PL)
- **Input:** `$ARGUMENTS` (what you want planned). If empty or ambiguous, ask for clarification before doing anything.
- **Purpose:** Run a full Clarification Expert loop, then generate a parallelizable, documentation-rich bead plan in `bd`.
- **Non-goal:** Do **not** implement code. PL ends after creating beads.

- **Process (Clarify → Beads → Hard stop)**
  1. **Confirm the right bd database/repo**
     - Run: `bd info --json`
     - If the database/repo looks wrong, stop and ask where planning should be recorded.
  2. **Research first**
     - Inspect the repo to answer factual questions yourself (stack, existing patterns, constraints).
     - Do not ask the user questions the code/docs can answer.
  3. **Maintain a running snapshot (update every loop)**
     - **Known facts** (repo-grounded)
     - **Decisions made** (user-confirmed)
     - **Open questions** (judgment calls only)
  4. **Clarification loop (keep looping until empty)**
     - Ask **only** the open questions in a **CLARIFICATION EXPERT: HUMAN INPUT REQUIRED** block with numbered questions.
     - Answer any user questions, incorporate answers into **Decisions made**, and then re-check for new **Open questions**.
     - Repeat until **Open questions** is empty and the user has no further questions for you.
  5. **Generate beads (create issues immediately)**
     - Ensure the `memory` template exists (seed if missing):
       - Run: `bd template list --json`
       - If `memory` is missing, create `.beads/templates/memory.yaml` with the contents in `codex/prompts/BD.md` (and ensure `.gitignore` allows committing it).
     - Use the `memory` template for all beads:
       - `bd create --from-template memory ... --json`
     - If you cannot seed templates (e.g., read-only), fall back to template-free creation:
       - `bd create -t <type> -p <priority> "<title>" --description "<...>" --design "<...>" --acceptance "<...>" --json`
     - Prefer **multiple epics** (not one mega-epic) as parallel workstreams; group by component/surface area to minimize merge conflicts.
     - Use hierarchical subtasks under epics when it helps coordination:
       - `bd create --parent <epic-id> -t task "..." --description "<...>" --design "<...>" --acceptance "<...>" --json`
     - Make beads **parallelizable**:
       - Keep bead scope atomic and “one agent can finish it”.
       - Use `blocks` dependencies only when truly required; prefer independent work.
     - Make beads **documentation-rich without dedicated docs beads**:
       - **Never** create a docs-only bead.
       - Instead, every bead’s `description`/`design`/`acceptance` must include the doc impact:
         - which doc file(s) change
         - what sections to add/update
         - what examples/commands to include
     - Make beads **agent-ready** (self-contained):
       - `description`: Outcome / Why / Where (paths/systems) / Verification commands
       - `design`: key decisions + rationale, alternatives, constraints/invariants, footguns
       - `acceptance`: exact re-runnable checks (commands/steps), plus doc updates as explicit criteria
     - Use dependencies explicitly when needed:
       - `bd dep add <issue> <depends-on> -t blocks|related|parent-child|discovered-from --json`
     - After creation, print a compact index: epics → child beads, with blockers called out.
  6. **Hard stop**
     - After beads are created and summarized, stop. Do not begin implementation.
