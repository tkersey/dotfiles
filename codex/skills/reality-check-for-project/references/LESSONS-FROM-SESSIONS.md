# Lessons From Real Sessions

Patterns extracted from 120+ CASS sessions across 12+ projects using Claude Code, Codex, and Gemini.

## Project-Level Pattern Map

| Project | Reality Check | Bridge Plan | Ambition | Refinement | Agent Types |
|---------|:---:|:---:|:---:|:---:|:---:|
| coding_agent_session_search | Full cycle | "close every gap" | -- | 4x repeated | CC |
| jeffreys-skills.md | Marketing audit + SSO reality | Gap-to-beads | -- | -- | CC |
| mcp_agent_mail_rust | Binary + stub audit | Bead generation | "MUCH BETTER" in AGENTS.md | -- | CC, Codex |
| frankensearch | CLI stub detection | -- | -- | -- | CC |
| frankensqlite | Performance benchmarks | Root cause plan | "1200 lines???" | -- | Codex |
| frankenjax | Missing features audit | -- | -- | -- | CC |
| asupersync | -- | -- | RUMINATE (all 3 agents) | -- | CC, Codex, Gemini |
| process_triage | -- | -- | TERRY TAO escalation | -- | Codex |
| frankentui | -- | -- | "decent start but" 3x | 5 rounds | Codex |
| wezterm_automata | -- | -- | -- | 5 rounds (11-15 beads each) | Codex |
| brenner_bot | -- | Bead generation | "more creative/clever" | -- | Codex |
| doodlestein_self_releaser | Mega-prompt (all phases combined) | Mega-prompt | Mega-prompt | Mega-prompt | Codex |

## Key Findings

### 1. The Bead Creation Prompt Is a Frozen Template

The exact text "OK so please take ALL of that and elaborate on it and use it to create a comprehensive and granular set of beads..." is copy-pasted verbatim across 5+ projects with zero variation. It was eventually codified in the idea-wizard skill. Do not modify it.

### 2. The Refinement Prompt Is Also Frozen

"Check over each bead super carefully..." appears identically across 20+ projects and dozens of sessions. The only historical variation is `bd` vs `br` (tool rename). The 10-item checklist within it never varies:
1. "are you sure it makes sense?"
2. "Is it optimal?"
3. "operate in plan space"
4. "DO NOT OVERSIMPLIFY THINGS!"
5. "DO NOT LOSE ANY FEATURES OR FUNCTIONALITY!"
6. "comprehensive unit tests and e2e test scripts"
7. "great, detailed logging"
8. "ONLY use the `br` cli tool"
9. "use the `bv` tool"
10. (implicit: "revise the beads" in-place)

### 3. Ambition Phrases Are Varied But Follow Patterns

Unlike the frozen templates, ambition phrases vary across sessions. But they follow predictable structures:
- **Opener:** Always begins with qualified acknowledgment ("decent start but...")
- **Escalation modifiers:** "MUCH MUCH MUCH", "WAY WAY WAY", "barely scratches the surface", "light years away from OPTIMAL"
- **Motivational closers:** "I believe in you", "Show me how brilliant you really are"
- **Directives:** "revise your existing plan document in-place", "think even harder", "Use ultrathink"

### 4. Ambition Was Embedded in AGENTS.md

For mcp_agent_mail_rust, the phrase "that's NOT enough. You have to do MUCH MUCH MUCH BETTER THAN THAT" was placed directly in AGENTS.md, making it fire on every session automatically. This is the most aggressive form of the pattern — baking ambition expectations into persistent project configuration.

### 5. Cross-Model Triangulation Happened Once

The RUMINATE prompt for asupersync was sent to Claude Code, Codex, AND Gemini — the only observed instance of the same ambition-round prompt being used across all three agent types for the same project. The Codex run produced 18,500+ characters of deep mathematical analysis.

### 6. The Transition Is Always Through Beads

In every observed session, the flow from ambition to implementation goes:
```
Ambition rounds → Bead creation prompt → Refinement rounds → Implementation
```
Never:
```
Ambition rounds → Direct implementation
```

### 7. Mega-Prompts Combine All Phases

For speed, all phases can be chained in a single message. Found in doodlestein_self_releaser:
```
[Research directive] + [Ambition "how can we make it better?"] +
[Bead creation prompt] + [Refinement checklist] + [br/bv tooling directive]
```

### 8. The idea-wizard Skill Formalizes This Flow

The idea-wizard skill at `~/.claude/skills/idea-wizard/SKILL.md` codifies the complete cycle:
- Phase 1: Ground in reality (read AGENTS.md + all beads)
- Phase 2-3: Generate ideas, winnow, expand (ambition)
- Phase 4: Check overlaps with open beads (reality check again)
- Phase 5: Operationalize into beads (bead creation template)
- Phase 6: Refine 4-5x (frozen refinement template)

## Anti-Patterns Visible in Sessions

| Anti-Pattern | Where Observed | Consequence |
|-------------|----------------|-------------|
| Same benchmark data pasted into 6+ Codex sessions | frankensqlite (Mar 24-26) | Problem persisted across sessions — reality check without follow-through |
| Issues "closed WITHOUT actually fixing the underlying bug" | GitHub audits across repos | False progress — bead closed but vision goal still unmet |
| Frustration response without structured gap analysis | frankensqlite performance rant | Emotional reaction bypasses the methodology |
| Skipping reality check, going straight to beads | Various early sessions | Beads created for wrong goals, missing actual gaps |

## Related Skills

- **idea-wizard** — Codifies the ambition → bead generation → refinement loop
- **mock-code-finder** — The stub/placeholder detection used in Phase 3 (code reality check)
- **beads-workflow** — Converting plans into beads with `br`
- **bv** — Graph-aware triage after bead generation
- **multi-model-triangulation** — Using multiple agents for the same ambition prompt
