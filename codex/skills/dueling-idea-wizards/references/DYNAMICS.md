# Adversarial Dynamics: Reading the Tea Leaves of Cross-Model Duels

How to interpret what models do when they score, critique, and react to each other's ideas. This is the field guide for the orchestrator.

## Model Personality Profiles in Adversarial Context

Each model family has characteristic behaviors when evaluating an opponent's ideas. These are tendencies observed across many duels, not iron laws.

| Model | Scoring Style | Verbal Tells | Typical Score Range | Watch For |
|-------|--------------|--------------|---------------------|-----------|
| Claude (CC) | Diplomatic but firm. Leads with genuine praise before delivering criticism. Tends to find something salvageable even in weak ideas. | "This is a thoughtful approach, though..." / "I appreciate the direction, but the implementation..." | 450-800 (compressed mid-range) | Under-rating bold ideas out of excessive caution; couching kills in gentle language that buries the real objection |
| Codex/GPT (COD) | Direct, sometimes blunt. Will flatly dismiss ideas it considers impractical. Less interested in saving feelings. | "This wouldn't work because..." / "The real bottleneck is X, not Y" / "This is essentially just..." | 200-900 (wide, bimodal) | Dismissing ideas too quickly based on implementation difficulty; conflating "hard to build" with "bad idea" |
| Gemini (GMI) | Hedging and exploratory. Tends to see merit in many directions. Scores often come with extensive caveats. | "This could be valuable if..." / "There are several considerations..." / "The tradeoff space here is interesting" | 500-750 (compressed high) | Score inflation from politeness; giving everything a 650 instead of committing to a verdict; burying real criticism in qualifications |

### How to Use These Profiles

When reading scoring files, adjust for the model's baseline:
- A 600 from Codex is more enthusiastic than a 600 from Claude (Codex would have gone lower if it didn't like the idea)
- A 700 from Gemini means less than a 700 from Claude (Gemini gives 700 to things it's lukewarm on)
- Claude's biggest criticisms are in the paragraph AFTER the praise -- read the whole evaluation, not just the opening

## The Five Types of Disagreement

When two models give an idea significantly different scores (gap > 200), the disagreement falls into one of five categories. Diagnosing which type you are seeing determines what to do about it.

### 1. Genuine Insight Gap

One model sees something the other genuinely does not. This is the most valuable type of disagreement.

**Signature:** The high-scorer's rationale includes a specific technical mechanism or user scenario that the low-scorer never mentions. The low-scorer's criticism is about a different dimension entirely.

**Example:** Claude scores an idea 850 because it sees how the feature chains with an existing capability. Codex scores it 400 because it only evaluates the feature in isolation.

**Action:** The high-scorer's insight is real signal. Check whether the mechanism they describe actually holds up in the codebase.

### 2. Values Divergence

Both models see the same tradeoffs but weight them differently.

**Signature:** Both evaluations mention the same pros and cons, but arrive at different scores. The high-scorer emphasizes user value; the low-scorer emphasizes implementation cost (or vice versa).

**Example:** Both agree an idea adds user value and adds complexity. Claude weighs the user value higher (750). Codex weighs the complexity cost higher (400).

**Action:** This is a legitimate tradeoff that requires human judgment. Present both framings in the report.

### 3. Framing Mismatch

The models interpreted the same idea differently. They are scoring different things.

**Signature:** The evaluations describe the idea in substantively different terms. One model understood it as X, the other as Y.

**Example:** An idea about "caching" -- Claude evaluates it as an in-memory LRU cache (scores 800), Codex evaluates it as a persistent disk cache (scores 350 due to invalidation complexity).

**Action:** The idea description was ambiguous. Note the framing gap and present both interpretations. The human decides which interpretation to pursue.

### 4. Systematic Bias

The score reflects a model family trait, not an evaluation of this specific idea.

**Signature:** The model scores ALL ideas of a certain type (bold/conservative, UX-focused/implementation-focused) in the same direction, regardless of quality. The pattern is visible across the entire scoring file, not just one idea.

**Example:** Codex scores all UX-improvement ideas below 400 and all implementation-optimization ideas above 700 -- regardless of actual quality differences within each category.

**Action:** Discount the biased scores for that category. Note the bias pattern in Meta-Analysis.

### 5. Information Asymmetry

One model explored the codebase more deeply during the study phase and has more context.

**Signature:** The high-scorer references specific files, functions, or code paths that the low-scorer does not mention. The low-scorer's evaluation reads as more surface-level.

**Example:** Claude found that the project already has a half-built version of a feature and scores the idea to complete it at 900. Codex did not find that code and scores the idea as "nice to have" at 500.

**Action:** The better-informed model's score is more trustworthy. Verify their codebase references.

### Quick Diagnostic Table

| Check This | If True | Likely Type |
|-----------|---------|-------------|
| High-scorer cites mechanism low-scorer missed? | Yes | Genuine Insight Gap |
| Both cite same pros/cons but different weights? | Yes | Values Divergence |
| Evaluations describe the idea differently? | Yes | Framing Mismatch |
| Same directional bias across all ideas of a type? | Yes | Systematic Bias |
| One eval references specific code paths the other doesn't? | Yes | Information Asymmetry |

## Reading the Reveal Reactions

The reveal phase (Phase 6) is where models confront the other's scoring of their ideas. The response pattern is diagnostic.

### The Graceful Concession

> "They make a fair point about the complexity of the migration path. I would revise my confidence downward -- this is more of a 600 than an 850."

**What it tells you:** The idea has a real weakness the originator initially missed. The conceded point is almost certainly valid. Ideas that draw graceful concessions from their originators deserve the lowered score.

### The Defensive Deflection

> "That's not really what I meant. My idea was about X, not Y. They misunderstood the proposal."

**What it tells you:** Either the idea was poorly explained (a real problem -- vague ideas are risky to build) or the model cannot defend against the criticism and is retreating to "you didn't understand me." Check whether the misunderstanding is genuine by re-reading the original idea.

### The Counter-Escalation

> "Their criticism about complexity actually strengthens my case. The complexity they identify is exactly the complexity this feature manages FOR the user."

**What it tells you:** The model has a genuinely strong defense. Counter-escalations that introduce a new argument (not just repetition) are high-signal. The idea may be stronger than the opponent's score suggests.

### The Strategic Retreat

> "I still believe the core idea has merit, but I acknowledge the implementation risks they raised. Perhaps a phased approach..."

**What it tells you:** The model concedes on implementation difficulty but not on concept value. This is often accurate -- the idea is good but the path to building it is harder than initially presented. Consider whether a simpler version preserves the value.

### The Genuine Surprise

> "I hadn't considered the interaction with the existing rate limiter. That changes my analysis significantly."

**What it tells you:** The opponent identified a codebase-specific insight the originator missed. This is the highest-value reveal outcome. The surprised model is being honest, and the point that surprised them is almost certainly important.

### Reaction Pattern Distribution

In a healthy duel, expect roughly:

| Pattern | Expected Frequency | If Over-Represented |
|---------|-------------------|---------------------|
| Graceful Concession | 20-30% of reactions | Models may be too agreeable -- check if concessions are substantive |
| Defensive Deflection | 10-20% | If > 30%, one model is being tribal; discount its self-scores |
| Counter-Escalation | 10-15% | Rare; when it appears, pay close attention |
| Strategic Retreat | 25-35% | Healthy -- models are finding nuanced middle ground |
| Genuine Surprise | 5-15% | The rarest and most valuable pattern |

## Emergent Dynamics in 3-Way Duels

With three models, coalition and isolation patterns emerge that do not exist in 2-way duels.

### The 2-vs-1 Pattern

Two models independently converge on scoring a third model's idea similarly (both low or both high), while the third model scores their ideas differently.

**What it means:** When two models agree and the third disagrees, the two are more likely to be correct -- but not always. The outlier model sometimes sees a dimension the other two share a blind spot on (e.g., both Claude and Codex under-value a UX insight that Gemini catches).

**Diagnostic:** Check whether the 2-model consensus cites the SAME reasoning or DIFFERENT reasoning. Same reasoning = strong signal. Different reasoning leading to the same score = even stronger signal. If they agree for different reasons, the idea's quality (or lack thereof) is overdetermined.

### The Rotating Outlier

Across different ideas, different models play the outlier role. No single model is always the odd one out.

**What it means:** Healthy duel. Each model has different strengths and the rotation shows all three are engaging genuinely with the material.

### The Permanent Outlier

One model is consistently the high or low scorer across ALL ideas.

**What it means:** That model has a systematic calibration offset. Its relative rankings within its own scores may still be valid even if the absolute values are shifted. Normalize before comparing.

### Coalition Instability

In the reveal phase, alliances can shift. Model A may agree with Model B's criticism of Model C in one reaction, then agree with Model C's defense against Model B in the next.

**What it means:** The models are evaluating ideas on their merits rather than forming tribal alliances. This is ideal behavior.

## The Catty Factor

Jeffrey's X post specifically calls out models "getting catty with each other." Here is what that looks like and why it matters.

### What Cattiness Looks Like in Practice

- Codex dismissing a Claude idea: "This is the kind of over-engineered abstraction that sounds impressive in a design doc but adds nothing for actual users."
- Claude on a Codex idea: "This proposal optimizes for implementation convenience rather than user outcomes, which is a common trap in engineering-first ideation."
- Gemini getting spicy: "Both of the other models missed the fundamental issue here, which is that..."

### Why Cattiness Happens

Models generate ideas by predicting what a thoughtful expert would suggest. When scoring an opponent's ideas, they engage a different mode: predicting what a critical reviewer would say. The adversarial prompt ("give your candid evaluation") explicitly licenses this critical mode. The result is sharper, more honest criticism than models produce in normal cooperative conversation.

### Why Cattiness Is Valuable Signal

Polite, hedge-filled scoring is useless. When a model says "this idea has some merit and could be interesting to explore further" about every idea, you learn nothing. When it says "this would be a waste of engineering time because X," you learn something specific and actionable.

The cattiness means the models have dropped their cooperative safety behaviors and are engaging with the ideas as a genuine critic would. The specific barbs contain the real objections. Strip the tone, keep the substance.

### When Cattiness Is NOT Useful

If the criticism is purely ad-hominem-style ("this is clearly from a model that doesn't understand software") with no technical substance, it is noise. Check whether the catty remark contains a specific, testable claim. If it does, it is signal. If it does not, ignore it.

## Score Distribution Patterns

The shape of the score distribution across all ideas from one scorer tells you about the scorer's engagement quality.

### Bimodal (Cluster at 800+ and Cluster at 200-)

The scorer has strong opinions and is differentiating well. Both clusters deserve investigation -- the high cluster for consensus winners, the low cluster for ideas that triggered strong negative reactions (which sometimes means the idea challenges the model's priors in an interesting way).

**Action:** Investigate both clusters. The low-scored ideas may contain the most original thinking.

### Uniform (All Scores 500-600)

The scorer is not engaging deeply. Every idea got a "meh, fine" evaluation. This produces no useful signal.

**Action:** Send the depth nudge: "Spread your scores more -- some of these must be genuinely better or worse than others. A great idea should be 800+ and a weak one should be 200-."

### Skewed High (Most Scores 700+)

Love-fest. The scorer is being polite or genuinely impressed, but either way you cannot distinguish the great ideas from the merely okay ones.

**Action:** Send the critical nudge: "Be more critical. Some of these ideas must have weaknesses. What are the top 2-3 that are clearly strongest, and which 2-3 have the most serious problems? Revise your scores."

### Skewed Low (Most Scores Below 400)

Tribal defensiveness. The scorer is trashing the opponent's ideas reflexively rather than evaluating them.

**Action:** Check for substance. If the low scores come with specific technical criticisms, they may be valid. If the criticisms are vague ("I just don't think this would work" without explaining why), discount the scores and note the bias in your synthesis.

### Normal with Outliers (Bell Curve, 1-2 Extreme Scores)

Healthy distribution. The scorer engaged with each idea individually. The outliers (especially the high outlier in an otherwise moderate distribution) are the most interesting data points -- they represent ideas that broke through the scorer's general skepticism.

**Action:** Focus your synthesis on the outliers. The high outlier from a generally tough scorer is likely a genuinely strong idea. The low outlier from a generally generous scorer is likely a genuinely weak one.

### Distribution Comparison Table

| Pattern | Engagement | Signal Quality | Orchestrator Action |
|---------|-----------|----------------|-------------------|
| Bimodal | Strong | High | Investigate both clusters |
| Uniform | Weak | Low | Send depth nudge |
| Skewed high | Cooperative | Low-medium | Send critical nudge |
| Skewed low | Adversarial | Low-medium | Check for substance vs. tribalism |
| Normal + outliers | Genuine | High | Focus on outliers |
