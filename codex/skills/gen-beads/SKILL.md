---
name: gen-beads
description: Generate beads in bd using the repo's swarm-ready rules; explicit invocation only.
---

# Gen-Beads

## Swarm rules (surgeon mode)
- One bead, one deliverable, one success state.
- Minimal incision: no refactor unless required by the outcome.
- Parallel by default; add `blocks` only for real prerequisites.
- Split anything that exceeds 1 day or touches >3 files.
- No docs-only beads; embed docs in the bead.
- Acceptance must be runnable: exact commands, paths, expected results.
- Cap epics at 7; split phases if needed.

## Workflow
1. Sanity-check `bd`: `bd info --json`.
2. Ensure the `memory` template exists.
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
         [Motivation / constraints]

         ## Where (paths / systems)
         - [ ] Path(s):
         - [ ] Component(s):

         ## Verification (exact commands + results)
         - [ ] Command(s):

         ## Additional context
         [Scratchpad while working; distill before closing.]
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
         - [ ] Bead fields distilled (no placeholders)
         - [ ] Final closure notes saved in `notes` (per `AGENTS.md` / `~/.codex/AGENTS.md`)
     YAML
     ```
   - If `.beads/templates/*.yaml` is ignored, update `.gitignore` so the template can be committed.
   - Re-run `bd template list --json` to confirm.
3. Draft the work graph.
   - Cap epics at 7.
   - Define children that can execute independently.
   - Mark only true prerequisites as `blocks`.
4. Create beads.
   - Prefer: `bd create --from-template memory ... --json`.
   - Fallback:
     - `bd create -t <type> -p <priority> "<title>" --description "…" --design "…" --acceptance "…" --json`
   - Use `-t epic` for epics; `-t task` (or `feature`/`bug`) for children.
   - Use `--parent <epic-id>` when coordination helps.
5. Wire deps: `bd dep add <issue> <depends-on> -t blocks|related|parent-child|discovered-from --json`.
6. Output a compact index: epics → children, plus which beads are ready.
7. Hard stop (no implementation).
