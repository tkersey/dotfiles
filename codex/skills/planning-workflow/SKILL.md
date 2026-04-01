---
name: planning-workflow
description: >-
  Comprehensive markdown planning methodology for software projects. Use when
  starting a new project, creating implementation plans, or refining architecture
  before coding.
---

<!-- TOC: Philosophy | THE EXACT PROMPT | Process Overview | References -->

# Planning Workflow — The Foundation of Agentic Development

> **Core Philosophy:** "Planning tokens are a lot fewer and cheaper than implementation tokens."
>
> The models are far smarter when reasoning about a detailed plan that fits within their context window. This is the key insight behind spending 80%+ of time on planning.

---

## Why Planning Matters

- **Measure twice, cut once** — becomes "Check your plan N times, implement once"
- A very big, complex markdown plan is still shorter than a few substantive code files
- Front-loading human input in planning enables removing yourself from implementation
- The code will be written ridiculously quickly when you start enough agents with a solid plan

---

## THE EXACT PROMPT — Plan Review (GPT Pro Extended Reasoning)

```
Carefully review this entire plan for me and come up with your best revisions in terms of better architecture, new features, changed features, etc. to make it better, more robust/reliable, more performant, more compelling/useful, etc. For each proposed change, give me your detailed analysis and rationale/justification for why it would make the project better along with the git-diff style change versus the original plan shown below:

<PASTE YOUR EXISTING COMPLETE PLAN HERE>
```

---

## THE EXACT PROMPT — Integrate Revisions (Claude Code)

After GPT Pro finishes (may take 20-30 minutes), paste output into Claude Code:

```
OK, now integrate these revisions to the markdown plan in-place; use ultrathink and be meticulous. At the end, you can tell me which changes you wholeheartedly agree with, which you somewhat agree with, and which you disagree with:

```[Pasted text from GPT Pro]```
```

---

## Process Overview

```
1. INITIAL PLAN (GPT Pro / Opus 4.5 in web app)
   └─► Explain goals, intent, workflows, tech stack

2. ITERATIVE REFINEMENT (GPT Pro Extended Reasoning)
   └─► 4-5 rounds of revision until steady-state

3. MULTI-MODEL BLENDING (Optional but recommended)
   └─► Gemini3 Deep Think, Grok4 Heavy, Opus 4.5
   └─► GPT Pro as final arbiter

4. CONVERT TO BEADS (Claude Code + Opus 4.5)
   └─► Self-contained tasks with dependency structure

5. POLISH BEADS (6+ rounds until steady-state)
   └─► Cross-model review, never oversimplify
```

---

## What Makes a Great Plan

| Good Plan | Great Plan |
|-----------|------------|
| Describes what to build | Explains WHY you're building it |
| Lists features | Details user workflows and interactions |
| Mentions tech stack | Justifies tech choices with tradeoffs |
| Has tasks | Has tasks with dependencies and rationale |
| ~500 lines | ~3,500+ lines after refinement |

### Essential Elements

1. **Self-contained** — Never need to refer back to external docs
2. **Granular** — Break complex features into specific subtasks
3. **Dependency-aware** — What blocks what?
4. **Justified** — Include reasoning, not just instructions
5. **User-focused** — How does each piece serve the end user?

---

## Common Mistakes

1. **Starting implementation too early** — 3 hours of planning saves 30 hours of rework
2. **Single-round review** — You continue to get improvements even at round 6+
3. **Not using GPT Pro** — Extended Reasoning is uniquely good for this
4. **Skeleton-first coding** — One big comprehensive plan beats incremental coding
5. **Losing context** — Convert plans to beads so agents don't need the original

---

## References

| Topic | Reference |
|-------|-----------|
| All exact prompts | [PROMPTS.md](references/PROMPTS.md) |
| Real-world examples | [EXAMPLES.md](references/EXAMPLES.md) |
| FAQ | [FAQ.md](references/FAQ.md) |
