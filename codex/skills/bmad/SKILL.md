---
name: bmad
description: "BMad Method v6 for AI-driven agile delivery: choose a track (Quick/Method/Enterprise), run phases (analysis -> planning -> solutioning -> implementation), and produce core artifacts (PRD/tech spec, UX, architecture, epics/stories, sprint/story)."
---

# BMad Method (BMAD) v6

Based on the upstream BMAD v6 "BMad Method" project: https://github.com/bmad-code-org/BMAD-METHOD.

## When to use

Use BMAD for structured, end-to-end delivery with AI workflows, especially to:

- Build a project with a workflow-driven process (greenfield or brownfield)
- Choose a planning track by scope/rigor
- Produce planning artifacts (PRD/tech spec), UX, architecture
- Break requirements into epics/stories and run sprint/story cycles
- Get guidance on the next agent/workflow (e.g. `workflow-init`, `workflow-status`)

## Core concepts (v6)

### Workflows, not ad-hoc prompts
BMAD v6 is organized around *workflows* run by specialized agents. Typical entry points:

- `workflow-init` to analyze the project and choose a track
- `workflow-status` when unsure what's next

### Three planning tracks
Track choice reflects planning depth (not just story count):

- **Quick Flow**: fast path; typically tech spec only; small changes/features
- **BMad Method**: fuller planning; PRD + optional UX + architecture; products/platforms
- **Enterprise Method**: extended planning; higher governance/compliance/testing needs

### Four-phase lifecycle
- **Phase 1: Analysis (optional)**: brainstorm, research, brief
- **Phase 2: Planning (required)**: PRD (Method/Enterprise) or tech spec (Quick)
- **Phase 3: Solutioning (track-dependent)**: architecture, then epics/stories
- **Phase 4: Implementation (required)**: sprint plan, create story, implement, review, repeat

### Context management rule of thumb
BMAD v6 prefers *fresh chats per workflow* to reduce context bleed and hallucinations.

## Lightweight playbook (BMAD "in chat")

1. Establish context:
   - Greenfield vs brownfield
   - Goals/outcomes + target users
   - Constraints: timeline, team size/skills, compliance, scale, budget
2. Recommend a track (Quick vs Method vs Enterprise) and why.
3. Outline the minimum artifact set for that track (tech spec vs PRD/UX/architecture).
4. Drive the next workflow step explicitly (e.g., start `workflow-init` or ask for `workflow-status`).

## Activation keywords / trigger prompts

Use this skill when the user mentions or asks for:

- "BMAD", "BMad Method", "Build More, Architect Dreams", "BMAD v6", "BMad Core"
- "workflow-init", "workflow-status", "track selection", "Quick Flow", "Enterprise Method"
- "PRD", "tech spec", "UX design doc", "create architecture"
- "epics and stories", "story lifecycle", "sprint planning", "dev-story", "code-review"
- "greenfield", "brownfield", "existing codebase workflow"

## Non-goals / scope note

BMAD v6 is an agile delivery *methodology*. If the user only wants a narrow A vs B technology trade study (TCO/lock-in/etc.) without the broader delivery workflow, use a dedicated decision framework instead.
