# SELF-APPLICATION — Applying this skill to itself (and to other skills)

The skill is a tool used by AI agents. Therefore the skill itself has agent-facing surfaces. Therefore the skill can be audited.

This file gives the meta-recursive playbook: applying the agent-ergonomics audit to skills (this one, or any Claude Code skill, or any agent-facing toolkit).

This is **Level 6** of the Track A maturity ladder (per OPERATIONALIZING-EXPERTISE-TRACK-A.md): the methodology improves itself.

---

## The skill's surfaces (what's audit-able)

When an agent invokes a Claude Code skill, the surfaces it touches are:

1. **The skill's name** — must be recognized by triggers in the user's prompt
2. **The skill's `description` frontmatter** — read to decide if the skill applies
3. **SKILL.md body** — the agent reads this to drive the workflow
4. **Trigger phrases in SELF-TEST.md** — tested for activation
5. **Reference files (`references/**/*.md`)** — agent reads when needed
6. **Subagent prompts (`subagents/**/*.md`)** — the agent uses these to spawn helpers
7. **Helper scripts (`scripts/**`, `tools/**`)** — invoked by the agent
8. **Asset templates (`assets/**`)** — consumed during workflow

Each is an agent surface. Each can be scored on the 11 dimensions.

---

## Adapting the rubric for skills

Most dimensions translate directly:

| Dimension | Adapted for skills |
|-----------|---------------------|
| 1 intuitiveness | Does the skill activate when the user types a relevant phrase? Does the agent know what to do after reading SKILL.md? |
| 2 ergonomics | How many references must the agent load before it can take the first action? |
| 3 ease_of_use | Does SKILL.md have a quickref / jump-table? Are trigger phrases discoverable? |
| 4 parseability | Can phase outputs be parsed mechanically (JSON, JSONL)? |
| 5 error_pedagogy | When the agent goes off-rails, do the references redirect? |
| 6 intent_inference | Does the skill activate on related-but-not-exact phrasing? |
| 7 safety | Does the skill prevent dangerous actions per AGENTS.md? |
| 8 determinism | Can two agents running the skill produce comparable outputs? |
| 9 self_documentation | Does the skill self-describe? Reference index? Failure-mode tables? |
| 10 composability | Can the skill compose with other skills? With existing tooling? |
| 11 regression_resistance | Are there tests against drift in the skill's content? |

**A skill with strong agent ergonomics:**

- Frontmatter description leads with trigger phrases and durable artifact paths
- SKILL.md body has a TOC / jump-table at top
- Phase IO contracts are documented in JSONL
- Failure-mode tables are present
- Subagent prompts are calibrated and verbatim-usable
- Helper scripts have shebang + `set -euo pipefail` + clear `--help`

---

## Self-audit of the agent-ergonomics skill

### Phase 0

```yaml
target: <repo>/.claude/skills/agent-ergonomics-and-intuitiveness-maximization-for-cli-tools
archetype: claude-code-skill (a meta-archetype)
existing_surfaces:
  trigger_phrases: yes (SELF-TEST.md has 14)
  jump_table: yes (TOC at top of SKILL.md)
  phase_io_contracts: yes (IO-CONTRACTS.md)
  failure_mode_table: yes (TROUBLESHOOTING.md)
canonical_tasks:
  - "Audit a CLI for agent ergonomics"
  - "Re-score after applying changes"
  - "Run a fresh-agent simulation"
```

### Phase 1 self-inventory (representative)

| surface_id | kind | name |
|------------|------|------|
| `skill__main` | meta-verb | the skill itself (invoked by name) |
| `phase__1` | phase | Phase 1: Surface Inventory |
| `phase__2` | phase | Phase 2: Scoring |
| `subagent__scorer` | subagent | scorer.md |
| `script__validate_pass` | script | validate_pass.sh |
| `ref__operators` | ref | OPERATORS.md (33 cards) |
| `template__manifest` | asset | manifest-template.json |
| `trigger__audit_cli_for_ergonomics` | trigger | "Audit this CLI for agent ergonomics" |

Total: ~120+ surfaces (the skill is rich).

### Phase 2 highlights of self-audit

What an audit of THIS skill would find (Pass 1, after the most recent expansions):

**Strengths (above 800):**
- `agent_ease_of_use`: SKILL.md has TOC + Reference Index ✓
- `output_parseability`: IO-CONTRACTS.md pins every JSONL artifact ✓
- `self_documentation`: explicit Track A mapping; verbatim subagent prompts ✓
- `regression_resistance`: SELF-TEST.md validates structural integrity ✓
- `composability`: skill cleanly combines with /agent-mail, /beads-br, /beads-bv, /cass, /idea-wizard ✓
- `error_pedagogy`: TROUBLESHOOTING.md has comprehensive failure-mode table ✓

**Below-bar (would generate recs):**
- `agent_ergonomics`: SKILL.md is ~700 lines; agents must read a lot before first action (700 score)
- `agent_intuitiveness`: trigger phrases are good but the skill name is long (~80 chars); some agents truncate (650)
- `intent_inference`: the skill doesn't (yet) detect when a related-but-different intent (e.g. "audit my MCP server") should activate (550)
- `determinism`: rubric_version not always pinned; if a scorer drifts mid-pass, scores diverge (700)
- Mega-command for the skill itself: there isn't one. There's no `<skill> --robot-triage` analog. Could be: a single intake script that spawns Phase 0 → Phase 4 in `audit-only` mode by default (600)

### Phase 4 self-recs (what would land in pass 2)

- **R-001**: Add a "quick start" 30-line section at top of SKILL.md (lifts intuitiveness + ergonomics)
- **R-002**: Add intent-inference for nearby skills (e.g. "audit my MCP server" → suggest combining this skill + mcp-server-design)
- **R-003**: Pin `rubric_version` per pass via `manifest_update.sh`; emit warning if scorers use mismatched versions
- **R-004**: Add a `<skill>:run-audit` mega-action that combines Phase 0–4 in audit-only mode
- **R-005**: Add a one-page "cheat sheet" reference (CHEAT-SHEET.md) for agents who can't read 700 lines

These would be applied in pass 2 of the skill's own audit.

---

## Self-application as Phase 11

For users who want to keep the skill itself sharp:

```
Phase 11 — SELF-AUDIT
  - Apply this skill to its own directory
  - Score every surface
  - Generate recommendations
  - Apply top recs (carefully — don't break existing content!)
  - Re-score
```

This is run quarterly per the continuous-improvement schedule.

The constraint per AGENTS.md: **never delete content**. So self-application can ADD scaffolding (cheat sheets, quick-start sections, mega-action wrappers) but never remove existing references.

---

## Applying this skill to OTHER skills

The same audit applies to any Claude Code skill. The user has dozens of skills; many would benefit from agent-ergonomics audits:

### What to look for in any skill

1. **Frontmatter `description` field**: leads with triggers? mentions durable artifacts? under 400 chars?
2. **SKILL.md body**: has TOC? has jump-table? has failure-mode table? phase loop documented?
3. **Subagent prompts**: verbatim-usable? cite operators / quote bank? have output JSON shape?
4. **Helper scripts**: have shebangs? `set -euo pipefail`? executable? produce JSON optionally?
5. **Asset templates**: parseable (valid JSON / JSONL)?
6. **SELF-TEST.md**: trigger probes? smoke tests?

### Common skill anti-patterns

- Frontmatter description is prose without trigger phrases
- No TOC; agents must read 1000+ lines before knowing what's there
- Subagent prompts are vague ("review this and fix things") without IO contract
- Helper scripts produce text-only output (no `--json`)
- No regression tests for the skill's outputs

### Skill-specific recommendations

Depending on the skill's archetype (corpus-based, audit-based, generation-based, etc.), specific recs apply. See `CLI-ARCHETYPES.md` for analogous archetypes and adapt.

---

## Self-application to subagents in this skill

Each subagent in `subagents/*.md` is itself a small agent prompt. Audit them:

- Are inputs clearly specified?
- Is output schema documented?
- Does it cite the relevant rubric / operator / quote?
- Is the discipline section explicit (don't violate AGENTS.md)?
- Does it print a status line on completion (so the parent agent knows success)?

A subagent's `agent-ergonomics` is dimensional too. Phase 4 recs can land on subagents.

---

## Self-application to the canonical exemplars

The exemplar CLIs (dcg, bv, am, ubs, cass) have already been mined for patterns. But running this skill against THEM (per WORKED-EXAMPLES.md) yields concrete recs.

When the user wants to improve dcg/bv/am/ubs/cass, this skill is the way.

---

## Cross-skill self-application

For users with many related skills (the user has 100+), this skill can audit them as a **family** (per MULTI-TOOL-FAMILY-AUDIT.md):

- Cross-cut consistency: do all skills use same frontmatter pattern? Same Reference Index format?
- Naming consistency: are skill names verb-flavored or noun-flavored? Mixed?
- Versioning: do skills declare a contract version?
- Cross-references: do skills reference each other consistently?

The user's skill collection is itself a multi-tool family. This skill is one of many.

---

## The recursive audit

The skill recommends building agent-ergonomic CLIs. The skill itself should BE an agent-ergonomic CLI-skill. If running this skill on itself yields a clean Polish-Bar pass, the methodology is internally consistent. If not, that's a methodology gap to fix.

This is the truest test of the methodology. Track A skills that can't survive their own discipline aren't ready.

---

## How to invoke self-application

```bash
# In a Claude Code session:
"Audit the /agent-ergonomics-and-intuitiveness-maximization-for-cli-tools skill itself
 for agent ergonomics. Treat it as a tool. Use audit-only mode. Apply your own methodology."
```

The agent will:
1. Recognize the skill as the target
2. Use the skill's own methodology to audit
3. Produce a sibling audit workspace
4. Generate recs that improve the skill
5. (Optionally) apply them in a follow-up pass

---

## Avoiding circular reasoning

When auditing the skill against itself, beware:

- Don't use the skill's own anchors (CANONICAL-EXEMPLARS) to validate the skill's coverage; circular
- Use external references (Anthropic's MCP docs, the broader CLI literature, dcg/bv/am/ubs/cass directly)
- Multi-model triangulation (Phase 7) is especially valuable here — different models bring different external priors

---

## When self-application reveals methodology gaps

If self-application surfaces a finding that doesn't map to existing operators or rubric anchors, that's a **methodology gap**. Resolve by:

1. Adding a new operator card (rare)
2. Adding a quote to QUOTE-BANK.md
3. Refining a rubric anchor
4. Adding to ANTI-PATTERNS.md

The kernel is sticky; gaps usually map to operator-library or rubric-anchor refinement.

---

## Related

- `OPERATIONALIZING-EXPERTISE-TRACK-A.md` — Level 6 maturity context
- `references/exemplars/WORKED-EXAMPLES.md` — already includes a worked example of self-audit
- `MULTI-TOOL-FAMILY-AUDIT.md` — pattern for auditing multiple skills together
