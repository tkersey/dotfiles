---
name: bmad
description: "BMad Method v6: workflow-driven agile delivery (track selection, PRD/spec, UX, architecture, epics/stories)."
---

# BMad Method (BMAD) v6

Source: https://github.com/bmad-code-org/BMAD-METHOD

## When to use
Use BMAD for structured, end-to-end delivery when the request is broad enough to need planning artifacts and a workflow.

Typical triggers:
- Track selection (Quick vs Method vs Enterprise).
- Planning artifacts (tech spec, PRD, UX, architecture).
- Turning requirements into epics/stories and sprint execution.
- “What should we do next?” workflow guidance.

## Core concepts

### Workflows, not ad-hoc prompts
BMAD v6 is organized around workflows run by specialized agents.
Common entry points:
- `workflow-init` to analyze the project and choose a track.
- `workflow-status` when unsure what’s next.

### Tracks (planning depth)
- Quick Flow: fast path; typically a tech spec; small changes/features.
- BMad Method: fuller planning; PRD + optional UX + architecture.
- Enterprise Method: extended planning; higher governance/compliance/testing needs.

### Lifecycle
- Analysis (optional): brainstorm/research/brief.
- Planning (required): PRD (Method/Enterprise) or tech spec (Quick).
- Solutioning (track-dependent): architecture, then epics/stories.
- Implementation (required): sprint plan → story → implement → review → repeat.

### Context rule
Prefer fresh chats per workflow to reduce context bleed.

## Lightweight playbook (in chat)
1. Establish context (greenfield/brownfield, outcomes/users, constraints).
2. Recommend a track and why.
3. Outline the minimum artifacts for that track.
4. Drive the next workflow step explicitly (`workflow-init` or `workflow-status`).

## Activation cues
- "BMAD" / "BMad Method" / "BMAD v6"
- "workflow-init" / "workflow-status" / "track selection"
- "PRD" / "tech spec" / "UX" / "architecture"
- "epics and stories" / "sprint planning" / "dev-story"
- "greenfield" / "brownfield"

## Non-goal
If the user only wants a narrow A-vs-B technology comparison (TCO/lock-in/etc.) without delivery workflow, use a dedicated decision framework instead.
