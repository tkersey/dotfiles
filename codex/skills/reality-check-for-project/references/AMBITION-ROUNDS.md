# Ambition Rounds: Breaking Past Trained Incrementalism

## Why This Works

LLMs have learned incrementalism from their training data. Most human-written project plans, code reviews, and technical documents were authored by people managing expectations — sandbagging scope so they could hit safe targets. The models absorbed this conservatism as a default behavior.

Ambition rounds override this default by:

1. **First response** = the model's "safe" answer — incremental, expected, risk-averse
2. **First push** ("DIG DEEPER") = forces the model to explore beyond the obvious
3. **Second push** = the model starts drawing on deeper knowledge, making non-obvious connections
4. **Third push** = genuinely creative solutions emerge; the model often self-initiates another round
5. **Refinement rounds** = clean up the exuberance without losing the ambition

This is not prompt theater. It materially changes output quality by overriding trained risk aversion in the planning phase, where bold ideas cost nothing to explore.

## The Ambition Prompt Corpus (from 12+ real projects, 120+ CASS sessions)

### The "Decent Start But" Opener (ALWAYS Round 1)

The first escalation always begins with qualified acknowledgment. Real variations found:

```
That's a decent start but it barely scratches the surface and is light years away from being
OPTIMAL. Please try again and revise your existing plan document in-place to make it MUCH, MUCH,
MUCH better in EVERY WAY.
```

```
That's a decent start but not that creative or earth shattering, is it? I want that next level
terry tao stuff dude. Don't hold out on me.
```

```
That's a decent first start but it could be infinitely better and more comprehensive.
```

```
Come on dude, that barely scratches the surface. 1200 lines??? This needs to be more like 6,000+
lines to do these ideas justice!
```

```
That's NOT enough. You have to do MUCH MUCH MUCH BETTER THAN THAT.
```

### Round 2: Sustained Escalation + Motivation

```
That's a lot better than before but STILL is a far cry from being OPTIMAL. Please try yet again
and revise your existing plan document in-place to make it MUCH, MUCH, MUCH better in EVERY WAY.
I believe in you, you can do this!!! Show me how brilliant you really are.
```

```
I think you can go much deeper and be much smarter and more creative/clever about this. Please do
that and revise your initial document in-place. Use ultrathink.
```

### Round 3: Domain-Specific Depth Elicitation

```
Now, TRULY think even harder. Surely there is some math invented in the last 60 years that would
be relevant and helpful here? Super hard, esoteric math that would be ultra accretive and give a
ton of alpha for the specific problems we're trying to solve here, as efficiently as possible?
REALLY RUMINATE ON THIS!!! DIG DEEP!! STUFF THAT EVEN TERRY TAO WOULD HAVE TO CONCENTRATE SUPER
HARD ON!
```

With explicit skill references:
```
I need you to think bigger and bolder. Use $alien-artifact-coding and $extreme-software-optimization.
BE AMBITIOUS. Otherwise I won't do this.
```

### Context Injection Patterns (from CASS)

Project-specific context is injected BEFORE the standard escalation templates:
- **Mathematical depth:** "Surely there is some math..." (process_triage, asupersync, meta_skill)
- **Quantitative targets:** "1200 lines??? This needs to be more like 6,000+" (frankensqlite)
- **Skill references:** "Use $alien-artifact-coding and $extreme-software-optimization" (glibc_rust)
- **Preservation requirements:** "EVERY SINGLE ELEMENT... MUST BE PRESERVED **EXACTLY**" (mcp_agent_mail_rust)
- **Visual quality axis:** "WAY WAY WAY better and more visually appealing" (gemini visualizations)

### The Hype Persona

Works because it signals bold ideas are welcome, not penalized. Real variations:

```
I BELIEVE IN YOU MY FRIEND. LET US CHANGE THE WORLD TOGETHER. Let's really show the world what's
possible when we bring our absolute best!
```

```
I believe in you, you can do this!!! Show me how brilliant you really are.
```

```
I know for a fact that there are at least 87 serious bugs throughout this project impacting every
facet of its operation. The question is whether you can find and diagnose and fix all of them
autonomously. I believe in you.
```

### Cross-Model Triangulation

The same RUMINATE prompt was sent to Claude Code, Codex, AND Gemini for the asupersync project — the only observed case of true multi-model ambition rounds. The Codex run produced 18,500+ characters of deep mathematical analysis spanning Mazurkiewicz traces, region-based memory, game semantics, and session types.

### Embedding in AGENTS.md

For persistent projects, the "MUCH MUCH MUCH BETTER THAN THAT" phrase was embedded directly into mcp_agent_mail_rust's AGENTS.md, making it fire on EVERY session automatically — not just user-initiated reality checks.

## The Refinement Rounds

After the ambition rounds, refinement is critical. The model may have over-committed or generated ideas that don't survive scrutiny. Refinement catches this WITHOUT losing the ambition:

### The Canonical Refinement Prompt (frozen template — do NOT modify)

This exact prompt is copy-pasted verbatim across 20+ projects (frankentui, wezterm_automata, flywheel_gateway, repo_updater, doodlestein_self_releaser, meta_skill, etc.) and was eventually codified in the idea-wizard skill. Repeat it 4-5 times per session:

```
Check over each bead super carefully-- are you sure it makes sense? Is it optimal? Could we change
anything to make the system work better for users? If so, revise the beads. It's a lot easier and
faster to operate in "plan space" before we start implementing these things! DO NOT OVERSIMPLIFY
THINGS! DO NOT LOSE ANY FEATURES OR FUNCTIONALITY! Also make sure that as part of the beads we
include comprehensive unit tests and e2e test scripts with great, detailed logging so we can be
sure that everything is working perfectly after implementation. Make sure to ONLY use the `br` cli
tool for all changes, and you can and should also use the `bv` tool to help diagnose potential
problems with the beads.
```

### Why 4-5 Iterations (not 2-3)

Evidence from wezterm_automata session:
- Round 1 (line 76): First refinement pass → found gaps
- Round 2 (line 279): Second pass → more gaps
- Round 3 (line 370): Hit rate limit, /login, continued → still finding issues
- Round 4 (line 437): Getting cleaner
- Round 5 (line 502): Converged — no new issues found

Each round typically creates 11-15 new beads filling discovered gaps, runs bv diagnostics, and validates the dependency graph. **Stop only when a round finds nothing to change.**

### The "DO NOT OVERSIMPLIFY" Clause Is Critical

Without it, the model's risk-averse default resurfaces during refinement and it aggressively prunes the very ambition you just built up. This is the most important anti-regression mechanism in the entire workflow.

### Flywheel Gateway Variant (adds embeddedness requirement)

```
It's critical that EVERYTHING from the markdown plan be embedded into the beads so that we never
need to refer back to the markdown plan and we don't lose any important context or ideas or
insights into the new features planned and why we are making them.
```

## When to Use Ambition Rounds

**Always use for:**
- Bridge plans from reality checks (the whole point of this skill)
- Initial bead generation for major features
- Architecture decisions for novel/ambitious projects
- Any planning where the model's first answer feels "too safe"

**Skip for:**
- Bug fixes with obvious solutions
- Routine maintenance tasks
- Well-defined, narrow scope work
- Tasks where the model's first answer is already excellent

## The Complete Flow

See the authoritative pipeline diagram in SKILL.md. The key detail this reference adds is what happens **between** the phases:

- After Phase 1 (reality check) → agent produces honest assessment → user reacts (sometimes with frustration, which should be channeled into Phase 2, not pasted raw into multiple sessions)
- After Phase 2 (bridge plan) → agent produces initial plan → this is "usually too safe" → triggers ambition rounds
- After Ambition Round 1 → agent produces improved plan → user says "decent start but..." or "a lot better but STILL..."
- After Ambition Round 2-3 → agent produces bold plan → user pivots to Phase 3a (bead creation frozen template)
- After bead creation → user begins Phase 5 refinement loop × 4-5 → each round discovers 11-15 new gaps
- After refinement converges → `bv --robot-triage` validation → agents pick up work via `br ready`

**Canonical exemplar:** The coding_agent_session_search session `f8751479` is the only observed full 5-phase cycle in a single session: reality check → bridge plan → bead generation → 4x refinement → audit.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Refining TOO aggressively (pruning all the ambition) | Always include "DO NOT OVERSIMPLIFY" and "DO NOT LOSE FEATURES" |
| Only doing 1 ambition round | 2-3 rounds minimum; quality keeps improving |
| Skipping refinement entirely | Unbounded ambition without reality checking = fantasy |
| Using ambition rounds on simple tasks | Overkill for bug fixes; save for planning/architecture |
| Not referencing available capabilities | If the project has advanced techniques available, name them |
