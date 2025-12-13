---
description: Generate dependency-aware beads in bd (epics + tasks, agent-parallel)
argument-hint: "<context already in chat>"
---

# Beads (BD)
- **Purpose:** Convert the clarified context into a dependency-aware bead plan and create it in `bd`.
- **Non-goal:** Do **not** implement code. BD ends after creating beads and printing an index.

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

- **Process**
  1. **Sanity check bd target**
     - Run: `bd info --json` (ensure you’re writing to the intended repo/database)
  2. **Ensure the `memory` template exists (seed if missing)**
     - Run: `bd template list --json`
     - If `memory` is missing, create `.beads/templates/memory.yaml` with the contents below:
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
     - Re-run: `bd template list --json` and confirm `memory` exists.
  3. **Draft the work graph**
     - Identify parallel workstreams and define 3–7 epics (or more if the scope is large).
     - For each epic, define child beads that are independently executable.
     - Mark only true prerequisites as `blocks`.
  4. **Create beads in bd**
     - Use the `memory` template for every bead:
       - `bd create --from-template memory ... --json`
     - If you cannot seed templates (e.g., read-only), fall back to template-free creation:
       - `bd create -t <type> -p <priority> "<title>" --description "<...>" --design "<...>" --acceptance "<...>" --json`
     - Use `-t epic` for epics and `-t task` (or `feature`/`bug`) for children.
     - Prefer hierarchical subtasks under epics when it helps coordination:
       - `bd create --parent <epic-id> -t task "..." --description "<...>" --design "<...>" --acceptance "<...>" --json`
     - Do not leave placeholders; fill fields during creation or immediately `bd update` to distill them.
  5. **Wire dependencies**
     - Use: `bd dep add <issue> <depends-on> -t blocks|related|parent-child|discovered-from --json`
  6. **Output**
     - Print a compact index: epics → child beads, and list which beads are ready (no blockers).
  7. **Hard stop**
     - Do not start implementation.
