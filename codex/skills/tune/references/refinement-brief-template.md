# `$tune` Refinement Brief Template

Use this template before handing work to `$refine`. Keep transcript evidence sanitized unless the user explicitly requests safe raw excerpts.

```text
Target skill: <skill>

Mode:
- audit-only | proposal-only | apply-with-refine

Apply gate:
- pass | blocked: <reason>

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
- Upgrade boundaries: <summary>

Observed usage:
- Summary: <sanitized finding>
- Recurrence: <frequency or recurrence summary, if known>
- Counterevidence: <anything that weakens the finding>

Evidence ledger:
- Source 1:
  - Command or source: <seq command, validation output, user feedback, or file review>
  - Why this source was chosen: <reason>
  - What it proves: <claim supported by the source>
  - What it does not prove: <limits>
  - Evidence class: <class>
  - Confidence: high | medium | low
  - Recurrence: <count/window or unknown>
  - Counterevidence: <counter-signal or none found>
  - Sanitization note: <what was omitted or generalized>
- Source 2:
  - <repeat as needed>

Gap:
- Type: <activation | interpretation | workflow | tooling | resource | validation | metadata | boundary>
- Diagnosis: <specific mismatch between intended and observed use>
- Severity: high | medium | low
- Risk if unchanged: <consequence>
- Risk of proposed change: <consequence>

Recommended `$refine` action:
- <smallest sufficient edit or upgrade>

Must not change:
- <core behavior, companion boundary, trigger scope, or validation expectation to preserve>

Files likely affected:
- codex/skills/<skill>/SKILL.md
- codex/skills/<skill>/agents/openai.yaml, if metadata changed
- codex/skills/<skill>/scripts/<name>, if deterministic tooling is justified
- codex/skills/<skill>/references/<name>.md, if reusable guidance is too long for SKILL.md
- codex/skills/<skill>/assets/<name>, if reusable static assets are justified

Success criteria:
- <criterion 1>
- <criterion 2>
- <criterion 3>

Validation:
- uv run --with pyyaml -- python3 codex/skills/.system/skill-creator/scripts/quick_validate.py codex/skills/<skill>
- <script sample command>, if scripts changed
- codex/skills/tune/scripts/validate-changed-skills, if shared assumptions or multiple skills changed
- If quick_validate.py is unavailable, report validation as blocked and do not claim a pass.

Privacy / sanitization:
- No raw transcript text unless explicitly requested and safe.
- No secrets, credentials, sensitive paths, private user-identifying path fragments, or private personal details.
```
