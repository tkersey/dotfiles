# AGENT-PROFILES — Calibrating ergonomics per agent type

Different AI agents have different strengths, failure modes, and ergonomic needs. A surface that's perfectly intuitive for Claude Code may trip up a smaller agent or fail under Codex's stderr+exit2 contract.

This file profiles the major agent types currently in use and gives per-profile calibration adjustments.

When the user runs an audit, the audit is implicitly *for the agent profile they care most about*. Adjust the rubric accordingly — and document the choice in `phase0_scope_decision.md`.

---

## The major agent profiles

Drawing from the user's CASS connector list (which agent types have run sessions on this machine):

```
Connectors: codex, claude_code, gemini, clawdbot, vibe, opencode, amp, cline,
            aider, cursor, chatgpt, pi_agent, factory, openclaw, kimi, copilot,
            copilot_cli, qwen, crush
```

Group by characteristics:

### Frontier coding agents

Anthropic Claude Code, OpenAI Codex CLI (gpt-5.5+), Google Gemini CLI (3.x).

**Strengths.** Large context (200K+); strong tool use; persistent across sessions via memory/cass; multi-step planning.

**Failure modes.**
- Confidently misreading verbose `--help` output and choosing wrong flag
- Constructing `<tool>` invocations from prior tool experience (cargo-style → npm; clap-style → cobra)
- Insufficient verification of stderr classification (treats "warning" as fatal)

**Ergonomic emphasis.**
- Mega-commands matter most (round-trip × cost)
- `capabilities --json` + `robot-docs guide` are table stakes
- Error pedagogy must include `did you mean` for typo recovery
- Universal envelope is highly valued

### Mid-tier coding agents

aider, cursor (composer), opencode, vibe, cline.

**Strengths.** Good IDE integration; fast feedback loops.

**Failure modes.**
- Limited working memory → forgets tool's conventions mid-session
- Often re-invokes `--help` repeatedly (2-3× per task)
- Confused by NDJSON streams — wants single JSON document

**Ergonomic emphasis.**
- Help footer + AGENT/AUTOMATION section critical
- `--limit` defaults that fit context window (10-50 items)
- Avoid NDJSON for results that fit in single-doc

### Specialized agents

clawdbot, brennerbot, pi_agent, factory.

**Strengths.** Domain-specific skills; persistent state.

**Failure modes.**
- May not know modern conventions (`NO_COLOR`, `--robot`)
- Often run in long-lived sessions; depend on stable contracts

**Ergonomic emphasis.**
- `contract_version` semantics critical
- Stable handles (`project_key`, surface_id) over volatile IDs
- Resumable workflows

### Smaller / faster models

GPT-4o-mini, Claude Haiku, Gemini Flash, Kimi.

**Strengths.** Fast; cheap; good for narrow tasks.

**Failure modes.**
- Limited context → can't read long `--help` outputs
- Limited reasoning → can't infer tool intent from patterns
- Often skip reading `--help` and guess

**Ergonomic emphasis.**
- Make `--help` short (top 30 lines must convey core)
- Mega-commands hugely beneficial
- Default behaviors must be safe (errors > silent_fail; confirm > destructive)

### IDE-integrated assistants

GitHub Copilot, Cursor inline, Continue.

**Strengths.** Tight code-context awareness.

**Failure modes.**
- Run `--help` once, cache, then drift when tool updates
- Limited stderr visibility (often only stdout shown to model)
- Time-budget pressure limits tool exploration

**Ergonomic emphasis.**
- Stable `--help` text (low drift)
- `capabilities --json` doubly important (caches better than `--help`)
- Errors should produce stdout indicators when stderr is invisible

### Codex CLI (special case)

Codex CLI uses a unique exit-code contract: **exit 2 on stderr = denial**. This is different from the typical 0/1 convention and from Claude Code's stdout-JSON denial format.

**Implications:**
- Hook tools (dcg-style) MUST support both contracts
- The audit should test against both contracts when the tool is intended for cross-agent use
- Regression tests should pin both behaviors

---

## Per-profile rubric adjustments

When the audit is targeted at a specific agent profile, apply these dimension weight adjustments:

| Dimension | Frontier | Mid-tier | Specialized | Smaller | IDE-integrated |
|-----------|---------|----------|-------------|---------|----------------|
| 1 intuitiveness | 1.0× | 1.2× | 1.0× | **1.5×** | 1.2× |
| 2 ergonomics | 1.2× | 1.0× | 1.0× | **1.5×** | 1.0× |
| 3 ease_of_use | 1.0× | 1.2× | 0.8× | **1.5×** | **1.5×** |
| 4 parseability | 1.2× | 1.0× | 1.2× | 1.0× | 1.2× |
| 5 error_pedagogy | 1.2× | **1.5×** | 1.0× | **1.5×** | 1.0× |
| 6 intent_inference | 1.2× | 1.2× | 1.0× | **1.5×** | 1.0× |
| 7 safety | 1.0× | 1.0× | 1.2× | **1.5×** | 1.0× |
| 8 determinism | 1.0× | 1.0× | **1.5×** | 1.0× | 1.2× |
| 9 self_documentation | 1.2× | 1.2× | 1.0× | 1.0× | **1.5×** |
| 10 composability | 1.2× | 1.0× | 1.0× | 1.0× | 1.0× |
| 11 regression_resistance | 1.0× | 1.0× | **1.5×** | 1.0× | **1.5×** |

These weights enter `weighted_score` computation. Default profile (frontier) keeps all 1.0×. When the user targets a different profile, document in `phase0_scope_decision.md`:

```yaml
target_agent_profile: smaller   # default: frontier
rubric_weight_overrides:
  agent_intuitiveness: 1.5
  agent_ergonomics: 1.5
  agent_ease_of_use: 1.5
  error_pedagogy: 1.5
  intent_inference: 1.5
  safety_with_recovery: 1.5
```

---

## Per-profile evidence requirements

The general "score > 700 requires evidence" rule applies. But the *kind* of evidence varies per profile:

- **Frontier**: cite source file:line (they read source readily)
- **Mid-tier**: cite `--help` excerpts (limited source reading)
- **Specialized**: cite `capabilities --json` field (they re-read on resumed sessions)
- **Smaller**: cite the first 30 lines of `--help` (they don't read further)
- **IDE-integrated**: cite the documented contract (drift is the main risk)

---

## Per-profile canonical-task adjustments

The CANONICAL-TASK-LIBRARY.md tasks apply universally, but with per-profile weighting:

- **Frontier**: include all tasks; emphasize multi-step + JSON pipeline tasks
- **Mid-tier**: skip pagination tasks; emphasize first-try success
- **Smaller**: limit to 3-5 simplest tasks; emphasize "first command works"
- **IDE-integrated**: emphasize introspection tasks (`capabilities`, `whoami`)

The Phase 9 simulator should be told the profile so its task selection is appropriate.

---

## Profile-specific failure patterns from CASS

CASS-mined patterns observed in the user's session history:

### Claude Code

- Confidently runs commands with subtly wrong flag spellings (especially after compaction events when context is fresh)
- Reads `--help` of unfamiliar tools eagerly; gets confused by 200+-line outputs
- Strong on macros once discovered

### Codex CLI

- Stricter error handling (exit 2 means hard stop)
- Sometimes mis-classifies stderr warnings as fatal
- Strong on agent-driven workflows

### Gemini CLI

- Often re-runs the same command 2-3× to verify before proceeding
- Strong on multi-step planning
- Sometimes ignores stderr

### Smaller / IDE agents

- Skip `--help` and guess
- Get stuck on cryptic errors
- Don't know about `--robot` modes

These patterns inform Phase 4 priority weighting.

---

## Cross-profile compatibility

For tools intended to work across all profiles, design for the **lowest-common-denominator**:

- `--help` top 30 lines convey core (smaller-friendly)
- `capabilities --json` exists and is contract-pinned (specialized + IDE-friendly)
- Mega-commands exist (frontier + mid-tier benefit)
- Error pedagogy includes `did you mean` (smaller-helpful)
- Both Codex's stderr+exit2 AND Claude Code's stdout-JSON contracts work (cross-agent)

The audit's default profile is "frontier"; cross-profile audits use the union of constraints.

---

## When you don't know the agent profile

Default to "frontier." It's the broadest target. If the user later specifies a different profile, re-score with the adjusted weights in pass N+1.

If the tool is broadly deployed (used by many agents), audit for cross-profile compatibility rather than any single profile.

---

## Profile-specific exemplars

Some canonical exemplars are particularly suited to certain profiles:

| Profile | Exemplar |
|---------|----------|
| Frontier | `bv --robot-triage` (leverages strong reasoning) |
| Mid-tier | `cass capabilities --json` (cached easily) |
| Specialized | `am macro_start_session` (collapses identity for long-running agents) |
| Smaller | `dcg explain` (terse, high-value output) |
| IDE-integrated | `ubs <files>` (one-shot exit-code semantics) |

These are the patterns to emulate when designing for that profile.

---

## Updating profiles over time

Agent capabilities evolve quickly. This file should be re-validated quarterly:

- New agent types emerging? Add a profile.
- Existing agents shifted strengths? Update emphasis.
- New CASS patterns emerging? Add to the failure-mode lists.

The agent landscape in 2026 differs from 2024; the audit's per-profile calibration should track.

---

## Related

- `references/exemplars/CASS-FINDINGS.md` — observed agent-specific failure patterns
- `references/methodology/CASS-MINING-RECIPES-DEEP.md` — per-agent CASS query recipes
- `references/methodology/CLI-ARCHETYPES.md` — orthogonal axis (tool-shape × agent-profile)
- the `/multi-model-triangulation` skill (external) — inverse: using multi-agent verification for the audit ITSELF
