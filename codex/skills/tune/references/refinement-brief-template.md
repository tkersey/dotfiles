# `$tune` Refinement Brief Template

Use this template before handing work to `$refine`. Keep transcript evidence sanitized unless the user explicitly requests safe raw excerpts.

```text
Target skill: <skill>

Mode:
- audit-only | proposal-only | apply-with-refine

Evidence sources:
- Source 1:
  - Kind: in-flight | history | provided | worktree | mixed
  - Locator: <current conversation | sessions root | session id | workdir | repo | file/artifact | validation output>
  - Scope: <current turn | current conversation | recent window | arbitrary history | explicit sessions | supplied evidence>
  - Window: <duration/date range/all/none>
  - Access method: <current context | $seq command | file read | tool output | user-provided text>
  - Privacy constraint: <summarize only | raw excerpts allowed if safe | no raw transcript>
  - Limitation: <what this source cannot prove>

Apply gate:
- pass | blocked: <reason>

Commit/push policy:
- For apply-with-refine, commit and push each validated atomic change unless the user explicitly disables publishing.

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
- Entry 1:
  - Source kind: <in-flight | history | provided | worktree>
  - Command, locator, or source: <seq command, session id, validation output, user feedback, file review>
  - Why this source was chosen: <reason>
  - What it proves: <claim supported by the source>
  - What it does not prove: <limits>
  - Evidence class: <class>
  - Confidence: high | medium | low
  - Scope/window: <scope>
  - Recurrence: <count/window or unknown>
  - Counterevidence: <counter-signal or none found>
  - Sanitization note: <what was omitted or generalized>
- Entry 2:
  - <repeat as needed>

Gap:
- Type: <activation | interpretation | workflow | tooling | resource | validation | metadata | boundary | source-scope>
- Diagnosis: <specific mismatch between intended and observed use>
- Severity: high | medium | low
- Risk if unchanged: <consequence>
- Risk of proposed change: <consequence>

Recommended `$refine` action:
- <smallest sufficient edit or upgrade>

Must not change:
- <core behavior, companion boundary, trigger scope, data-source assumptions, or validation expectation to preserve>

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

Publishing, apply-with-refine only:
- Atomic change boundary: <what this commit contains and why it is one coherent change>
- Scoped files to stage: <files justified by the brief>
- Unrelated worktree changes: <none | present and left unstaged | blocked because inseparable>
- Commit command: git commit -m "Tune <skill>: <short gap/fix summary>"
- Commit SHA: <sha | blocked/not run and why>
- Push command/result: <git push result | blocked/not run and why>
- Do not create PRs, merge branches, or clean up branches unless the user separately invokes that workflow.

Privacy / sanitization:
- No raw transcript text unless explicitly requested and safe.
- No secrets, credentials, sensitive paths, private user-identifying path fragments, or private personal details.
```
