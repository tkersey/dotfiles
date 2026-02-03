---
name: ms
description: Create, update, or refactor Codex skills in this repo, including SKILL.md, agents/openai.yaml, and any scripts/references/assets. Use when asked to design, scaffold, edit, validate, or improve skills, or when the user mentions skill creation, updates, triggers, or metadata.
---

# Meta Skill (ms)

## Overview

Create and update Codex skills with minimal diffs. Work directly in the skill folder (no external registry) and keep the skill lean.

## Hard constraints

- Minimal diff: change only what is needed to satisfy the new requirement.
- No extra docs: do not add README/INSTALL/CHANGELOG-style files.
- Frontmatter:
  - Default: only `name` and `description`.
  - Preserve existing allowed keys (e.g., `metadata`, `license`, `allowed-tools`) when updating system skills.
  - `name` must be hyphen-case (<=64 chars) and match the folder name.
  - `description` is the trigger surface: include "when to use" cues; no angle brackets; <=1024 chars.
- SKILL.md body:
  - Imperative voice.
  - Keep under 500 lines; spill deep details into `references/`.
  - Do not put trigger guidance in the body; put it in frontmatter `description`.
- `agents/openai.yaml` (if present/needed):
  - Prefer generating via `generate_openai_yaml.py`.
  - `short_description` must be 25-64 chars.
  - `default_prompt` must be one short sentence and mention `$skill-name`.
- Always run `quick_validate.py` before calling it done.
  - Recommended (no global installs):
    - `uv run --with pyyaml -- python3 codex/skills/.system/skill-creator/scripts/quick_validate.py <path/to/skill>`
  - Note: skill-creator scripts require PyYAML (`import yaml`).

## Workflow Decision Tree

- If a matching skill already exists: run Update Workflow.
- If no matching skill exists: run Create Workflow.
- If the name, location, or triggers are unclear: ask 1-3 targeted questions, then proceed.

## Create Workflow

1. De-duplicate: search for an existing skill that already covers the intent; prefer updating over creating a near-duplicate.
2. Discover and define: collect 2-3 concrete user prompts, then write:
   - Problem statement (1 line)
   - Success criteria (how we'll know it works)
3. Plan reusable assets: decide whether `scripts/`, `references/`, or `assets/` are required; create only what is necessary.
4. Initialize (scaffold):
   - `uv run --with pyyaml -- python3 codex/skills/.system/skill-creator/scripts/init_skill.py <skill-name> --path codex/skills`
   - Add `--resources scripts,references,assets` only when needed.
   - If you need UI metadata now, pass `--interface key=value` (repeatable).
5. Author `SKILL.md`:
   - Update frontmatter `description` to include concrete triggers (file types, tools, tasks, key phrases).
   - Keep the body procedural and composable (decision tree + steps + pointers into `references/`).
6. Sync UI metadata (optional but recommended for new skills):
   - Generate or regenerate: `uv run --with pyyaml -- python3 codex/skills/.system/skill-creator/scripts/generate_openai_yaml.py codex/skills/<skill-name> --interface key=value`
   - If the skill already had `default_prompt`, include it again in overrides (generator does not infer it).
   - For field constraints, read `codex/skills/.system/skill-creator/references/openai_yaml.md`.
7. Validate:
   - `uv run --with pyyaml -- python3 codex/skills/.system/skill-creator/scripts/quick_validate.py codex/skills/<skill-name>`
8. Iterate with the user: tighten triggers, remove redundancy, and promote repeatable code into `scripts/`.

## Update Workflow (In Place)

1. Locate the target skill folder in `codex/skills` (or `codex/skills/.system` for system skills).
2. Read the current `SKILL.md` and resources to identify the smallest set of required changes.
3. Edit in place:
   - Update frontmatter `description` if triggers changed.
   - Adjust workflows, tasks, or references with minimal diffs (no formatting churn).
   - Add or remove resource folders only when they create real reuse.
4. Sync UI metadata:
   - If `agents/openai.yaml` exists, keep it consistent with the skill and regenerate if stale.
   - If missing and UI metadata is desired, create it with `uv run --with pyyaml -- python3 codex/skills/.system/skill-creator/scripts/generate_openai_yaml.py <path/to/skill> --interface key=value`.
5. Validate with `uv run --with pyyaml -- python3 codex/skills/.system/skill-creator/scripts/quick_validate.py <path/to/skill>`.
6. Summarize changes and next steps.

## Trigger Examples

- "Create a skill to manage OpenAPI specs and generate SDKs."
- "Update skill X to include a new workflow and regenerate agents/openai.yaml."
- "Refactor this skill's SKILL.md and add references/ for schemas."
- "Refactor this skill's SKILL.md, move deep details into references/, and keep it under 500 lines."
