# Bridge Plan Structure

## Purpose

The bridge plan transforms the gap analysis into a concrete, actionable plan for getting the project from its current state to full vision delivery. Every gap gets a specific resolution strategy.

## Plan Structure

### Per-Gap Resolution

For each gap identified in the analysis, produce:

```markdown
### [Gap #N]: [Goal Name] — [Status] → WORKING

**Current state:** [What exists now — be specific about files/functions]
**Target state:** [What "done" looks like — concrete and testable]
**Success criteria:**
- [ ] [Specific test that proves it works]
- [ ] [Performance benchmark that proves it's fast enough]
- [ ] [E2E scenario that proves it works in context]

**Implementation plan:**
1. [Specific change to specific file]
2. [Specific new code to write]
3. [Specific test to add]

**Dependencies:** [Other gaps that must be resolved first]
**Estimated complexity:** [S/M/L/XL]
**Vision goals served:** [Which numbered vision goals this closes]
```

### Prioritization

Order the bridge plan by **vision impact**, not by ease:

1. **Critical path first:** Gaps that block the core value proposition
2. **Proof gaps next:** Code exists but isn't proven — add tests
3. **Partial completions:** Finish what's started
4. **New implementations:** Build what doesn't exist yet
5. **Polish:** Edge cases, error handling, documentation

### The "Would Beads Close It?" Check

For each gap, explicitly answer: **If all existing open beads related to this goal were completed, would the gap close?**

- **Yes:** Just need to prioritize and execute existing beads
- **Partially:** Existing beads cover some aspects, need new beads for the rest
- **No:** No bead coverage at all — must create entirely new beads

## Bead Generation

When the project uses beads, the bridge plan should flow directly into bead creation:

```bash
# Create parent epic for a gap cluster
br create --title="[Vision Goal]: Bridge to full implementation" \
  --type=epic --priority=1 \
  --comment="$(cat <<'EOF'
Gap analysis found this vision goal at [STATUS].
Current state: [description]
Target state: [description]
This epic tracks all work needed to close this gap.
Source: Reality check performed on [date]
EOF
)"

# Create implementation bead
br create --title="Implement [specific feature]" \
  --type=task --priority=2 \
  --comment="$(cat <<'EOF'
## Context
[Why this is needed — which vision goal it serves]

## Current State
[What exists now in the code]

## Implementation Plan
[Detailed steps]

## Files to Change
- src/foo.rs: [what to change]
- src/bar.rs: [what to add]

## Success Criteria
- [ ] [specific test passes]
- [ ] [specific benchmark met]
EOF
)"

# Create companion test bead
br create --title="Add tests for [specific feature]" \
  --type=task --priority=2 \
  --comment="$(cat <<'EOF'
## What to Test
[Specific behaviors that must be verified]

## Test Types Needed
- Unit tests: [specific functions to test]
- Integration tests: [specific interactions to verify]
- E2E tests: [specific user-facing scenarios]

## Logging
Include detailed structured logging so failures are diagnosable.
EOF
)"

# Wire up dependencies
br dep add <test-bead-id> <impl-bead-id>  # tests depend on implementation
br dep add <impl-bead-id> <prerequisite-bead-id>  # if sequencing needed
```

### Bead Quality Standards

Every bead in the bridge plan must be:

1. **Self-contained** — Reading ONLY the bead's comment gives enough context to implement it without consulting any other document
2. **Self-documenting** — Includes the reasoning, the why, the connection to vision goals
3. **Testable** — Has explicit success criteria that can be verified
4. **Scoped** — One bead = one logical unit of work (not too big, not too small)
5. **Dependency-aware** — Dependencies on other beads are explicitly declared

### Plan-Space Iteration

Before implementing, iterate on the plan 4-5 times (evidence from wezterm_automata: 5 rounds before convergence, each finding 11-15 new gaps):

**Round 1: Completeness check**
- Does every vision goal have at least one gap resolution?
- Does every resolution have success criteria?
- Are dependencies correctly declared?

**Round 2: Optimality check**
- Could any resolutions be combined for efficiency?
- Are there smarter approaches than the obvious one?
- Would a different ordering unlock more parallelism?

**Round 3: Test coverage check**
- Does every implementation bead have a companion test bead?
- Do the tests actually prove the feature works end-to-end?
- Is there a "final integration" bead that tests everything together?

```bash
# Validate the bead graph after creation
bv --robot-triage | jq '.quick_ref'
bv --robot-insights | jq '.Cycles'  # Must be empty!
bv --robot-plan | jq '.plan.summary'
```

## Output Artifact

The bridge plan should be saveable as a standalone document:

```markdown
# Bridge Plan: [Project Name]

**Reality check date:** YYYY-MM-DD
**Gap count:** N critical, M major, P minor
**New beads created:** X
**Estimated work:** [rough scope]

## Critical Gaps (must fix for vision delivery)

### Gap #1: ...
[full resolution as above]

## Major Gaps (significantly degrades vision)

### Gap #2: ...

## Minor Gaps (polish)

### Gap #3: ...

## Dependency Graph

[Mermaid diagram or text description of bead ordering]

## Verification Plan

After all bridge work is complete, verify:
- [ ] [Each vision goal from the checklist, with how to test it]
```
