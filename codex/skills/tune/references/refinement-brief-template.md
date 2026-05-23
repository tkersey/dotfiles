# `$tune` Refinement Brief Template

Use this template before handing work to `$refine`.

```text
Target skill: <skill>

Mode:
- audit-only | proposal-only | apply-with-refine

Tuning goal:
- <one-line goal>

Intended-use contract:
- Purpose: <summary>
- Trigger boundary: <summary>
- Anti-triggers / non-goals: <summary>
- Workflow expectation: <summary>
- Tool/resource expectation: <summary>
- Validation expectation: <summary>
- Companion-skill handoffs: <summary>

Observed usage:
- Evidence class: <class>
- Source: <seq command, validation output, or user feedback>
- Finding: <sanitized finding>
- Recurrence: <frequency or recurrence summary, if known>
- Counterevidence: <anything that weakens the finding>

Gap:
- Type: <activation | interpretation | workflow | tooling | resource | validation | metadata | boundary>
- Diagnosis: <specific mismatch between intended and observed use>

Recommended `$refine` action:
- <smallest sufficient edit or upgrade>

Files likely affected:
- codex/skills/<skill>/SKILL.md
- codex/skills/<skill>/agents/openai.yaml, if metadata changed
- codex/skills/<skill>/scripts/<name>, if deterministic tooling is justified
- codex/skills/<skill>/references/<name>.md, if reusable guidance is too long for SKILL.md
- codex/skills/<skill>/AUTO.md, if autonomous maintenance policy is affected

Success criteria:
- <criterion 1>
- <criterion 2>
- <criterion 3>

Validation:
- uv run --with pyyaml -- python3 codex/skills/.system/skill-creator/scripts/quick_validate.py codex/skills/<skill>
- <script sample command>, if scripts changed
- codex/skills/auto/scripts/auto-validate-corpus codex/skills, if shared assumptions or multiple skills changed

Privacy / sanitization:
- No raw transcript text unless explicitly requested and safe.
- No secrets, credentials, sensitive paths, or private personal details.
```
