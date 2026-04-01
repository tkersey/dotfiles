# Phase-by-Phase Workflow Details

## Phase 1: Research Context

```bash
# Understand project state
cat AGENTS.md
br list --json           # Open beads
br list --status closed --json  # Closed beads
```

**Why:** Ground ideation in reality. Prevents duplicate ideas and ensures alignment with project goals.

**Checklist:**
- [ ] Read AGENTS.md completely
- [ ] Review all open beads
- [ ] Review closed beads (lessons learned)
- [ ] Understand current architecture

---

## Phase 2: Initial Ideation (30→5)

**The Prompt:**
```
Come up with your very best ideas for improving this project to make it more robust, reliable, performant, intuitive, user-friendly, ergonomic, useful, compelling, etc. while still being obviously accretive and pragmatic. Come up with 30 ideas and then really think through each idea carefully, how it would work, how users are likely to perceive it, how we would implement it, etc; then winnow that list down to your VERY best 5 ideas. Explain each of the 5 ideas in order from best to worst and give your full, detailed rationale and justification for how and why it would make the project obviously better and why you're confident of that assessment.
```

**Evaluation Criteria:**

| Criterion | Question |
|-----------|----------|
| Robust | Does it handle edge cases? |
| Reliable | Will it work consistently? |
| Performant | Is it fast enough? |
| Intuitive | Will users understand it? |
| User-friendly | Is it pleasant to use? |
| Ergonomic | Does it reduce friction? |
| Useful | Does it solve real problems? |
| Compelling | Will users want it? |
| Accretive | Does it add clear value? |
| Pragmatic | Is it realistic to build? |

**Why 30→5:** Generating many ideas then filtering prevents premature commitment to mediocre ideas. The winnowing forces quality.

---

## Phase 3: Expand to Top 15

**The Prompt:**
```
ok and your next best 10 and why
```

**Why:** The #6-15 ideas often have unique strengths that complement the top 5. Together they form a more complete improvement package.

**Variations:**
- `what were your next 10 best ideas and why` (more explicit)
- `ok and your next best 5 and why` (smaller expansion)

---

## Phase 4: Overlap Check & Merge

Before creating beads, compare against existing:

```bash
br list --json | jq '.[].title'
```

| Overlap Type | Action |
|--------------|--------|
| Direct duplicate | Skip, reference existing bead |
| Complementary | Merge into existing bead |
| Conflicts | Note explicitly, architectural decision needed |

**Why:** Prevents duplicate work, ensures ideas enhance rather than duplicate existing plans.

---

## Phase 5: Comprehensive Bead Creation

**The Prompt:**
```
OK so please take ALL of that and elaborate on it and use it to create a comprehensive and granular set of beads for all this with tasks, subtasks, and dependency structure overlaid, with detailed comments so that the whole thing is totally self-contained and self-documenting (including relevant background, reasoning/justification, considerations, etc.-- anything we'd want our "future self" to know about the goals and intentions and thought process and how it serves the overarching goals of the project.). The beads should be so detailed that we never need to consult back to the original markdown plan document. Remember to ONLY use the `br` tool to create and modify the beads and add the dependencies.
```

**Requirements Checklist:**
- [ ] Tasks broken into subtasks
- [ ] Dependencies via `br dep add`
- [ ] Self-documenting comments (why, not just what)
- [ ] No external context needed
- [ ] ONLY use `br` tool for operations

**Self-Documenting Comments Should Answer:**
1. **What** - What specifically needs to be done?
2. **Why** - Why is this important?
3. **How** - Key implementation approach
4. **Risks** - What could go wrong?
5. **Success criteria** - How do we know it's done?

---

## Phase 6: Iterative Refinement (4-5 Passes)

**The Prompt:**
```
Reread AGENTS.md so it's still fresh in your mind. Check over each bead super carefully-- are you sure it makes sense? Is it optimal? Could we change anything to make the system work better for users? If so, revise the beads. It's a lot easier and faster to operate in "plan space" before we start implementing these things! DO NOT OVERSIMPLIFY THINGS! DO NOT LOSE ANY FEATURES OR FUNCTIONALITY! Also make sure that as part of the beads we include comprehensive unit tests and e2e test scripts with great, detailed logging so we can be sure that everything is working perfectly after implementation. Make sure to ONLY use the `br` cli tool for all changes, and you can and should also use the `bv` tool to help diagnose potential problems with the beads.
```

**Critical Constraints:**
- **DO NOT OVERSIMPLIFY** - Resist the urge to collapse complexity
- **DO NOT LOSE FEATURES** - Every capability must be preserved
- **Include tests** - Unit tests AND e2e tests with detailed logging
- **Use bv for diagnosis** - Detect cycles, validate dependencies

**After Context Compaction:** Always re-read AGENTS.md to restore project rules to working memory.

**Why 4-5 Passes:**
- Pass 1: Structural issues, missing tasks
- Pass 2: Dependency sanity, cycle detection
- Pass 3: Test coverage gaps
- Pass 4: Comment quality, self-documentation
- Pass 5: Final optimization

---

## Validation Between Phases

```bash
# After Phase 5 and each Phase 6 pass:
bv --robot-insights | jq '.Cycles'      # Must be empty!
bv --robot-plan | jq '.plan.summary'    # Check dependency sanity
br ready --json | jq 'length'           # Verify actionable work exists
```
