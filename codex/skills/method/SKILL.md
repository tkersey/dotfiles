---
name: method
description: Create a new skill that encodes a team’s software-development method and packages it as a .skill. Use only when the user explicitly says "$method".
---

# Method

## Overview
Turn a team’s values and build preferences into a new Codex skill, then package it as a .skill in the current directory.

## Workflow (step-by-step)

### 0) Gate on explicit invocation
Proceed only if the user explicitly says `$method`.

### 1) Elicit the method (ask, then wait)
Ask these as a numbered block and wait for answers:

- Project goals and non-goals
- Invariants / safety constraints
- Scope boundaries (no-go areas, forbidden changes)
- Architecture style (modules, layering, data flow)
- Data model / schema expectations
- Error handling + recovery posture
- Testing strategy + required signals
- Performance / latency constraints
- Security / compliance constraints
- API ergonomics and DX expectations
- Code review / quality gates
- Tooling constraints (linters, formatters, CI)

Also ask:
- Which existing skills should influence this method? (e.g., $sp, $trace). Align, adapt, or diverge?
- Who is the target user for this new skill (agent type, experience level, use cases)?
- What are 3–5 example prompts that should trigger the new skill, and 1–2 that should not?
- What degree of freedom should the new skill enforce (high-level vs step-by-step vs script-driven)?

### 2) Derive the new skill spec
From the answers, define:
- Skill name (lowercase, hyphenated)
- Frontmatter description with explicit trigger conditions
- Core doctrine/values (short, directive)
- Deliverable expectations (what the skill must output each run)
- Guardrails (what it must not do)

### 3) Plan reusable contents
Decide whether to add:
- `scripts/` for repeatable automation
- `references/` for detailed doctrine or policies
- `assets/` for templates or boilerplate

Keep SKILL.md lean; move depth into references only if it will be reused.

### 4) Initialize the skill
Create the new skill with the system script:

```bash
uv run codex/skills/.system/skill-creator/scripts/init_skill.py <skill-name> --path codex/skills
```

Create resource directories only if needed.

### 5) Write SKILL.md for the new skill
- Use imperative/infinitive form.
- Encode the method as a concrete workflow with clear guardrails.
- Include the explicit trigger rule in frontmatter description.
- Include the example triggers/non-triggers provided by the user.
- If influenced by $sp or $trace, reference them by name only; do not copy their contents.

Suggested structure:
- Overview
- Core doctrine / values
- Workflow (step-by-step)
- Guardrails
- Deliverable format

### 6) Package the skill
Package into the current directory and report the path:

```bash
uv run codex/skills/.system/skill-creator/scripts/package_skill.py codex/skills/<skill-name> .
```

Confirm the output file name (e.g., `./<skill-name>.skill`).

## Guardrails
- Do not proceed without explicit `$method` invocation.
- Do not create extra docs (README/CHANGELOG/etc.).
- Do not invent values; only encode what the user states.
- Keep changes minimal and reversible.

## Deliverable
- A packaged `.skill` in the current directory.
- A short summary of what the new skill encodes and how it should be triggered.
