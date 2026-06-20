---
name: ms
description: "Create or directly edit Codex skill packages: SKILL.md, triggers, agents/openai.yaml, scripts, references, assets, and optional decision instrumentation. Use for explicit skill creation or direct skill surgery now; classify the skill as decision/execution/evidence/orchestration/mixed, and scaffold SKDC-v1 only when stable decision rules need future `$seq`/`$tune` observability. Use `$refine` instead for usage-backed existing-skill refinement."
---

# ms

## Mission

Create lean, composable, valid skill packages.

For skills whose value lies in changing choices, make future decision evidence observable without turning every run into receipt ceremony.

## Hard constraints

- Make the smallest sufficient change.
- Do not add README/INSTALL/CHANGELOG files inside a skill package.
- Default frontmatter to `name` and `description`.
- `name` is hyphen-case, at most 64 characters, and matches the folder.
- `description` is the trigger surface and remains under 1024 characters.
- Keep `SKILL.md` under 500 lines; move deep detail into `references/`.
- Keep `agents/openai.yaml` aligned.
- Always run `quick_validate.py`.
- Record the `agents/openai.yaml` disposition.

## Skill type

Classify:

```text
decision
execution
evidence
orchestration
mixed
```

Examples:

- pattern-selection doctrine -> decision
- code implementer -> execution
- session miner -> evidence
- lifecycle controller -> orchestration
- review governor -> mixed

The classification guides observability. It does not belong in frontmatter unless the local convention supports it.

## Decision instrumentation gate

Create:

```text
references/decision-contract.yaml
```

only when all are true:

- the skill contains stable triggers and decision rules;
- future tuning would benefit from clause-level evidence;
- selected/rejected/no-action routes can be named;
- the contract is likely to survive wording changes.

Do not create a decision contract for a simple file transformer, narrow executor, or evidence fetcher unless it also makes consequential route decisions.

## SKDC-v1

A decision contract contains stable:

```text
trigger IDs
route IDs
clause IDs
required/prohibited routes
success/failure signals
required artifacts
```

Use:

```yaml
skill_decision_contract:
  contract_version: SKDC-v1
  skill:
    name:
    kind:
  triggers: []
  routes: []
  clauses: []
```

Validate:

```bash
python3 codex/skills/tune/tools/decision_contract_lint.py \
  codex/skills/<skill>/references/decision-contract.yaml
```

## Optional SDR-v1

A decision-oriented skill may specify an optional:

```text
skill_decision_receipt / SDR-v1
```

Use only when the skill makes a real route decision that later tuning cannot otherwise recover.

Do not emit receipts for ordinary prose, every checklist step, or simple tool execution.

## Create workflow

1. Search for an existing skill covering the intent.
2. Collect 2–3 realistic trigger prompts.
3. Write:
   - one-line problem statement;
   - success criteria;
   - non-trigger boundary.
4. Classify the skill type.
5. Decide whether reusable resources are justified.
6. Decide whether SKDC-v1 is justified.
7. Scaffold:
   ```bash
   uv run --with pyyaml -- python3 \
     codex/skills/.system/skill-creator/scripts/init_skill.py \
     <skill-name> --path codex/skills
   ```
8. Author procedural `SKILL.md`.
9. Create decision contract only if the gate passes.
10. Generate or update `agents/openai.yaml`.
11. Validate.
12. Remove redundant doctrine and examples.

## Update workflow

Use for direct user-authorized surgery without a `$tune` diagnosis.

1. Read the current package.
2. Preserve unrelated behavior.
3. If a decision contract exists:
   - preserve stable IDs;
   - update only affected clauses;
   - avoid silent contract drift.
4. If the skill is becoming decision-oriented, evaluate the instrumentation gate.
5. Update metadata.
6. Validate.

## Future tuneability check

Before completion, ask:

```text
Can future evidence tell whether this skill was present?
Can it tell whether a consequential decision changed?
Can it tell which rule was exercised?
Can it distinguish compliance from success?
```

It is acceptable for the answer to be “not applicable.”

Do not add instrumentation merely to make every answer “yes.”

## Seq feedback for `ms`

When refining `ms` itself, prefer:

```bash
seq skill-decision-audit \
  --skill ms \
  --mode tune-packet \
  --last 30d \
  --exclude-current \
  --format json
```

If unavailable, use narrow activation/message/validation evidence and report the CLI gap.

## Validation

```bash
uv run --with pyyaml -- python3 \
  codex/skills/.system/skill-creator/scripts/quick_validate.py \
  codex/skills/<skill>
```

If scripts were added, run representative samples.

If SKDC-v1 was added, run its linter.

## Final report

```text
Skill:
- Action:
- Type:
- Decision instrumentation: added | updated | not justified
- agents/openai.yaml:
- quick_validate:
- contract validation:
- Remaining uncertainty:
```
