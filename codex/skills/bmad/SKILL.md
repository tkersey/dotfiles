---
name: bmad
description: "BMad Method (Build More, Architect Dreams) v6. Use for AI-driven agile delivery: choosing a planning track (Quick Flow vs BMad Method vs Enterprise), running workflow-based phases (analysis -> planning -> solutioning -> implementation), and producing core artifacts (PRD/tech-spec, UX design, architecture, epics/stories, sprint/story execution)."
---

# BMad Method (BMAD) v6

This skill is based on the upstream BMAD v6 “BMad Method” project: https://github.com/bmad-code-org/BMAD-METHOD.

## When to use

Use BMAD when the user wants a structured, end-to-end methodology for building software with AI agents/workflows, especially when they ask for any of:

- A workflow-based process for building a project (greenfield or brownfield)
- Choosing a planning “track” based on scope/rigor
- Producing planning artifacts (PRD or tech spec), UX design, architecture
- Breaking requirements into epics/stories and running a sprint/story lifecycle
- Guidance on which agent/workflow to run next (e.g. `workflow-init`, `workflow-status`)

## Core concepts (v6)

### Workflows, not ad-hoc prompts
BMAD v6 is organized around *workflows* run by specialized agents. A typical entry point is:

- `workflow-init` to analyze the project and choose a track
- `workflow-status` when unsure what’s next

### Three planning tracks
Track choice is about planning needs (not just “story count”):

- **Quick Flow**: fast path; typically tech-spec only; small changes/features
- **BMad Method**: fuller planning; PRD + (optional UX) + architecture; products/platforms
- **Enterprise Method**: extended planning; higher governance/compliance/testing needs

### Four-phase lifecycle
- **Phase 1: Analysis (optional)**: brainstorm, research, brief
- **Phase 2: Planning (required)**: PRD (Method/Enterprise) or tech-spec (Quick)
- **Phase 3: Solutioning (track-dependent)**: architecture; then create epics/stories
- **Phase 4: Implementation (required)**: sprint planning; create story; implement; review; repeat

### Context management rule of thumb
BMAD v6 strongly prefers *fresh chats per workflow* to reduce context bleed/hallucinations.

## Lightweight playbook (how to run BMAD “in chat”)

1. Establish context:
   - Greenfield vs brownfield
   - Goal/outcomes + target users
   - Constraints: timeline, team size/skills, compliance, scale, budget
2. Recommend a track (Quick vs Method vs Enterprise) and explain why.
3. Outline the minimum artifact set for that track (tech-spec vs PRD/UX/architecture).
4. Drive the next workflow step explicitly (e.g. “start with `workflow-init` / ask for `workflow-status`”).

## Activation keywords / trigger prompts

Use this skill when the user mentions or asks for:

- “BMAD”, “BMad Method”, “Build More, Architect Dreams”, “BMAD v6”, “BMad Core”
- “workflow-init”, “workflow-status”, “track selection”, “Quick Flow”, “Enterprise Method”
- “PRD”, “tech spec”, “UX design doc”, “create architecture”
- “epics and stories”, “story lifecycle”, “sprint planning”, “dev-story”, “code-review”
- “greenfield”, “brownfield”, “existing codebase workflow”

## Non-goals / scope note

BMAD v6 is an agile delivery *methodology*. If the user is strictly asking for a narrow “A vs B technology choice” trade study (TCO/lock-in/etc.) without wanting the broader delivery workflow, consider using a dedicated tech-decision framework instead of BMAD.
