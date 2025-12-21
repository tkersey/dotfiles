---
name: gen-beads
description: Generate beads in bd using the repo's swarm-ready rules; explicit invocation only.
---

# Gen-Beads

## Swarm-ready rules (surgeon mode)
- One bead, one deliverable, one success state.
- Smallest incision: no refactor unless required by outcome.
- Parallel by default; add `blocks` only for true prerequisites.
- Atomic scope: one agent, one sitting; split if it exceeds 1 day or >3 files.
- Embed docs in each bead; no docs-only beads.
- Acceptance is runnable: exact commands, file paths, expected results.
- Epic cap: 7 max; split phases if more are needed.

## Workflow
1) Sanity check target
   - `bd info --json`
2) Ensure `memory` template exists (seed if missing)
   - `bd template list --json`
   - If missing, create `.beads/templates/memory.yaml`:
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
   - If `.beads/templates/*.yaml` is ignored, update `.gitignore` so the template can be committed.
   - Re-run `bd template list --json` to confirm.
3) Draft the work graph
   - Cap epics at 7 for parallel workstreams; split phases if more are needed.
   - Define child beads that can be executed independently.
   - Mark only true prerequisites as `blocks`.
4) Create beads
   - Prefer `bd create --from-template memory ... --json`.
   - If you cannot seed templates, fall back to template-free creation:
     - `bd create -t <type> -p <priority> "<title>" --description "<...>" --design "<...>" --acceptance "<...>" --json`
   - Use `-t epic` for epics and `-t task` (or `feature`/`bug`) for children.
   - Prefer hierarchical subtasks when coordination helps:
     - `bd create --parent <epic-id> -t task "..." --description "<...>" --design "<...>" --acceptance "<...>" --json`
   - Do not leave placeholders; distill fields immediately if needed.
5) Wire dependencies
   - `bd dep add <issue> <depends-on> -t blocks|related|parent-child|discovered-from --json`
6) Output
   - Print a compact index: epics → children, plus which beads are ready.
7) Hard stop
   - Do not start implementation.
