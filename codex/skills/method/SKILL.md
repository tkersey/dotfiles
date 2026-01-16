---
name: method
description: Create a new skill that encodes a team’s bead-implementation method and packages it as a .skill. Use only when the user explicitly says "$method".
---

# Method

## Overview
Turn a team’s bead-implementation method (defaults + per-bead intake questions) into a new Codex skill, then package it as a .skill in the current directory.

## Workflow (step-by-step)

### 0) Gate on explicit invocation
Proceed only if the user explicitly says `$method`.

### 1) Elicit the method (discover, then ask)
Before asking the user anything, try to discover what you can from the repo:
- Read any `AGENTS.md` in scope.
- Skim `README*`, `CONTRIBUTING*`, and the nearest "how to test" docs.
- Identify the toolchain + entrypoints: `Makefile`, `justfile`, `Taskfile.yml`, `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, CI config, etc.
- Write down a short **Snapshot** so you don’t re-ask discoverable facts.

Then ask the remaining judgment calls as a numbered block and wait for answers.

Use this exact heading:
```
METHOD: HUMAN INPUT REQUIRED
1. ...
```

Ask these in order.

Answer format expectations:
- Reply with numbered answers.
- For commands, give copy-pastable commands.
- If you don’t know, say "unknown" (don’t guess).

Inference rule:
- Do not ask the user to pick “safety vs speed”; infer default posture from required signals + autonomy + invariants. Ask explicitly only if still unclear.

Core questions (ask these first; always):
1. **Goal**: What does “properly implement a bead” mean for your team? (1–3 sentences)
2. **Skill boundary**: Default: implement one bead end-to-end (including git/PR). If you want protocol-only (no git/PR unless explicitly requested), say so.
3. **Triggering + non-triggering**: Give 3–5 example prompts that SHOULD trigger the new skill, and 1–2 that should NOT.
4. **Target user**: Who is the target user (agent type, experience level, typical use cases)?
5. **Runtime intake (hybrid)**: At the start of *each bead*, what questions should the skill ask before editing code? (Aim for 5–10. Include feature/refactor/bugfix-specific ones if different.)
6. **Source of truth**: Where do requirements live for a bead? (beads/issue tracker, spec doc paths, tests, design docs)
7. **Definition of done**: What must be true before the bead is done? Include your git policy (commit/push/PR), docs requirements, and any CI gates.
8. **Proof commands**: Provide exact commands (or canonical entrypoints) for each category:
   - formatter
   - lint/typecheck
   - build/package
   - fastest credible test signal
   - full test suite (if different)
9. **Autonomy gate**: When may the agent proceed without asking vs must stop? Give 2 concrete examples of each.
10. **Feature beads**: What is the preferred implementation strategy? (e.g., smallest vertical slice, UI expectations, backwards compat)
11. **Refactor beads**: What constraints apply? (semantics-preserving, characterization tests required, API stability)
12. **Bugfix beads**: What is the preferred debugging strategy? (repro-first? characterization tests? instrumentation?) Any rollback/release posture?

Optional deepeners (ask only if still ambiguous):
13. **Scope / no-go**: What is explicitly out of scope? (no-go directories/files; forbidden refactors; forbidden dependency changes)
14. **Invariants**: What invariants must remain true across feature/refactor work? (compat guarantees, data integrity rules, public API stability)
15. **Architecture boundaries**: Where should changes live, and what dependencies/layers are forbidden?
16. **Data model** (if applicable): Where is schema defined? Are migrations allowed? What’s the compatibility policy?
17. **Error handling posture**: Fail-fast vs recover; logging/telemetry requirements; user-visible behavior.
18. **Performance / latency** (if applicable): Any budgets, SLOs, or known hotspots to avoid?
19. **Security / compliance** (if applicable): secrets/PII rules, authz expectations, audit logging, approved deps.
20. **Tooling constraints**: must-use tools (e.g., `uv`, `jj`, `gh`), formatters/linters, CI gates, and any banned/destructive commands.
21. **Influences**: Which existing skills should influence this method? (e.g., `$sp`, `$fix`, `$close-the-loop`, `$commit`, `$beads`) For each: align / adapt / diverge.
22. **Output format**: What should the skill output every run? (patch summary, file list, commands run, proof block, PR link, etc.)
23. **Bead ledger** (optional; ask only if the repo uses one): If the repo uses `bd` (beads) or another work ledger, what updates are required during/after the run? (status updates, comments, close reason, linking discovered work)

### 2) Derive the new skill spec
From the answers, define:
- Skill name (lowercase, hyphenated)
- Frontmatter description with explicit trigger conditions
- Core doctrine/values (short, directive)
- Runtime intake questions (what the skill asks before editing)
- Autonomy gate (when it may proceed vs must ask)
- Deliverable expectations (what the skill must output each run)
- Guardrails (what it must not do)

### 2.5) Confirm the spec (don’t skip)
Before creating files, present a 1-page summary:
- Proposed skill name + frontmatter description
- Workflow outline (major sections)
- Guardrails + deliverable format
- Planned `scripts/` / `references/` / `assets/` (if any)

Ask for an explicit “go ahead” before running `init_skill.py`.

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
- Keep SKILL.md frontmatter valid (`name` hyphen-case <= 64 chars; `description` <= 1024 chars; no `<` or `>` in description).
- Keep changes minimal and reversible.

## Deliverable
- A packaged `.skill` in the current directory.
- A short summary of what the new skill encodes and how it should be triggered.
