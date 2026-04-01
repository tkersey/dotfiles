---
name: idea-wizard
description: >-
  Generate and operationalize improvement ideas for projects. Use when brainstorming
  features, planning improvements, creating beads from ideas, or "what should we build next".
---

# idea-wizard

> Generate many → winnow ruthlessly → operationalize into self-documenting beads.

## Quick Start

```
1. Read AGENTS.md + all beads       → Ground in reality
2. Phase 2 prompt (30→5)            → Generate & winnow
3. Phase 3 prompt (next 10)         → Expand to 15
4. Check overlaps with open beads   → Merge, don't duplicate
5. Phase 5 prompt                   → Create beads
6. Phase 6 prompt (repeat 4-5x)     → Refine in "plan space"
```

---

## THE EXACT PROMPTS

**Phase 2 — Generate 30→5:**
```
Come up with your very best ideas for improving this project to make it more robust, reliable, performant, intuitive, user-friendly, ergonomic, useful, compelling, etc. while still being obviously accretive and pragmatic. Come up with 30 ideas and then really think through each idea carefully, how it would work, how users are likely to perceive it, how we would implement it, etc; then winnow that list down to your VERY best 5 ideas. Explain each of the 5 ideas in order from best to worst and give your full, detailed rationale and justification for how and why it would make the project obviously better and why you're confident of that assessment.
```

**Phase 3 — Expand:** `ok and your next best 10 and why`

**Phase 5 — Create Beads:**
```
OK so please take ALL of that and elaborate on it and use it to create a comprehensive and granular set of beads for all this with tasks, subtasks, and dependency structure overlaid, with detailed comments so that the whole thing is totally self-contained and self-documenting (including relevant background, reasoning/justification, considerations, etc.-- anything we'd want our "future self" to know about the goals and intentions and thought process and how it serves the overarching goals of the project.). The beads should be so detailed that we never need to consult back to the original markdown plan document. Remember to ONLY use the `br` tool to create and modify the beads and add the dependencies.
```

**Phase 6 — Refine (repeat 4-5x):**
```
Reread AGENTS.md so it's still fresh in your mind. Check over each bead super carefully-- are you sure it makes sense? Is it optimal? Could we change anything to make the system work better for users? If so, revise the beads. It's a lot easier and faster to operate in "plan space" before we start implementing these things! DO NOT OVERSIMPLIFY THINGS! DO NOT LOSE ANY FEATURES OR FUNCTIONALITY! Also make sure that as part of the beads we include comprehensive unit tests and e2e test scripts with great, detailed logging so we can be sure that everything is working perfectly after implementation. Make sure to ONLY use the `br` cli tool for all changes, and you can and should also use the `bv` tool to help diagnose potential problems with the beads.
```

---

## Commands

```bash
br list --json && br list --status closed --json   # Phase 1: Research
br list --json | jq '.[].title'                    # Phase 4: Check overlaps
br create "Title" -p 1 -t task --body "..."        # Phase 5: Create
br dep add <child> <parent>                        # Phase 5: Dependencies
bv --robot-insights | jq '.Cycles'                 # Validate: Must be empty!
```

---

## Anti-Patterns

| Don't | Do |
|-------|-----|
| Skip Phase 1 | Read beads first — prevents duplicates |
| Stop at 5 ideas | Expand to 15 — #6-15 often complementary |
| Single-pass beads | 4-5 passes — first draft never optimal |
| Omit tests | Explicit test tasks with logging |
| Bare `bv` | `--robot-*` flags — bare bv blocks TUI |
| Oversimplify | Resist — complexity exists for reasons |

**Phase 6 constraints:** DO NOT OVERSIMPLIFY. DO NOT LOSE FEATURES. After compaction → re-read AGENTS.md.

---

## References

| Topic | File |
|-------|------|
| Phase details | [PHASES.md](references/PHASES.md) |
| Bead patterns | [BEADS.md](references/BEADS.md) |
| Examples | [EXAMPLES.md](references/EXAMPLES.md) |
| Evaluation rubric | [RUBRIC.md](references/RUBRIC.md) |

Ideas evaluated on: robust, reliable, performant, intuitive, user-friendly, ergonomic, useful, compelling, accretive, pragmatic — see [RUBRIC.md](references/RUBRIC.md)
