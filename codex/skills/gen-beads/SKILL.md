---
name: gen-beads
description: Convert a project plan written in a Markdown file into a complete bd beads graph (tasks, subtasks, dependencies) using only bd for creation and edits, then review and optimize each bead. Use when asked to beadify a plan document (plan.md, plan-*.md, DESIGN/IMPLEMENTATION/ARCHITECTURE docs, or any planning markdown) or to generate bd tasks from a plan.
---

# Gen Beads

## Overview

Transform a markdown plan into a comprehensive bead graph with clear dependencies and rich, self-documenting comments, then review and refine every bead for optimal sequencing and user impact.

## Inputs

- Path to the plan markdown file
- Any scope boundaries, sequencing constraints, or priority guidance

## Workflow

1. Locate and read the plan file. Ask for the exact file path if multiple candidates exist.
2. Extract major workstreams, tasks, risks, milestones, and implied dependencies.
3. Generate beads using the "Generate Step Prompt" verbatim. Use only bd commands to create beads and add dependencies.
4. Evaluate every bead using the "Review Prompt" verbatim, revising beads via bd only.
5. Report what was created/updated and list any remaining ambiguities.

## Generate Step Prompt (use verbatim)

```
OK so please take ALL of that and elaborate on it more and then create a comprehensive and granular set of beads for all this with tasks, subtasks, and dependency structure overlaid, with detailed comments so that the whole thing is totally self-contained and self-documenting (including relevant background, reasoning/justification, considerations, etc.-- anything we'd want our "future self" to know about the goals and intentions and thought process and how it serves the over-arching goals of the project.)  Use only the `bd` tool to create and modify the beads and add the dependencies.
```

## Review Prompt (use verbatim)

```
Check over each bead super carefully-- are you sure it makes sense? Is it optimal? Could we change anything to make the system work better for users? If so, revise the beads. It's a lot easier and faster to operate in "plan space" before we start implementing these things!
```

## Guardrails

- Use only bd commands to create, modify, and wire dependencies; do not hand-edit bead files.
- Preserve plan intent. If the plan is inconsistent or missing critical details, ask targeted questions before deciding.
- Keep bead comments self-contained: background, rationale, success criteria, and sequencing considerations.
- Prefer small, composable beads with explicit dependencies over monolithic tasks.

## Output Expectations

- A coherent bead graph with tasks, subtasks, and dependencies.
- A short summary of what was created/changed and any open questions.
