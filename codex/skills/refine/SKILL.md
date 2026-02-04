---
name: refine
description: Refine an existing Codex skill by applying $ms updates to SKILL.md, triggers, resources, and agents/openai.yaml, then validating with quick_validate. Use when asked to improve, iterate, fix, refactor, expand, or rename a skill; adjust triggers/metadata; add scripts/references/assets; regenerate UI metadata; or incorporate session-mining findings about skill quality.
---

# Refine

## Overview

Refine a target Codex skill by turning evidence into minimal, validated updates using $ms.

## Inputs

- Target skill name or path
- Improvement signals (user feedback, session mining notes, errors, missing steps)
- Constraints (minimal diff, required tooling, validation requirements)

## Example Prompts

- "Refine the docx skill to tighten triggers and regenerate agents/openai.yaml."
- "Add a small script to the pdf skill, then validate it."
- "Use session-mining notes to refine the gh skill's workflow."

## Workflow (Double Diamond)

### Discover

- Read the target skill's `SKILL.md`, `agents/openai.yaml` (if present), and any `scripts/`, `references/`, or `assets/`.
- Collect evidence from usage: confusion points, missing steps, bad triggers, or stale metadata.
- If no example prompts are provided, synthesize 2-3 realistic prompts that should trigger the skill.

### Define

- Write a one-line problem statement and 2-3 success criteria.
- Choose the smallest change set that addresses the evidence.
- Record explicit constraints (always run quick_validate, minimal diffs, required tooling).

### Develop

- List candidate updates: frontmatter description, workflow steps, new resources, or metadata regeneration.
- Prefer minimal-incision improvements; only add resources when they are repeatedly reused or required for determinism.

### Deliver

- Invoke $ms to implement changes in-place on the target skill.
- Keep SKILL.md frontmatter compliant for the target skill (name/description only unless a system skill allows more).
- Regenerate `agents/openai.yaml` if stale or missing.
- If adding scripts, run a representative sample to confirm behavior.

## Validation

Always run quick_validate on the target skill. Example command: `uv run --with pyyaml -- python3 codex/skills/.system/skill-creator/scripts/quick_validate.py codex/skills/<skill-name>`.

## Output Checklist

- Updated `SKILL.md` with accurate triggers and clear workflow
- Updated or regenerated `agents/openai.yaml` when needed
- New or modified resources (scripts/references/assets) if justified
- Validation signal from quick_validate (and script runs if added)
