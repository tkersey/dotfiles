# Scoring Rubric and Interpretation

## The 0-1000 Scale

The scoring prompt asks agents to evaluate on a composite scale. Here's how to interpret scores:

| Range | Meaning | Action |
|-------|---------|--------|
| 900-1000 | Exceptional -- no-brainer, do it now | Pursue immediately |
| 700-899 | Strong -- clearly accretive, worth the effort | Pursue with priority |
| 500-699 | Decent -- has merit but also real concerns | Evaluate further |
| 300-499 | Weak -- costs likely outweigh benefits | Deprioritize unless champion emerges |
| 100-299 | Poor -- fundamental problems with the idea | Kill unless strong counter-argument |
| 0-99 | Terrible -- actively harmful or nonsensical | Dead on arrival |

## Score Dimensions

The prompt asks agents to evaluate across multiple dimensions implicitly. When reading scoring files, look for commentary on:

1. **Smartness** -- Is this a clever insight or an obvious suggestion?
2. **Practical utility** -- Would real humans and AI agents actually benefit?
3. **Implementation feasibility** -- Can we build this correctly without heroics?
4. **Complexity budget** -- Does the value justify the added complexity and tech debt?
5. **Accretiveness** -- Does this build on existing strengths rather than bolt on unrelated features?

## Cross-Score Analysis

### Consensus Matrix

After collecting all scores, build this matrix:

```
| Idea | Origin | Agent A Score | Agent B Score | Agent C Score | Avg | Gap | Verdict |
|------|--------|---------------|---------------|---------------|-----|-----|---------|
| #1   | CC     | (self)        | 850           | 780           | 815 | 70  | STRONG  |
| #2   | CC     | (self)        | 350           | 420           | 385 | 70  | WEAK    |
| #3   | COD    | 900           | (self)        | 650           | 775 | 250 | SPLIT   |
```

### Interpreting the Gap

The gap between scores is as informative as the scores themselves:

| Gap (max - min) | Interpretation |
|-----------------|----------------|
| < 100 | Strong agreement -- high confidence in the verdict |
| 100-250 | Mild disagreement -- worth investigating why |
| 250-400 | Significant disagreement -- model biases at play |
| > 400 | Fundamental disagreement -- one model sees something the other doesn't |

### Verdict Categories

- **CONSENSUS WIN** -- All agents score 700+, gap < 200. Do this.
- **STRONG** -- Average 700+, no agent below 500. Very likely good.
- **SPLIT** -- One agent loves it (800+), another is lukewarm or hostile. Needs human judgment.
- **CONSENSUS KILL** -- All agents score below 400. Don't do this.
- **CONTESTED** -- Average 400-700 with large gap. The disagreement itself is interesting.

## Post-Reveal Score Adjustments

After the reveal phase, agents sometimes revise their positions. Track:

1. **Concessions** -- "They made a good point, I lower my score to X." These are high-signal: a model acknowledging its own blind spot.
2. **Defenses** -- "I disagree because Y." If the defense is substantive, the original score stands. If it's defensive/vague, discount it.
3. **Escalations** -- "Actually, their criticism made me realize my idea is even better because Z." Rare but interesting -- the adversarial pressure surfaces a stronger argument.

## Calibration Notes

### Known Model Biases in Scoring

| Model Family | Typical Bias | Watch For |
|-------------|-------------|-----------|
| Claude (CC) | Tends toward nuanced mid-range scores (500-750) | May under-rate bold ideas out of caution |
| Codex/GPT (COD) | Can be more extreme (high highs, low lows) | May over-rate implementation-heavy ideas |
| Gemini (GMI) | Sometimes generous across the board | May cluster scores in 600-800 range |

These are tendencies, not rules. Actual behavior varies by project and prompt.

### Score Inflation Detection

If an agent scores all opponent ideas above 600, it's likely being polite rather than honest. Send the depth nudge prompt from [PROMPTS.md](PROMPTS.md).

### Score Deflation Detection

If an agent scores all opponent ideas below 300, it's likely being tribal. Check whether the defenses in the reaction file are substantive. If they're vague ("I just think my approach is better"), discount the low scores.

## The 10-Criterion Evaluation Rubric

The cross-scoring prompt asks for a single 0-1000 score, but that score implicitly evaluates across the Idea Wizard's 10 criteria. When reviewing scoring files, check if the agent addressed each:

| Criterion | What It Means | Red Flag If Missing |
|-----------|---------------|---------------------|
| **Robust** | Handles edge cases, doesn't break | Security/reliability ideas under-evaluated |
| **Reliable** | Works consistently, not intermittent | Operability concerns missed |
| **Performant** | Fast enough for the use case | Latency-sensitive code not considered |
| **Intuitive** | Users predict behavior correctly | API/UX ideas under-evaluated |
| **User-friendly** | Pleasant experience, helpful errors | Developer experience ignored |
| **Ergonomic** | Reduces friction, fewer steps | Workflow improvements dismissed |
| **Useful** | Solves a real, frequent problem | "Cool but pointless" ideas over-rated |
| **Compelling** | Users would want/request this | "Nobody asked for this" risk |
| **Accretive** | Adds clear value, builds on strengths | Bolt-on features over-rated |
| **Pragmatic** | Realistic to build correctly | Fantasy features rated too high |

### Weighted Scoring

For synthesis, weight these criteria:
- **Useful**: 2x (does it solve a real problem?)
- **Pragmatic**: 2x (can we actually build it right?)
- **Accretive**: 1.5x (does it make the project genuinely better?)
- All others: 1x

An idea that scores 900 on "compelling" but 200 on "pragmatic" is a trap. The weighted average reveals this.

### Winnowing Heuristics

Imported from the idea-wizard rubric:
- **Hard cut**: Score of 1/5 on ANY criterion = instant kill
- **Threshold cut**: Average below 3/5 = deprioritize
- **Synergy bonus**: Weaker ideas that enable stronger ideas may deserve elevation
- **Red flag phrases**: "Users will figure it out", "We'll document it later", "It's technically correct" = immediate skepticism

## Mapping Scores to Action

After synthesis, map the consensus winners to next steps:

| Score Range | Suggested Next Step |
|-------------|-------------------|
| Consensus 800+ | Create a bead immediately (`br create`) -- see [BEADS.md](BEADS.md) |
| Consensus 700-800 | Draft a brief implementation spec, then bead |
| Split with avg 700+ | Discuss with project owner, then decide |
| Split with avg < 700 | Table it -- revisit if the champion model's reasoning improves |
| Consensus < 400 | Archive in the report as "considered and rejected" |

## Disaggregated Score Analysis

For the most important ideas, ask the scoring agent to break down their score:

```text
For your top-scored and bottom-scored idea from the other model, break your overall score into these 10 sub-scores (each 0-100): Robust, Reliable, Performant, Intuitive, User-friendly, Ergonomic, Useful, Compelling, Accretive, Pragmatic. This helps us understand WHERE you see strength or weakness.
```

This optional follow-up (send after Phase 5 if you want deeper analysis) produces a detailed profile per idea that makes disagreements much easier to diagnose.
