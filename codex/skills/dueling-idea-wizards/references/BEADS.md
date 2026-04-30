# Bead Creation Pipeline

How to turn duel winners into actionable, self-documenting beads.

## When to Create Beads

| Verdict | Action |
|---------|--------|
| CONSENSUS WIN (700+ all agents) | Create bead immediately |
| STRONG (avg 700+, none below 500) | Create bead with normal priority |
| SPLIT (one agent 800+, another hostile) | Create bead at P3, note disagreement |
| CONTESTED (avg 400-700, large gap) | Parking lot -- revisit later |
| CONSENSUS KILL (all below 400) | Do not create bead |

## Bead Structure for Duel Winners

Every bead created from a duel must include the adversarial context. This is what makes duel-derived beads qualitatively different from single-agent beads.

```bash
br create "Epic: [IDEA_TITLE]" -p $PRIORITY -t epic --body "
## Origin
Dueling Idea Wizards -- [DATE]
Cross-model consensus score: [AVG]/1000

## Idea Summary
[Synthesized from both agents' descriptions -- take the best framing from each]

## Cross-Model Validation
- [Agent A type] score: [X]/1000
  Key argument: [Their strongest reason FOR]
  Key concern: [Their strongest reason AGAINST, if any]
- [Agent B type] score: [Y]/1000
  Key argument: [Their strongest reason FOR]
  Key concern: [Their strongest reason AGAINST]
- Post-reveal adjustments: [Any concessions or escalations]

## Why This Idea Survived Adversarial Scrutiny
[What makes this idea robust enough to survive cross-model evaluation]

## Implementation Approach
[Synthesized from both agents -- where they agree on approach, note it;
where they disagree, present both options]

## Risks and Concerns (From Opponents)
[The OPPONENT's criticism is the most honest risk assessment available.
Extract specific technical concerns from the scoring files.]

## Success Criteria
[Concrete, measurable outcomes]

## Dependencies
[What must exist first]
"
```

## Subtask Decomposition

After creating the epic, decompose into tasks:

```bash
# Implementation tasks
br create "Implement [core component]" -p $PRIORITY -t task --body "..."
br create "Implement [integration point]" -p $PRIORITY -t task --body "..."

# Test tasks (mandatory for duel winners)
br create "Unit tests for [idea]" -p $PRIORITY -t task --body "
## Coverage Requirements
[Specific test scenarios derived from both agents' analysis]

## Edge Cases Flagged by Opponents
[Extract edge cases from the opponent's scoring -- they're more honest about risks]
"

br create "E2E tests for [idea]" -p $PRIORITY -t task --body "
## Scenarios
[Happy path, error path, integration scenarios]

## Logging
[Structured logging for verification]
"

# Wire up dependencies
br dep add [impl-task] [epic]
br dep add [test-task] [impl-task]
```

## Validation After Bead Creation

```bash
bv --robot-insights | jq '.Cycles'      # MUST be empty
bv --robot-plan | jq '.plan.summary'    # Check dependency sanity
br ready --json | jq 'length'           # Verify actionable work exists
```

## Iterative Bead Refinement

Follow the idea-wizard Phase 6 pattern -- refine beads 4-5 times before implementation:

```text
Reread AGENTS.md so it's still fresh in your mind. Check over each bead from the dueling wizards session super carefully -- are you sure it makes sense? Is it optimal? Could we change anything based on the adversarial feedback from the cross-scoring? The opponents' criticisms are especially valuable for identifying risks we haven't thought through. DO NOT OVERSIMPLIFY THINGS! DO NOT LOSE ANY FEATURES OR FUNCTIONALITY! Also make sure that as part of the beads we include comprehensive unit tests and e2e test scripts. Make sure to ONLY use the br cli tool for all changes.
```

## Handling Contested Ideas

For SPLIT verdicts (one agent loves it, one hates it), create a bead but mark it as a "thesis to investigate":

```bash
br create "Investigate: [CONTESTED_IDEA_TITLE]" -p 3 -t task --body "
## Status: Contested (needs human judgment)

## The Disagreement
- [Agent A] scored [X]/1000: [their argument]
- [Agent B] scored [Y]/1000: [their counter-argument]

## What Would Resolve This
[What information or prototype would settle the debate]

## Recommended Next Step
Build a minimal prototype/spike to test the contested assumption,
then re-evaluate.
"
```

## Cross-Referencing with Existing Beads

Before creating beads, always check for overlap:

```bash
br list --json | jq '.[].title'
br list --status closed --json | jq '.[].title'
```

| Overlap Type | Action |
|-------------|--------|
| Direct duplicate | Skip, add cross-model validation to existing bead's body |
| Complementary | Merge insights into existing bead |
| Conflicts with existing | Create new bead noting the conflict; architectural decision needed |
| Subsumes existing | Update existing bead with richer context from duel |
