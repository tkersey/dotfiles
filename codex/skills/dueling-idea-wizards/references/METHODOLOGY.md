# Methodology: Why Adversarial Cross-Model Ideation Works

## The Epistemological Framework

### Single-Model Ideation is Grading Your Own Homework

When a single model generates 30 ideas and winnows to 5, it applies its own evaluation function to its own generative function. The blind spots are correlated: the same biases that caused it to generate certain ideas also cause it to rate those ideas favorably. This is precisely the "confirmation bias" problem, but at the model level.

### Cross-Model Scoring Decorrelates the Blind Spots

Different model families (Claude, GPT/Codex, Gemini) have genuinely different:
- **Training data distributions** -- different corpora emphasize different patterns
- **RLHF reward signals** -- different alignment objectives create different preference profiles
- **Architectural biases** -- different attention patterns favor different reasoning styles
- **Failure modes** -- where Claude is cautious, GPT may be bold, and vice versa

When Model A scores Model B's ideas, the evaluation function is decorrelated from the generative function. This is the same principle behind ensemble methods in ML, peer review in science, and adversarial training in GANs -- independent evaluation surfaces errors that self-evaluation misses.

### The 0-1000 Scale Forces Granularity

A binary "good/bad" rating loses information. The 0-1000 scale forces models to commit to relative rankings, which exposes their confidence levels. An idea scored 850 by one model and 300 by another tells you something fundamentally different from an idea scored 600 by both. The gap is the signal.

### The Reveal Phase Exploits Social Dynamics

Even LLMs exhibit something resembling social pressure. When shown that another model rated their ideas poorly, they face a choice: defend or concede. The concessions are extremely high-signal -- a model acknowledging its own blind spot is rare and valuable. The defenses are also informative: a strong technical defense means the original score was justified; a vague defensive response means the model was wrong and can't articulate why.

## The Operator Toolkit

Drawing from `operationalizing-expertise`, these are the cognitive operators the dueling wizard methodology implicitly invokes:

### ✂ Exclusion-Test (via Cross-Scoring)
The opponent's scoring is an exclusion test on each idea. Low scores with specific technical reasoning are hypothesis killers -- they identify ideas that sound good but don't survive scrutiny.

### ◊ Paradox-Hunt (via Score Gaps)
Large score gaps between models are paradoxes worth investigating. When two capable models disagree fundamentally about an idea's value, the disagreement itself is a signal about hidden assumptions, underspecified requirements, or genuine trade-offs.

### ⊕ Cross-Domain (via Model Diversity)
Different models bring different "domain expertise" by virtue of their different training. Codex/GPT tends to see implementation patterns; Claude tends to see systemic implications; Gemini tends to see user-facing angles. The cross-pollination is automatic.

### ΔE Exception-Quarantine (via Contested Ideas)
Ideas that score wildly differently between models are exceptions that deserve quarantine rather than dismissal. They may represent genuine insight that one model has and the other lacks, or they may represent a bias that one model needs corrected.

### † Theory-Kill (via Consensus Kill)
When all models agree an idea is weak, it's dead. No amount of the originator's enthusiasm can revive it. This is the fastest, cheapest way to kill mediocre ideas -- much cheaper than building them and discovering they're mediocre.

## Why the Methodology Scales

### To More Models
Adding a third model (3-way duel) provides more data points per idea. The consensus becomes more robust, and the contested ideas become more interesting because you can see which model is the outlier.

### To Different Domains
The cross-scoring mechanic is domain-agnostic. The mode variants (architecture, security, UX, performance) just change what the models generate -- the adversarial dynamics work identically regardless of domain.

### To Multiple Rounds
Fresh sessions between rounds prevent "exhausted mine" effects. Each round starts with a clean context, so models don't converge toward a shared understanding that might be wrong. The multi-round approach is essentially a tournament bracket for ideas.

### From Ideation to Action
The bead creation pipeline (Phase 8) bridges the gap from "good ideas" to "actual work." The opponent's criticism gets embedded directly into the bead as a risk assessment, which means the implementation team inherits adversarially-validated specifications rather than wishful-thinking feature requests.

## Comparison to Other Approaches

| Approach | Strengths | Weaknesses | Dueling Wizards Advantage |
|----------|-----------|------------|---------------------------|
| Single-agent brainstorm | Fast, simple | Confirmation bias, no adversarial pressure | Decorrelated evaluation |
| Multi-model triangulation | Gets multiple perspectives | Manual copy-paste, no adversarial dynamics | Automated via NTM, reveal phase adds pressure |
| Human brainstorming | Social dynamics, domain expertise | Slow, groupthink, political dynamics | Faster, no politics, unlimited energy |
| Modes-of-reasoning analysis | Deep analytical coverage | Analysis, not ideation | Complementary -- use modes first, duel on conclusions |
| Design review board | Multi-perspective evaluation | Expensive, calendar-bound | Available 24/7, costs ~$7/day per model |

## When NOT to Use This

- **Trivial decisions** -- if the right answer is obvious, don't waste agents on it
- **Highly constrained problems** -- if there's only one viable approach, ideation adds nothing
- **Emergency fixes** -- speed matters more than completeness; just fix it
- **Style preferences** -- models are bad at aesthetics; use human judgment
- **When you have 1 model type** -- dueling requires decorrelated evaluators; same model x2 is just noise

## When to Use This

- **Roadmap planning** -- "what should we build next?" is the canonical use case
- **Pre-architecture** -- before committing to a design, duel on alternatives
- **Pre-launch** -- security/reliability duels catch what single-model reviews miss
- **After a big milestone** -- step back and adversarially evaluate "where do we go from here"
- **When stuck** -- if you can't decide between approaches, let the models fight it out

---

## The Information Theory of Adversarial Scoring

Model the duel as an information channel. Each model's scoring function adds information bits to the evaluation of each idea. The key insight is that **consensus and disagreement carry fundamentally different types of information**.

### Consensus = Low Entropy, High Confidence

When both models score an idea similarly (e.g., both give 750-800), this is a low-entropy signal. The information content is: "two decorrelated evaluators agree on the value of this idea." Because their biases are decorrelated, agreement is strong evidence that the idea genuinely has the properties both models attribute to it. This is analogous to two independent measurements returning the same value -- the confidence interval shrinks dramatically.

### Disagreement = High Entropy, High Information

When models diverge sharply (e.g., 850 vs. 300), the entropy is high -- but so is the information value. A large score gap reveals **hidden structure**: one model is seeing something the other is not. This could be:
- A genuine insight one model has and the other lacks
- A hidden assumption that one model is making and the other is not
- A domain-specific consideration that one model weighs heavily and the other ignores
- A fundamental ambiguity in the idea specification that admits two valid interpretations

The disagreement itself is more valuable than either score alone because it identifies exactly where investigation is needed.

### The Bayesian Update Chain

Each phase of the duel functions as a Bayesian update step, where prior beliefs about an idea's value get revised based on new evidence:

**Phase 4 (Ideation) -- Hypothesis Generation:**
Information value = **generative**. Each model produces 30 hypotheses about what improvements matter. These are priors drawn from each model's training distribution. No evaluation has occurred yet, so the information is raw and unfiltered. The self-winnowing to top 5 is the first filter, but it's still grading your own homework.

**Phase 5 (Cross-Scoring) -- First Bayesian Update:**
Information value = **evaluative, decorrelated**. Each model evaluates the other's ideas using a different evaluation function than the one that generated them. This is the first real information injection: the prior (self-assessment) gets updated by independent evidence (opponent assessment). The magnitude of the update is proportional to the score gap -- large gaps mean large updates, small gaps mean the prior was approximately correct.

**Phase 6 (Reveal) -- Second Bayesian Update with Social Pressure:**
Information value = **meta-evaluative**. Each model now sees both its own score and the opponent's score for every idea. This is a second-order update: the model must now update not just on "what is this idea worth?" but on "what does it mean that we disagree about what this idea is worth?" The social pressure component (seeing that an opponent rated your favorite idea poorly) forces re-examination. Models that update honestly here produce the highest-quality signal in the entire pipeline.

**Phase 6.5 (Rebuttal) -- Adversarial Stress Test:**
Information value = **adversarial, targeted**. This phase specifically targets the highest-disagreement ideas and forces the defending model to articulate WHY it disagrees with the opponent's assessment. The information gain comes from the quality of the defense: a strong technical defense with specific evidence is high-information; a vague "I still think it's good" is low-information and effectively a concession.

**Phase 6.75 (Steelman) -- Forced Perspective Shift:**
Information value = **empathetic, counter-bias**. Each model must construct the strongest possible version of the opponent's argument. This is the most epistemically demanding phase because it requires modeling the opponent's reasoning well enough to improve upon it. The information gained is about the idea's maximum potential value (as opposed to its current articulation).

**Phase 6.9 (Blind Spot Probe) -- Creative Expansion Beyond Original Frames:**
Information value = **generative, meta-level**. Rather than evaluating existing ideas, this phase asks "what did BOTH of us miss?" The information is orthogonal to everything generated so far because it specifically targets the intersection of both models' blind spots. Ideas surfaced here are often the most novel because they required two rounds of adversarial evaluation to expose the gap where they live.

### Quantifying the Information Budget

Across a typical 2-model duel:
- Phase 4 generates ~60 ideas (raw bits, high redundancy)
- Phase 5 adds ~10 bits per idea (independent evaluation)
- Phase 6 adds ~5 bits per idea (meta-evaluation) but ~20 bits for high-disagreement ideas
- Phases 6.5-6.9 add ~15-30 bits concentrated on the 5-8 most contested ideas

The information is front-loaded in volume (Phase 4) but back-loaded in quality (Phases 6-6.9). The later phases produce fewer bits but those bits have dramatically higher signal-to-noise ratio.

---

## The Innovation Funnel in Practice

The dueling wizard pipeline maps directly onto the classic innovation funnel model (diverge, filter, converge, validate), but with adversarial dynamics at each stage.

### Stage 1: Diverge (Phase 4 -- Ideation)

Each model independently generates 30 ideas. The independence is critical -- no cross-contamination means the two idea sets represent genuinely different samplings from the possibility space. Two models with different training distributions sampling 30 ideas each will produce some overlap (typically 3-7 ideas that are obviously similar) and significant unique coverage (20+ ideas that only one model thought of).

**Total ideas entering the funnel: ~60** (30 per agent)

### Stage 2: Self-Filter (Still Phase 4)

Each model winnows its own 30 ideas down to its top 5. This is the weakest filter in the pipeline because it's self-evaluation, but it's necessary to make cross-scoring tractable. The winnowing criteria tend to favor ideas the model can articulate clearly and feels confident about -- which means the 25 ideas killed at this stage include both genuinely weak ideas AND ideas the model couldn't fully articulate despite their potential value.

**Ideas surviving self-filter: 10** (5 per agent)

### Stage 3: Adversarial Filter (Phase 5 -- Cross-Scoring)

The opponent scores each surviving idea on the 0-1000 scale. This is where the funnel gets aggressive. Ideas that score below ~400 from the opponent are effectively killed -- they might be defended in the rebuttal phase, but they start with a significant deficit. Ideas that score above ~700 from both models are consensus winners and advance easily.

**Typical distribution after cross-scoring:**
- Consensus winners (both score 650+): 3-5 ideas
- Contested (gap > 300 points): 2-3 ideas  
- Consensus kills (both score < 500): 2-4 ideas

### Stage 4: Convergence Test (Phase 6 -- Reveal)

The reveal forces honest re-evaluation. Models see both scores and must update their assessments. This phase tends to **collapse the contested middle**: models that were on the fence about an idea either strengthen their commitment (seeing the opponent agrees) or abandon it (seeing the opponent's detailed critique). The contested ideas from Stage 3 typically resolve here: 1-2 get promoted to consensus winners, 1-2 get killed.

**Ideas with strong support after reveal: 4-6**

### Stage 5: Stress Test (Phases 6.5, 6.75 -- Rebuttal and Steelman)

The surviving contested ideas get the most rigorous treatment. The rebuttal phase lets defenders make their case; the steelman phase forces attackers to consider they might be wrong. Ideas that survive both phases with strong support from at least one model are genuinely robust -- they've been attacked, defended, and their best possible version has been articulated.

**Ideas surviving stress test: 3-5 consensus + 1-2 contested-but-strong**

### Stage 6: Creative Expansion (Phase 6.9 -- Blind Spot Probe)

After the filtering is complete, the blind spot probe adds 1-3 genuinely new ideas that neither model originally proposed. These ideas often combine elements from the killed ideas in novel ways, or address problems that the original framing missed entirely.

**Ideas added by blind spot probe: 1-3**

### Stage 7: Action (Phase 8 -- Bead Creation)

The consensus winners and strong contested ideas get converted into actionable beads with adversarially-validated specifications. Each bead carries the opponent's critique as embedded risk assessment.

**Final output: 4-8 beads**

### Funnel Statistics

Of ~60 total ideas generated (30 per agent):
- **50+ are killed** -- by self-winnowing, cross-scoring, or consensus kill
- **3-5 survive as consensus winners** -- both models agree these are strong
- **2-3 are contested but strong** -- one model championed them through adversarial pressure
- **1-3 are novel additions** -- surfaced by the blind spot probe

This **~90% kill rate** is a feature, not a bug. The funnel is aggressive by design because the cost of implementing a mediocre idea far exceeds the cost of generating and evaluating ten ideas to find one good one. A single duel session (~30-60 minutes, ~$7 in API costs) achieves a compression ratio that would take a human team days of meetings to approximate.

---

## Why "Use Ultrathink" Matters

The prompts throughout the dueling wizard pipeline all end with "Use ultrathink" (or equivalent extended thinking triggers like "think deeply" or "reason step by step before scoring"). This is not stylistic decoration. It is a load-bearing structural element of the methodology.

### The Pattern-Matching Failure Mode

Without extended thinking, models tend to:
1. Read an idea description
2. Pattern-match it against similar ideas they've seen in training
3. Produce a score that reflects familiarity rather than quality
4. Generate a brief justification that is post-hoc rationalization of the pattern-matched score

This produces polite, vague, clustered scores -- most ideas land in the 500-700 range with generic comments like "this is a reasonable idea with some implementation challenges." The scores carry almost no information because they don't reflect genuine evaluation.

### What Extended Thinking Actually Does

Extended thinking modes (Claude's `ultrathink`, or chain-of-thought prompting for other models) force the model to:
1. Decompose the idea into constituent claims
2. Evaluate each claim against the specific codebase context
3. Consider implementation complexity, side effects, and interaction with existing systems
4. Identify specific technical risks and their likelihood
5. Compare against alternative approaches
6. Only THEN produce a score that summarizes this analysis

The thinking tokens are where the real evaluation happens. The output score is just the summary statistic. A score of 350 backed by 2000 tokens of technical reasoning is a fundamentally different object than a score of 350 backed by "this seems difficult."

### Impact on Cross-Scoring Quality

The ultrathink directive has its largest impact during Phase 5 (cross-scoring) because:
- The model is evaluating SOMEONE ELSE'S idea, so it has less default context
- Without thinking, it's tempted to skim and give a default-generous score
- With thinking, it actually works through the implications and produces differentiated scores
- The detailed reasoning becomes ammunition for the reveal and rebuttal phases

### Impact on Score Distribution

Without ultrathink, score distributions tend to be:
- Mean: ~620, Std Dev: ~120
- Most ideas cluster in 500-750 range
- Very few scores below 300 or above 850

With ultrathink, score distributions shift to:
- Mean: ~550, Std Dev: ~220
- Bimodal distribution: ideas cluster near 300-400 (clear rejects) and 700-850 (clear winners)
- Much more information in each score because the spread is wider

The bimodal distribution is what makes the adversarial dynamics work. Without it, there's not enough score variance to generate meaningful disagreements, and the reveal phase becomes a formality rather than a genuine update step.

---

## The Psychological Dynamics of the Reveal

Even though LLMs don't have psychology in the human sense, they exhibit consistent behavioral patterns under adversarial pressure that function like psychological dynamics. Understanding these patterns is essential for interpreting duel results correctly.

### Ego Defense

Models defend their own ideas more vigorously than they defend ideas they adopted from others. When a model proposed an idea and the opponent scored it 300, the model's rebuttal will be significantly more detailed and technical than when defending an idea it merely evaluated favorably. This is not sentience -- it's a training artifact where models learn that generating-then-defending is a coherent pattern, while adopting-then-defending is less rehearsed.

**Practical implication:** An idea that survives ego defense from its originator is somewhat validated. An idea that survives defense from a model that didn't originate it is STRONGLY validated, because the defender had to construct the defense from scratch rather than falling back on the generation context.

### Respect for Specificity

A score of 350 accompanied by a detailed technical critique ("this approach requires O(n^2) joins across the user table, which will degrade beyond 10K users and conflicts with the existing pagination strategy") gets taken seriously by the opposing model. The defender must address the specific technical claim or concede.

A score of 350 accompanied by vague dismissal ("this seems overcomplicated and unlikely to deliver value") gets counter-attacked. The defender correctly identifies that the low score isn't backed by substance and pushes back aggressively.

**Practical implication:** The quality of the cross-scoring reasoning matters more than the numeric score. When reviewing duel results, read the REASONING first and the score second.

### Concession Cascades

Once a model concedes that one of its ideas was weak, it becomes measurably more likely to concede on related ideas in the same response. This cascade effect means that the ORDER in which ideas are presented for re-evaluation can influence outcomes. The duel methodology partially mitigates this by presenting all scores simultaneously (in the reveal), but the cascade effect can still be observed within a single model's re-evaluation response.

**Practical implication:** If a model concedes on 3 of its 5 ideas, look carefully at the 2 it defended -- those are the ideas it genuinely believes in after accounting for the concession pressure.

### Anchoring

The first score a model sees for an idea influences its subsequent evaluation. This is why the methodology requires **simultaneous, independent scoring** (both agents score before either sees the other's scores). If Agent A scored first and Agent B saw those scores before scoring, Agent B's scores would be anchored toward Agent A's, destroying the decorrelation that makes cross-scoring valuable.

**Practical implication:** Any variation of the methodology that introduces sequential scoring (model A scores, then model B sees A's scores and scores) is fundamentally broken. The independence of Phase 5 scoring is non-negotiable.

### The Contrarian Impulse

Counterintuitively, when shown that an opponent AGREES with them (both scored an idea highly), models sometimes become MORE critical in the reveal phase. They start looking for problems they "should" have caught, reasoning that if the idea were truly as good as both scores suggest, there must be a catch they're both missing.

This contrarian impulse is actually useful -- it provides a final filter on consensus winners that catches "too good to be true" ideas that both models over-rated due to similar biases (the rare case where decorrelation fails because both models share the same blind spot).

**Practical implication:** If both models score an idea 800+ and then BOTH slightly downgrade it in the reveal phase, pay close attention to why. They may have independently identified a shared blind spot, which is extremely high-value information.

---

## Historical Analogues

The dueling wizards methodology is a modernized, automated version of several proven intellectual traditions. Understanding these analogues clarifies why the methodology works and what properties it inherits from each tradition.

### Adversarial Collaboration (Kahneman & Klein, 2009)

In their landmark paper, Daniel Kahneman and Gary Klein -- two researchers with fundamentally opposed views on expert intuition -- collaborated to identify **testable predictions that would distinguish their views**. Rather than debating in the abstract, they committed to specific, falsifiable claims.

The dueling wizards methodology does exactly this: when two models disagree on an idea's value, the rebuttal and steelman phases force them to identify specific, testable claims about why the idea will or won't work. The output isn't "model A thinks it's good and model B thinks it's bad" -- it's "model A predicts this will reduce latency by 40% while model B predicts it will introduce race conditions under concurrent load." Both predictions are testable.

### Red Team / Blue Team

Military and cybersecurity organizations routinely split teams into attackers (red) and defenders (blue). The red team's job is to find vulnerabilities; the blue team's job is to defend against attacks. Neither team has complete information, and the adversarial dynamic surfaces vulnerabilities that neither team would find alone.

In the dueling wizards methodology, both models play both roles simultaneously -- each is a red team for the opponent's ideas and a blue team for its own. The reveal phase forces role-switching: a model that attacked an idea must now steelman it, and a model that defended an idea must now consider the attack's merit.

### Dialectical Reasoning (Hegel)

The Hegelian dialectic -- thesis, antithesis, synthesis -- describes a process where an initial proposition (thesis) encounters its contradiction (antithesis), and the resolution (synthesis) transcends both by incorporating the valid elements of each while resolving the contradiction.

The duel follows this structure:
- **Thesis:** Model A's top ideas
- **Antithesis:** Model B's critical scoring of those ideas
- **Synthesis:** The reveal phase, where Model A integrates Model B's critique and produces a revised assessment that incorporates both the original insight and the opponent's objections

The synthesis phase (reveal + rebuttal + steelman) produces ideas that are strictly superior to either model's initial output because they've incorporated adversarial feedback.

### Peer Review

Scientific peer review sends a paper to independent experts who evaluate it without knowing each other's assessments. The independence prevents groupthink; the expertise ensures relevant critique; the anonymity (in double-blind review) prevents social dynamics from corrupting the signal.

The dueling wizards methodology is essentially automated double-blind peer review for ideas. Phase 5 (cross-scoring) is the independent review step; the reveal is the editor's synthesis of multiple reviews; and the rebuttal is the author response.

### Market Mechanisms

Markets aggregate distributed information through price discovery. When many independent agents with different information sets trade, the market price converges toward the true value. This is the core insight behind prediction markets and the efficient market hypothesis.

In the duel, the "market price" of an idea is its consensus score. When both models agree on a high score, the market has spoken -- the idea's value is well-estimated. When the models disagree, the market is illiquid and the true value is uncertain, which is itself valuable information (it tells you where more investigation is needed).

### The Synthesis

The dueling wizards methodology combines ALL of these traditions into a single automated pipeline:
- **Adversarial collaboration** -- models commit to testable predictions about ideas
- **Red/blue teaming** -- simultaneous attack and defense across all ideas
- **Dialectical reasoning** -- thesis/antithesis/synthesis structure across phases
- **Peer review** -- independent evaluation by qualified reviewers
- **Market mechanisms** -- consensus scores aggregate distributed information

This combination runs in 30-60 minutes and costs ~$7 in API calls. The equivalent human process (assemble a cross-functional team, brainstorm, critique, revise, synthesize) takes days of calendar time and thousands of dollars in opportunity cost. The dueling wizards methodology doesn't replace human judgment -- it provides adversarially-validated input TO human judgment, dramatically improving the quality of the decisions that humans then make.

---

## Operationalized Operators (Full Set)

The operator toolkit from `operationalizing-expertise` maps onto specific duel phases. Below is the comprehensive mapping, organized by the phase where each operator has its primary impact.

### Ideation Phase Operators (Phase 4)

**⊕ Cross-Domain: Automatic Cross-Pollination**

Different models naturally bring cross-domain perspectives by virtue of their different training data distributions. Claude tends to surface systemic and architectural patterns; GPT/Codex tends to surface implementation patterns and API-level optimizations; Gemini tends to surface user-facing and product-level considerations. The cross-domain operator is invoked automatically every time two different model families generate ideas for the same codebase -- no explicit prompting required.

When to watch for it: Look for ideas that reference analogies from other fields ("this is like connection pooling in databases, but for LLM API calls") -- these are the cross-domain operator firing and they tend to score well because they import proven patterns.

**∿ Dephase: Explicit Contrarian Generation**

The innovation mode prompts explicitly ask for "contrarian" and "unconventional" ideas. This invokes the dephase operator, which deliberately seeks ideas that are out of phase with conventional wisdom. Models that score poorly on a dephased idea aren't necessarily right -- they may be penalizing the idea for being unfamiliar rather than for being bad.

When to watch for it: Ideas prefaced with "this might seem counterintuitive, but..." or "against conventional practice..." are dephased ideas. Check whether the opponent's low score reflects genuine technical critique or mere unfamiliarity.

**◊ Paradox-Hunt: Contradiction as Beacon**

When two agents generate ideas that directly contradict each other (Agent A says "add caching" while Agent B says "remove the cache layer"), the contradiction is a paradox worth investigating. It usually means the two models are operating from different assumptions about the system's bottleneck, and resolving the paradox requires surfacing and testing those assumptions.

When to watch for it: Look at the full idea lists (not just the top 5) for direct contradictions between agents. These contradictions, when they occur in the winnowed top 5, produce the highest-information score gaps in Phase 5.

### Scoring Phase Operators (Phase 5)

**✂ Exclusion-Test: Hypothesis Killing via Low Scores**

When a model gives an idea a score below 400 with specific technical reasoning, it's performing an exclusion test -- articulating conditions under which the idea fails. These exclusion tests are the most efficient part of the pipeline: they kill ideas cheaply (a paragraph of critique) before expensive implementation reveals the same flaws.

When to watch for it: Read every score below 400 carefully. If the reasoning identifies a specific, verifiable failure condition ("this will break because X"), that's a strong exclusion test. If the reasoning is vague ("this doesn't seem practical"), the exclusion test is weak and the idea deserves defense in the rebuttal phase.

**⊞ Scale-Check: Implicit "Does This Matter at Scale?"**

The scoring criteria in the prompts include "potential impact" as a factor, which implicitly invokes the scale-check operator. Models evaluating ideas naturally consider whether an improvement matters at the system's current and projected scale. An optimization that saves 10ms per request matters at 1M requests/day; it's noise at 100 requests/day.

When to watch for it: Ideas that score well on technical merit but poorly on impact are often failing the scale check. The opponent's reasoning will typically include some form of "this is technically sound but the improvement is marginal given current usage patterns."

**🎭 Potency-Check: "Won't Work" vs. "Can't Work"**

This operator distinguishes between ideas that are impractical under current constraints ("won't work") and ideas that are fundamentally impossible ("can't work"). Models sometimes conflate these, scoring a merely difficult idea as if it were impossible. The potency check asks: if we removed all practical constraints (time, budget, staffing), would this idea work in principle?

When to watch for it: When an idea gets a low score, check whether the critique is about feasibility ("this would require rewriting the entire auth layer") or impossibility ("this violates the CAP theorem"). Feasibility concerns are negotiable; impossibility is not.

### Reveal Phase Operators (Phase 6, 6.5, 6.75)

**ΔE Exception-Quarantine: Contested Ideas Get Quarantined**

Ideas with score gaps exceeding 300 points are exceptions that deserve quarantine rather than immediate resolution. The exception-quarantine operator tags these ideas for special investigation: they're neither killed nor promoted but held in a contested state pending the rebuttal and steelman phases. The quarantine prevents premature convergence -- it would be just as wrong to kill a contested idea as to promote it without adversarial validation.

When to watch for it: The summary output after the reveal phase should clearly identify which ideas are in quarantine (contested) versus resolved (consensus win or consensus kill). If the summary doesn't distinguish these, the reveal phase didn't extract full value.

**† Theory-Kill: Consensus Kills Are Permanent**

When all models agree an idea is weak (both score below 400), the theory-kill operator fires. The idea is dead. No amount of subsequent enthusiasm can revive it without new evidence that wasn't available during the scoring phase. This is the most decisive operator in the pipeline: consensus kills are fast, cheap, and almost always correct because they require two decorrelated evaluators to independently identify weakness.

When to watch for it: The theory-kill should be celebrated, not mourned. Every consensus kill saved hours of implementation time on an idea that would have failed. Count the consensus kills as a measure of the duel's efficiency.

**⌂ Materialize: "If This Is Good, What Would We See?"**

The materialize operator forces concrete thinking about abstract ideas. During the reveal and rebuttal phases, when a model defends an idea, the strongest defenses include materialization: "if we implemented this, we would see [specific, measurable outcome]." This converts a vague "good idea" into a testable prediction.

When to watch for it: Defenses that include specific predictions ("this would reduce P95 latency by 30-50%", "this would eliminate the class of bugs caused by X") are materialized defenses and carry much more weight than abstract defenses ("this would improve the system's overall quality").

### Synthesis Phase Operators (Phase 6.9, Phase 8)

**≡ Invariant-Extract: What MUST Be True?**

After the adversarial phases resolve, the invariant-extract operator identifies conditions that must hold for the consensus winners to work as predicted. These invariants become the acceptance criteria for the resulting beads. If a consensus winner depends on the assumption that "database queries remain under 50ms," that invariant must be explicitly stated and tested.

When to watch for it: The best duel syntheses include explicit invariant statements for each consensus winner. If the synthesis says "implement X" without stating what must remain true for X to work, the invariant-extract operator wasn't fully invoked.

**⟂ Object-Transpose: Change WHAT, Not HOW**

The object-transpose operator asks: "could we solve this problem by changing what we're optimizing rather than how we're optimizing it?" This is a meta-level move that can unlock entirely new solution spaces. During the blind spot probe (Phase 6.9), this operator fires naturally because the probe is specifically looking for framings that both models missed.

When to watch for it: Blind spot ideas that reframe the problem ("instead of optimizing the search algorithm, what if we restructured the data so search isn't needed?") are object-transpositions. They're often the most valuable ideas in the entire duel output because they escape the local optimum that both models were exploring.

**👁 HAL (Have A Look): Read Before You Commit**

The HAL operator is a grounding check: before creating beads from consensus winners, actually read the relevant code sections. Models sometimes agree that an idea is brilliant based on their understanding of the codebase, but their understanding might be outdated or incomplete. The HAL operator says: "we both agree this is a great idea -- but let's actually look at the code it would modify before we commit to it."

When to watch for it: The bead creation phase (Phase 8) should include evidence that the model examined the specific files and functions that would be modified. Beads created without this grounding step carry higher implementation risk because they might be based on stale assumptions about the codebase's current state.
