# Prompt Bank

## Phase 3: Project Study Prompt

Sent to ALL agents at the start. Identical for all agent types.

```text
First read ALL of the AGENTS.md file and README.md file super carefully and understand ALL of both! Then use your code investigation agent mode to fully understand the code, and technical architecture and purpose of the project.
```

## Phase 4: Ideation Prompt (The Idea Wizard)

Sent to ALL agents after study is complete. Customize `$NUM_IDEAS`, `$NUM_TOP`, and optional `$FOCUS`.

### Standard Version

```text
Come up with your very best ideas for improving this project to make it more robust, reliable, performant, intuitive, user-friendly, ergonomic, useful, compelling, etc. while still being obviously accretive and pragmatic. Come up with $NUM_IDEAS ideas and then really think through each idea carefully, how it would work, how users are likely to perceive it, how we would implement it, etc; then winnow that list down to your VERY best $NUM_TOP ideas. Explain each of the $NUM_TOP ideas in order from best to worst and give your full, detailed rationale and justification for how and why it would make the project obviously better and why you're confident of that assessment. Write your final top $NUM_TOP ideas to a file called WIZARD_IDEAS_[YOUR_AGENT_TYPE].md (e.g., WIZARD_IDEAS_CC.md or WIZARD_IDEAS_COD.md or WIZARD_IDEAS_GMI.md). Use ultrathink.
```

### Focused Version (when --focus is set)

```text
Come up with your very best ideas for improving this project, with a particular emphasis on $FOCUS. The ideas should make the project more robust, reliable, performant, intuitive, user-friendly, ergonomic, useful, compelling, etc. while still being obviously accretive and pragmatic. Come up with $NUM_IDEAS ideas and then really think through each idea carefully, how it would work, how users are likely to perceive it, how we would implement it, etc; then winnow that list down to your VERY best $NUM_TOP ideas. Explain each of the $NUM_TOP ideas in order from best to worst and give your full, detailed rationale and justification for how and why it would make the project obviously better and why you're confident of that assessment. Write your final top $NUM_TOP ideas to a file called WIZARD_IDEAS_[YOUR_AGENT_TYPE].md. Use ultrathink.
```

### Expansion Variant (optional Phase 4b)

After collecting the initial top 5, you can optionally ask for more:

```text
Ok and your next best 10 ideas and why. Add them to your WIZARD_IDEAS_[TYPE].md file.
```

This expands the idea pool from 5 to 15. Ideas #6-15 are often complementary to the top 5 and provide more material for cross-scoring. Only use this if you want a richer duel.

## Phase 5: Cross-Scoring Prompt

Sent to each agent individually via `--pane=N`. Contains the OTHER agent's ideas.

### 2-Agent Version

```text
I asked another model the same thing and it came up with this list:

```
$OTHER_AGENT_IDEAS
```

Now, I want you to very carefully consider and evaluate each of them and then give me your candid evaluation and score them from 0 (worst) to 1000 (best) as an overall score that reflects how good and smart the idea is, how useful in practical, real-life scenarios it would be for humans and AI coding agents like yourself, how practical it would be to implement it all correctly, whether the utility/advantages of the new feature/idea would easily justify the increased complexity and tech debt, etc. Write your scores and evaluations to WIZARD_SCORES_${MY_TYPE}_ON_${OTHER_TYPE}.md. Use ultrathink.
```

### 3-Agent Version

When 3 agent types are in play, each agent scores both others' ideas in a single prompt:

```text
I asked two other models the same thing. Here are their ideas:

--- Model A ($TYPE_A) ---
```
$TYPE_A_IDEAS
```

--- Model B ($TYPE_B) ---
```
$TYPE_B_IDEAS
```

Now, I want you to very carefully consider and evaluate EACH idea from BOTH models. Give each idea a candid score from 0 (worst) to 1000 (best) reflecting how good and smart the idea is, how useful in practical, real-life scenarios it would be for humans and AI coding agents like yourself, how practical it would be to implement it all correctly, whether the utility/advantages of the new feature/idea would easily justify the increased complexity and tech debt, etc. Write your scores and evaluations to WIZARD_SCORES_${MY_TYPE}_ON_OTHERS.md. Use ultrathink.
```

## Phase 6: The Reveal Prompt

Sent to each agent individually. Contains how the OTHER agent scored THEIR ideas.

### Standard Reveal

```text
I asked the other model the exact same thing, to score YOUR ideas using the same grading methodology; here is what it came up with:

```
$OTHER_AGENT_SCORES_ON_MY_IDEAS
```

Now give me your honest reaction. Where do you agree with their assessment? Where do you think they're wrong, and why? Are there any ideas where you now think the other model made a good point that changes your own evaluation? Be candid -- if they raised a valid criticism, acknowledge it. If you think they missed something important, explain why. Write your reactions to WIZARD_REACTIONS_${MY_TYPE}.md. Use ultrathink.
```

### 3-Agent Reveal

```text
I asked both other models to score YOUR ideas using the same grading methodology. Here are their evaluations:

--- Model A ($TYPE_A) on your ideas ---
```
$TYPE_A_SCORES_ON_MY_IDEAS
```

--- Model B ($TYPE_B) on your ideas ---
```
$TYPE_B_SCORES_ON_MY_IDEAS
```

Now give me your honest reaction. Where do you agree with their assessments? Where do you think they're wrong, and why? Are there any ideas where both models raised the same concern -- does that change your evaluation? Be candid. Write your reactions to WIZARD_REACTIONS_${MY_TYPE}.md. Use ultrathink.
```

## Nudge Prompts

### Ideation Nudge (agent idle, no ideas file)

```text
You should have your ideas by now. Write your top $NUM_TOP ideas to WIZARD_IDEAS_[YOUR_TYPE].md. Include full rationale for each idea, ordered best to worst.
```

### Scoring Nudge (agent idle, no scores file)

```text
Score the other model's ideas and write your evaluations to the appropriate WIZARD_SCORES_*.md file. Be candid and specific -- scores of exactly 500 for everything are not useful.
```

### Depth Nudge (scores too uniform)

```text
Your scores are too clustered. Some of these ideas must be genuinely better or worse than others. Spread your scores more -- a great idea should be 800+ and a weak one should be 200-. Revise your scoring file.
```

### Reaction Nudge (agent idle, no reactions file)

```text
Write your reactions to the other model's scoring of YOUR ideas. Where do you agree? Where do you disagree? Did any of their criticisms change your mind? Be specific and candid. Write to WIZARD_REACTIONS_[YOUR_TYPE].md.
```

---

## Phase 6.5: Rebuttal Round

After the reveal phase, optionally send this to each agent. This is where the methodology gets genuinely interesting -- agents pick their hill to die on and mount a formal defense. The rebuttal often surfaces reasoning that was implicit in the original idea but never articulated. Produces a `WIZARD_REBUTTAL_${MY_TYPE}.md` file.

```text
You've now seen how the other model scored your ideas and you've given your initial reactions. It's time to get serious.

Pick your TOP 2 ideas that the other model scored lowest -- these are the hills you're going to die on. Write a formal rebuttal for each:

1. **Defense of your underrated ideas**: Make the strongest possible case for why the other model got it wrong. What did they miss? What context did they fail to account for? What second-order effects did they not consider? Be specific and forceful -- cite concrete scenarios, implementation details, or user behavior patterns that support your case.

2. **Attack on their weakest ideas**: Pick the 2 ideas from the OTHER model's list that you scored lowest. Explain precisely why these ideas are worse than the other model thinks. What are the hidden costs? What failure modes did they ignore? What makes this idea look good on paper but fall apart in practice?

For each of the 4 ideas you discuss (2 defenses + 2 attacks), structure your argument as:
- **The claim**: What the scoring disagreement is about
- **The evidence**: Concrete technical or UX reasoning
- **The verdict**: Your final position and confidence level (0-100%)

Write your rebuttals to WIZARD_REBUTTAL_${MY_TYPE}.md. Use ultrathink.
```

## Phase 6.75: Steelman Challenge

Send this AFTER the rebuttal round. This is counterintuitive but incredibly valuable -- an agent forced to steelman its opponent's best idea often discovers why the idea is actually good, and the resulting steelman is frequently more compelling than the originator's own pitch. This phase breaks agents out of adversarial tunnel vision. Produces a `WIZARD_STEELMAN_${MY_TYPE}.md` file.

```text
This is the Steelman Challenge. You are going to do something counterintuitive: argue FOR your opponent's ideas.

Take the other model's #1 highest-scored idea (the one THEY ranked as their best). Your job is to write the STRONGEST POSSIBLE case for this idea -- stronger than the original model wrote it. You are not being asked whether you agree. You are being asked to demonstrate that you understand it deeply enough to advocate for it better than its creator did.

Your steelman must include:
- **Why this idea is actually brilliant**: What insight does it capture that might not be obvious at first glance?
- **The strongest implementation path**: How would you build this to maximize its impact? Be more specific than the original proposal.
- **The second-order benefits**: What positive knock-on effects would this create that the original author may not have articulated?
- **Pre-emptive defense**: What are the two most likely objections, and why are they wrong or manageable?
- **Honest residual concerns**: After steelmanning, what (if any) genuine weaknesses remain that you could not argue away?

Then do the same for their #2 idea.

Be genuinely intellectually honest. If the steelmanning process actually changes your mind about the idea, say so explicitly. Write to WIZARD_STEELMAN_${MY_TYPE}.md. Use ultrathink.
```

## Phase 6.9: The Blind Spot Probe

Send this AFTER the full adversarial exchange (reveal, rebuttals, steelmanning). The adversarial pressure has expanded both models' understanding of the problem space, and they can now see beyond their original framing. This is the creative goldmine of the entire process -- the best novel ideas frequently emerge here. Produces a `WIZARD_BLINDSPOTS_${MY_TYPE}.md` file.

```text
You've now been through the full adversarial process: you generated ideas, scored your opponent's ideas, saw how they scored yours, wrote rebuttals, and steelmanned their best work. Your understanding of this project's improvement space is now significantly broader than when you started.

Here is the critical question: **What important idea did NEITHER of us think of?**

The adversarial process tends to anchor both models on the ideas that were already proposed. But the most valuable insight might be something that falls outside both models' original framing entirely. Think about:

1. **The gap analysis**: Look at both idea lists side by side. What category of improvement is completely absent? What user need or technical concern did both of us somehow overlook?

2. **The synthesis insight**: Is there an idea that only becomes visible when you combine something from your list with something from theirs? An idea that neither list contains but that the intersection of both lists points toward?

3. **The contrarian take**: Is there something both models implicitly assumed was fine or out of scope that actually deserves to be questioned?

Come up with 3-5 genuinely new ideas that emerged from this expanded understanding. These should NOT be variations on previously proposed ideas -- they should be ideas that could only emerge after the adversarial process broadened your perspective. For each, explain why neither model thought of it originally and why it matters.

Write to WIZARD_BLINDSPOTS_${MY_TYPE}.md. Use ultrathink.
```

## Phase 5 Scoring Variants by Mode

When the duel is run with a specific `--focus` mode, the generic scoring criteria ("how good and smart the idea is") should be replaced with mode-specific criteria. Use the appropriate variant below instead of the standard Phase 5 cross-scoring prompt. Each variant changes the scoring rubric while keeping the 0-1000 scale and the same output file convention.

### Architecture Mode

```text
I asked another model the same thing and it came up with this list:

$OTHER_AGENT_IDEAS

Score each idea from 0 (worst) to 1000 (best) using architecture-specific criteria:
- **Structural soundness** (0-250): Does this improve separation of concerns, reduce coupling, or clarify boundaries? Or does it add architectural debt?
- **Scalability impact** (0-250): How does this affect the system's ability to handle growth in data, users, or feature surface area?
- **Maintainability** (0-250): Will this make the codebase easier or harder to reason about in 6 months? Does it reduce or increase cognitive load for contributors?
- **Migration feasibility** (0-250): Can this be adopted incrementally, or does it require a risky big-bang rewrite?

Give a breakdown across these four dimensions and a total score. Write your scores and evaluations to WIZARD_SCORES_${MY_TYPE}_ON_${OTHER_TYPE}.md. Use ultrathink.
```

### Security Mode

```text
I asked another model the same thing and it came up with this list:

$OTHER_AGENT_IDEAS

Score each idea from 0 (worst) to 1000 (best) using security-specific criteria:
- **Threat mitigation value** (0-300): What specific attack vectors or vulnerability classes does this address? How severe are those threats (CVSS-style reasoning)?
- **Attack surface change** (0-250): Does this reduce or expand the attack surface? Does it introduce new trust boundaries or authentication requirements?
- **Defense in depth contribution** (0-200): Does this add a meaningful layer to existing defenses, or is it redundant with existing controls?
- **Implementation risk** (0-250): Security features implemented incorrectly are worse than no security feature at all. How likely is a subtle implementation flaw that creates a false sense of security?

Give a breakdown across these four dimensions and a total score. Write your scores and evaluations to WIZARD_SCORES_${MY_TYPE}_ON_${OTHER_TYPE}.md. Use ultrathink.
```

### UX Mode

```text
I asked another model the same thing and it came up with this list:

$OTHER_AGENT_IDEAS

Score each idea from 0 (worst) to 1000 (best) using UX-specific criteria:
- **User pain reduction** (0-300): How much friction, confusion, or frustration does this eliminate for real users? Is the pain point this addresses common or rare?
- **Discoverability and learnability** (0-250): Will users find and understand this feature naturally, or does it add hidden complexity? Does it follow existing mental models or require learning new ones?
- **Accessibility impact** (0-200): Does this improve or degrade the experience for users with disabilities, slow connections, small screens, or non-English locales?
- **Delight factor** (0-250): Beyond reducing pain, does this make the product genuinely more pleasant to use? Does it create moments of "this is well-made"?

Give a breakdown across these four dimensions and a total score. Write your scores and evaluations to WIZARD_SCORES_${MY_TYPE}_ON_${OTHER_TYPE}.md. Use ultrathink.
```

### Performance Mode

```text
I asked another model the same thing and it came up with this list:

$OTHER_AGENT_IDEAS

Score each idea from 0 (worst) to 1000 (best) using performance-specific criteria:
- **Latency impact** (0-300): What measurable improvement to p50/p95/p99 latency does this provide? Is the improvement on a hot path or a rarely-hit code path?
- **Resource efficiency** (0-250): How does this affect CPU, memory, disk I/O, or network utilization? Does it reduce waste or just shift it?
- **Scalability ceiling** (0-200): Does this raise or lower the throughput ceiling? At what scale does this optimization start to matter?
- **Complexity cost** (0-250): Performance optimizations often trade readability for speed. Is the performance gain worth the maintenance burden? Could a simpler approach get 80% of the benefit?

Give a breakdown across these four dimensions and a total score. Write your scores and evaluations to WIZARD_SCORES_${MY_TYPE}_ON_${OTHER_TYPE}.md. Use ultrathink.
```

## The Convergence Refinement Prompt

Send this when the consensus analysis identifies ideas that both agents independently generated (i.e., scored highly by both sides and appearing in both lists). Independent convergence is a strong signal of high confidence. Send to both agents simultaneously and let them jointly refine the idea. Produces a `WIZARD_CONVERGENCE_${MY_TYPE}.md` file.

```text
Something interesting happened: both you and the other model independently came up with the same idea (or very similar ideas). Here is the convergence:

**Your version:**
$MY_VERSION_OF_IDEA

**Their version:**
$OTHER_VERSION_OF_IDEA

When two different models independently converge on the same idea, that's a strong signal it's genuinely good. But the two versions likely emphasize different aspects or propose different implementation approaches.

Your job is to produce the BEST POSSIBLE version of this idea by synthesizing both perspectives:

1. **What your version got right that theirs missed**: Specific details, edge cases, or implementation insights from your proposal that should be preserved.
2. **What their version got right that yours missed**: Be honest -- if they had a better framing, a better implementation approach, or identified benefits you didn't, acknowledge it.
3. **The synthesized version**: Write the definitive version of this idea that takes the best of both proposals. This should be strictly better than either individual version.
4. **Confidence assessment**: On a scale of 0-100%, how confident are you that this idea should be implemented? What would need to be true for this to fail?

Write to WIZARD_CONVERGENCE_${MY_TYPE}.md. Use ultrathink.
```

## Implementation Spec Prompt

Send this after consensus winners are identified and the duel is winding down. Pick one agent and give it the other agent's implementation notes for each winning idea. This bridges from "good idea" to "actionable plan." Produces a `WIZARD_IMPL_SPEC.md` file.

```text
The duel is over. The following ideas have been identified as consensus winners (scored highly by both models):

$CONSENSUS_WINNERS_WITH_BOTH_AGENTS_NOTES

For each consensus winner above, you have both your own notes and the other model's notes on how to implement it. Your job is to produce a detailed implementation specification that synthesizes both perspectives into an actionable plan.

For each idea, write:

1. **Summary**: One-sentence description of what this is.
2. **Files affected**: List every file that would need to be created or modified, with a brief note on what changes.
3. **Implementation order**: What needs to happen first, second, third? Are there dependencies between steps?
4. **Key design decisions**: Where the two models' implementation approaches differed, which approach is better and why? Where they agreed, note the consensus.
5. **Risk factors**: What could go wrong during implementation? What assumptions are we making?
6. **Estimated complexity**: T-shirt size (S/M/L/XL) with brief justification.
7. **Acceptance criteria**: How do we know this is done and working correctly?

Write the full implementation spec to WIZARD_IMPL_SPEC.md. Use ultrathink.
```

## The "Devil's Advocate" Prompt

Send this as a final stress test after consensus winners are identified. Even ideas scored 900+ by both models might have hidden problems. Assign this to whichever agent was more critical during the scoring phase (or to a fresh third agent if available). Produces a `WIZARD_DEVILS_ADVOCATE.md` file.

```text
You are now the Devil's Advocate. Your job is to find the strongest possible objections to EVERY consensus winner from this duel.

These ideas survived adversarial cross-scoring and were rated highly by multiple models. That makes them likely good -- but "likely good" is not "certainly good." Popular consensus among AI models can still be wrong, especially when:
- Both models share similar training biases
- The ideas sound impressive but have subtle practical problems
- The second-order consequences weren't fully explored
- The implementation complexity was underestimated
- There are better alternatives that neither model considered

For each consensus winner:

**Idea**: $IDEA_TITLE
1. **The strongest objection**: What is the single most compelling reason NOT to do this? Not a nitpick -- the real killer argument.
2. **The hidden cost**: What ongoing maintenance burden, performance cost, or complexity tax does this create that wasn't discussed?
3. **The failure mode**: Describe the most likely way this idea fails or backfires after implementation. Be specific.
4. **The alternative**: Is there a simpler or better way to achieve the same benefit that neither model proposed?
5. **Final verdict**: After making the strongest possible case against it, do you still think this idea should be implemented? (Yes/No/Yes-but-modified, with explanation)

Be ruthless but intellectually honest. If an idea truly has no serious objections, say so -- but explain why you're confident rather than just rubber-stamping it.

Write to WIZARD_DEVILS_ADVOCATE.md. Use ultrathink.
```

## Post-Compaction Recovery Prompt

Send this when an agent's context gets compacted mid-duel (detected by NTM monitoring or when an agent seems to have lost track of the duel state). This prompt re-establishes the full duel context and brings the agent back up to speed. Adjust `$CURRENT_PHASE` and the included files to match where the duel actually is.

```text
CONTEXT RECOVERY -- You were participating in a Dueling Idea Wizards session but your context was compacted. Here is the full state of the duel so you can pick up where you left off.

**Your role**: You are the $MY_TYPE agent in a $NUM_AGENTS-agent adversarial idea generation duel for the project in this repository.

**Duel state**: We are currently in $CURRENT_PHASE.

**Your ideas** (from WIZARD_IDEAS_${MY_TYPE}.md):
$MY_IDEAS

**Other agent's ideas** (from WIZARD_IDEAS_${OTHER_TYPE}.md):
$OTHER_IDEAS

**Your scores on their ideas** (from WIZARD_SCORES_${MY_TYPE}_ON_${OTHER_TYPE}.md, if exists):
$MY_SCORES_ON_THEIRS

**Their scores on your ideas** (from WIZARD_SCORES_${OTHER_TYPE}_ON_${MY_TYPE}.md, if exists):
$THEIR_SCORES_ON_MINE

**Your reactions so far** (from WIZARD_REACTIONS_${MY_TYPE}.md, if exists):
$MY_REACTIONS

**What you need to do next**: $NEXT_TASK_DESCRIPTION

Re-read the project files (AGENTS.md, README.md) to refresh your understanding of the codebase, then proceed with the task described above. Use ultrathink.
```
