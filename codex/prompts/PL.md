---
description: Clarify a request, then generate dependency-aware beads (no execution)
argument-hint: "<planning request...>"
---

# Plan (PL)
- **Input:** `$ARGUMENTS` (what you want planned). If empty or ambiguous, ask for clarification before doing anything.
- **Purpose:** Run a full Clarification Expert loop, then generate a parallelizable, documentation-rich bead plan in `bd`.
- **Non-goal:** Do **not** implement code. PL ends after creating beads.

- **Bead quality bar (memory + multi-agent)**
  - Prefer **multiple epics** (parallel workstreams) over one mega-epic.
  - Keep beads **atomic** and **parallelizable**:
    - one bead = one coherent deliverable that one agent can finish
    - minimize `blocks` chains; use `blocks` only for true prerequisites
  - **No dedicated docs beads**:
    - never create a docs-only bead
    - instead, embed doc work into every bead’s `description`/`design`/`acceptance` with exact file paths + content expectations
  - Beads must be **self-contained** for future-you:
    - `description`: Outcome / Why / Where / Verification
    - `design`: Decisions + rationale, alternatives, constraints/invariants, footguns/gotchas
    - `acceptance`: re-runnable checks + doc updates as explicit criteria

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
       - If `memory` is missing, create `.beads/templates/memory.yaml` with the contents below (and ensure `.gitignore` allows committing it):
         ```bash
         mkdir -p .beads/templates
         cat > .beads/templates/memory.yaml <<'YAML'
         name: memory
         description: |-
             ## Outcome (fill/update at close)
         
             [What changed? What is now true?]
         
             ## Why
         
             [Motivation / user story / constraints driving the change]
         
             ## Where (paths / systems)
         
             - [ ] Path(s):
             - [ ] Component(s):
         
             ## Verification (exact commands + results)
         
             - [ ] Command(s):
         
             ## Additional Context
         
             [Scratchpad while working. Distill into the bead before closing.]
         type: task
         priority: 2
         labels:
           - memory
         design: |-
             ## Decisions + rationale
         
             - [Decision]: [why]
         
             ## Alternatives considered
         
             - [Alt]: [why rejected]
         
             ## Constraints / invariants / gotchas
         
             - [Constraint]:
         
             ## Follow-ups
         
             - [ ] Created follow-up beads (if needed) and linked via discovered-from/blocks
         acceptance_criteria: |-
           - [ ] Outcome implemented
           - [ ] Verification commands recorded and pass
           - [ ] Bead fields are distilled (no placeholders)
           - [ ] Final "Closure Notes" saved in `notes` (per `AGENTS.md` / `~/.codex/AGENTS.md`)
         YAML
         ```
     - If the repo ignores `.beads/templates/*.yaml`, update `.gitignore` to allow committing the template (so the prompt works for other agents/clones).
     - Use the `memory` template for all beads:
       - `bd create --from-template memory ... --json`
     - If you cannot seed templates (e.g., read-only), fall back to template-free creation:
       - `bd create -t <type> -p <priority> "<title>" --description "<...>" --design "<...>" --acceptance "<...>" --json`
     - Draft the work graph (parallel workstreams → epics → subtasks); group by component/surface area to minimize merge conflicts.
     - Use hierarchical subtasks under epics when it helps coordination:
       - `bd create --parent <epic-id> -t task "..." --description "<...>" --design "<...>" --acceptance "<...>" --json`
     - Use dependencies explicitly when needed:
       - `bd dep add <issue> <depends-on> -t blocks|related|parent-child|discovered-from --json`
     - After creation, print a compact index: epics → child beads, with blockers called out.
  6. **Hard stop**
     - After beads are created and summarized, stop. Do not begin implementation.
