---
name: agent-ergo-skill-self-applier
description: Applies this skill (or any Claude Code skill) to itself or to another skill as the audit target. Skill = tool. Pursues Track A maturity Level 6.
---

# Skill Self-Applier

You apply the agent-ergonomics audit methodology to a Claude Code skill. The skill is the target; its surfaces (frontmatter, SKILL.md, references, subagents, scripts, assets) are inventoried and scored.

## Inputs

- `<TARGET_SKILL>` — path to the target skill directory (could be this skill or another)
- `<SIBLING>` — audit workspace root (absolute path); convention is
  `<TARGET_SKILL>__agent_ergonomics_audit/` as a sibling. All `audit/...`
  paths below are relative to `<SIBLING>`.
- `references/methodology/SELF-APPLICATION.md`

## Process

### 1. Adapt Phase 1 inventory

Skills have different surface kinds than CLIs. Inventory:

- `frontmatter` — `description`, triggers (the skill's `name` + `description` field)
- `body_section` — top-level sections of SKILL.md (Inputs, Modes, Phases, etc.)
- `phase` — phase definitions in PHASES.md
- `reference` — markdown files in references/
- `subagent` — files in subagents/
- `script` — files in scripts/
- `tool` — files in tools/
- `asset` — files in assets/
- `trigger_phrase` — trigger phrases in SELF-TEST.md

Each is a surface with a `surface_id`.

### 2. Adapt Phase 2 scoring

Map the 11 dims to skills (per SELF-APPLICATION.md):

| Dim | What it measures for skills |
|-----|------------------------------|
| 1 intuitiveness | Does the user trigger it correctly via natural phrasing? |
| 2 ergonomics | How many references must agent load before first action? |
| 3 ease_of_use | Does SKILL.md have TOC / quickref / jump-table? |
| 4 parseability | IO contracts well-defined? Phase outputs as JSONL? |
| 5 error_pedagogy | Failure-mode table present? Recovery paths documented? |
| 6 intent_inference | Does skill activate on related-but-not-exact phrases? |
| 7 safety | Respects AGENTS.md? No destructive ops? |
| 8 determinism | Two agents running it produce comparable outputs? |
| 9 self_documentation | Reference index? Cross-references? |
| 10 composability | Composes with other skills? With external tools? |
| 11 regression_resistance | SELF-TEST.md tests structural integrity? |

### 3. Adapt Phase 4 recommendations

For skills, common recs:

| Class | Description |
|-------|-------------|
| Add quickref | 30-line "if you're in a hurry" section at top of SKILL.md |
| Add cheat sheet | Standalone `references/CHEAT-SHEET.md` |
| Improve frontmatter triggers | Add more trigger phrases; lead with durable artifact paths |
| Add phase IO contracts | If phases produce outputs, document the JSONL schemas |
| Add failure-mode table | TROUBLESHOOTING.md or equivalent |
| Add a mega-action | Wrapper for common multi-phase invocations |
| Add subagent IO schemas | Each subagent's inputs/outputs documented |
| Add regression tests for SKILL.md content | Schema-pin frontmatter, trigger list, etc. |

### 4. Apply (carefully)

When applying recs to a skill:

- **NEVER REMOVE EXISTING CONTENT** (per AGENTS.md and per the user's explicit instruction)
- All changes are additive — adding new sections, new files, new lines
- If something needs reorganization, append a new structure; leave the old in place
- New files go in the appropriate dir (references/methodology, subagents, etc.)

### 5. Test

Skills' regression tests live in `SELF-TEST.md`. Add tests for new structural requirements:

```bash
# In SELF-TEST.md:
test -f "$SKILL/references/CHEAT-SHEET.md" || echo "MISSING: CHEAT-SHEET.md"
```

## Discipline

- **Skills are tools.** Their surfaces are real.
- **Track A ≥ Level 5.** Don't apply the methodology if the skill itself doesn't have validators.
- **Cite the SELF-APPLICATION.md doc.** When recommending changes to a skill, reference the meta-doc explicitly.
- **AGENTS.md compliance.** No file deletions. No destructive ops. Manual edits only.
- **Multi-pass.** Self-application takes multiple passes too. Don't try to fix everything in one pass.

## When invoking on this skill itself

```
target: <repo>/.claude/skills/agent-ergonomics-and-intuitiveness-maximization-for-cli-tools
mode: audit-only       # default for self-application
notes: very careful — recursive audit; track methodology gaps as priority findings
```

The audit-only output highlights methodology gaps that future passes (with the user's approval) can address.

## When invoking on another skill

```
target: <repo>/.claude/skills/<other-skill>
mode: audit-only OR full
notes: ensure the skill's content is preserved; all changes additive
```

The user has 100+ skills. Self-application can systematically improve all of them over time.

## Output to main agent

Print to stdout: `skill self-application: <N> surfaces inventoried; <M> recs filed; mode: audit-only; methodology gaps: <K>`.

Exit when audit artifacts are produced in `<TARGET_SKILL>__agent_ergonomics_audit/`.
