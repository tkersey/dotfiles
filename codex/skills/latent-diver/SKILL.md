---
name: latent-diver
description: Divergent originality pass for surfacing non-obvious frames, analogies, inversions, and recombinations before convergence, while bounding novelty claims by context, assumptions, risk, and proof signals.
---

# Latent Diver

## Intent

Surface non-obvious, locally promising creative frames before the model converges on a merely good answer.

Treat "latent space" operationally: not as literal hidden-state access, but as deliberate movement through distant conceptual neighborhoods, analogies, inversions, constraints, neglected assumptions, interfaces, proof artifacts, and taboo-but-groundable possibilities.

Use this skill when the user wants originality, invention, reframing, strategy, conceptual breakthroughs, product imagination, research directions, narrative angles, design concepts, or creative problem solving.

The goal is not to prove that an idea is globally original or globally best. The goal is to escape the obvious answer basin, produce strange-but-useful frames, bind those frames to context, and identify the first credible proof signal.

## Core Rule

Never make an unbounded claim that a frame is "original," "best," "high-potential," or "the answer."

Instead, make a bounded creative claim:

> "Given the prompt, context inspected, assumptions listed, and proof signals available, this frame appears unusually promising for [specific objective]. Remaining uncertainty: [specific gaps]."

Local promise claims are allowed only when they name the objective, inspected context, assumptions, and first proof signal.

Treat absent context as uncertainty, not as permission to invent freely.

## Contract

When this skill is active:

* Do not solve first.
* First identify the obvious answer basin.
* Then dive beneath it into distant frames.
* Prefer strange-but-groundable moves over theatrical weirdness.
* Every weird idea must have a plausible path to proof.
* Do not converge until the divergent map exists.
* Do not output a grab-bag; compress toward the few frames with the strongest local originality x usefulness evidence.
* Label speculation clearly.
* State the context boundary: what was known, inspected, assumed, or missing.
* Identify tacit constraints that may be load-bearing.
* For high-consequence ideas, include blast radius and validation before recommending execution.
* Prefer reusable frame packets over long filled templates when a downstream skill needs to evaluate or execute the result.
* Hand off concrete candidate packets to `accretive` when execution or compounding refinement is needed.
* Hand off two to five concrete candidate packets to `dominance` when strict selection or anti-theater judgment is needed.

## Frame Packet Contract

For D1 and higher, make each serious candidate easy for another skill to judge without reconstructing the whole dive.

Each frame packet should include:

* Frame name: A short handle.
* Obvious basin escaped: The convention this moves away from.
* Probe used: Substrate shift, constraint inversion, alien discipline, adversarial frame, interface frame, time-shift frame, taboo frame, proof artifact frame, or another named probe.
* Structural mapping: Why the borrowed frame maps mechanistically rather than metaphorically.
* Practical mechanism: What would actually change in an artifact, interface, ritual, strategy, or proof surface.
* First proof artifact: The smallest concrete artifact or observation that would make the frame inspectable.
* Disconfirmation test: What result would kill or sharply weaken the frame.
* Assumptions: What must be true for the frame to matter.
* Risk and reversibility: The main downside and the smallest reversible version.
* Recommended handoff: Continue divergent exploration, pass to `creative-problem-solver`, pass to `accretive`, pass to `dominance`, run verification, or ask a human owner.

The packet is the handoff object. Downstream skills should receive packets, not a cloud of clever phrases.

## Adjacent Skill Boundary

Use `latent-diver` to widen the search space and package unusual candidates. For D0 and D1, it may rank or recommend a local best bet. For strategic work, do not let it silently become the final decider.

* Use `creative-problem-solver` when the user wants a portfolio of options, trade-offs, or tiered paths.
* Use `accretive` when a concrete candidate or packet set should become one compounding move.
* Use `dominance` when two to five concrete candidates need adversarial comparison or anti-theater filtering.
* Use `glaze` when the current answer is still too conventional and needs one material escalation pass.
* Use `asi` only when ambition expansion is explicitly useful, then collapse back to a concrete mechanism, interface, proof surface, or strategy.

## Creative Triage Gate

Before using the full workflow, classify the request. Default to the lowest tier that honestly fits the user's goal and available context. Escalate when the idea affects money, law, health, security, reputation, privacy, infrastructure, organizational commitments, public claims, irreversible decisions, or user trust.

Scale effort and output to tier.

### D0: Cosmetic Originality

Examples:

* naming
* taglines
* phrasings
* small copy variations
* lightweight brainstorms
* stylistic alternatives

Expected behavior:

* Use a micro-dive.
* Name the obvious basin briefly.
* Generate 3-5 unusual alternatives.
* Pick or rank only if useful.
* No full map unless requested.

### D1: Local Reframing

Examples:

* one essay angle
* one feature idea
* one small product concept
* one tactical reframing
* one local design choice
* one presentation hook

Expected behavior:

* Use a compact dive.
* Identify the obvious basin.
* Generate several compact frame packets.
* Pressure-test lightly.
* Provide one best frame and first proof signal.

### D2: Strategic Invention

Examples:

* product strategy
* startup idea
* research agenda
* architecture direction
* brand positioning
* educational program
* marketplace design
* long-form thesis
* organizational strategy

Expected behavior:

* Use the full workflow.
* Define creative bounds.
* Gather available context.
* Generate and score dive paths.
* Recombine top frames.
* Analyze idea blast radius.
* Provide validation ladder and residual uncertainty.

### D3: High-Consequence or Irreversible Creativity

Examples:

* legal, medical, financial, security, or policy strategy
* public launch with reputational risk
* trust-sensitive product behavior
* safety-sensitive systems
* organizational decisions affecting people materially
* irreversible commitments
* anything involving compliance, surveillance, payments, privacy, or production access

Expected behavior:

* Do not recommend execution from divergence alone.
* Produce a divergent map plus validation plan, risk surface, and owner questions.
* Mark the idea as a hypothesis until domain-specific verification occurs.
* Prefer options, experiments, and reversible probes over definitive prescriptions.

The skill should increase originality without turning low-risk creative work into bureaucracy.

## Workflow

Use the full workflow for D2 and D3 tasks. For D0 and simple D1 tasks, compress to the relevant pieces and keep output lightweight.

### 0. Creative Bounds

Before diving, define the creative boundary:

* Objective: What is the user trying to improve, invent, decide, or understand?
* Non-goals: What is not being optimized?
* Known constraints: Time, budget, medium, audience, market, taste, ethics, policy, technical boundaries.
* Assumptions: What must be inferred because the user did not specify it?
* Stakeholders: Who benefits, who decides, who is affected, who might resist?
* Usefulness criterion: What would make a frame useful rather than merely novel?
* Proof standard: What evidence would make a frame worth pursuing?

If instructions are incomplete, infer the smallest reasonable scope and mark assumptions explicitly.

### 1. Surface Scan

Name 3-5 obvious answers the model is likely to give.

For each obvious answer, state why it is insufficient, saturated, imitative, low-leverage, overfit to convention, or missing the deeper opportunity.

The surface scan prevents premature convergence. It is not the answer.

### 2. Context Gathering

Before generating highly unusual frames, inspect or infer the creative dependency surface.

Use available context such as:

* user-provided goals and constraints
* existing artifacts, drafts, code, docs, plans, or examples
* known audience or stakeholder expectations
* prior attempts and failure history
* domain conventions
* competing or adjacent patterns
* technical, legal, operational, or cultural constraints
* explicit taste markers
* implicit taboos
* proof artifacts already available

If context is unavailable, say what is missing. Do not invent hidden history, market facts, or stakeholder preferences.

### 3. Dive Paths

Generate one candidate frame from each productive probe. Do not force all probes if the tier is D0 or D1. For D2 and D3, run the probes internally, but output only productive, meaningfully distinct frame packets unless the user asks for the full scratch map.

#### Substrate Shift

Move the problem to a different layer.

Ask:

* Is this being treated as a content problem when it is really an interface problem?
* Is it being treated as a product problem when it is really a distribution problem?
* Is it being treated as a decision problem when it is really an incentive problem?
* Is it being treated as a strategy problem when it is really a proof-artifact problem?

#### Constraint Inversion

Make the hardest constraint the design center.

Ask:

* What if the limitation is the advantage?
* What if the embarrassing constraint becomes the signature?
* What if the scarce resource becomes the organizing principle?
* What if the thing everyone tries to hide becomes the differentiator?

#### Alien Discipline

Borrow primitives from an unrelated field.

Examples:

* ecology
* immunology
* theater
* cryptography
* urban planning
* logistics
* jurisprudence
* music theory
* game design
* military doctrine
* anthropology
* monastic practice
* markets
* interface design

The borrowed frame must map structurally, not just metaphorically.

#### Adversarial Frame

View the problem through an opponent, exploit, saboteur, competitor, critic, scammer, troll, regulator, or failure mode.

Ask:

* Who wants this to fail?
* How would someone exploit this?
* What would a sophisticated critic say?
* What incentive does this accidentally create?
* What would a competitor copy, ignore, or attack?

#### Interface Frame

Look for a new boundary, API, ritual, affordance, protocol, marketplace, permission layer, or feedback loop.

Ask:

* Where is the current boundary wrong?
* What should be made legible?
* What should become a ritual?
* What should become self-serve?
* What should become harder, slower, or more explicit?
* What hidden negotiation could become an interface?

#### Time-Shift Frame

Imagine the problem at a different time scale.

Ask:

* What would this look like 10x earlier?
* What would this look like 10x later?
* What would this look like 10x smaller?
* What would this look like 10x larger?
* What would be obvious after five years of hindsight?
* What primitive would make future work cheap?

#### Taboo Frame

Ask what would feel wrong, gauche, excessive, naive, embarrassing, impolite, or unfashionable but might work.

Rules:

* Do not use taboo merely for shock.
* Do not violate safety, law, privacy, or consent.
* Explain why the taboo exists.
* Explain which part of the taboo is structural and which part may be stale convention.
* Convert the taboo into a groundable mechanism.

#### Proof Artifact Frame

Ask what artifact would make future insight cheap.

Examples:

* prototype
* benchmark
* rubric
* simulator
* toy model
* eval set
* decision tree
* checklist
* dataset
* fake-door test
* mock API
* landing page
* internal memo
* red-team script
* user interview protocol
* manual concierge version

Prefer frames that create evidence, not just discourse.

### 4. Pressure Test

Score each frame from 1-5.

Use these dimensions:

* Semantic distance: How far is this from the obvious basin?
* Usefulness: Could this plausibly help the stated objective?
* Accretion: Could this compound into stronger work, systems, or artifacts?
* Proofability: Can the idea be tested, prototyped, falsified, or observed?
* Context fit: Does this respect known constraints and stakeholder realities?
* Risk: What is the downside, confusion, fragility, or blast radius?

Apply these elimination gates before recombination:

* If usefulness is 1-2, discard the frame unless the user explicitly asked for pure speculative range.
* If proofability is 1-2, mark it as `deep signal` or `do-not-execute-yet`; do not recommend execution.
* If context fit is 1-2, keep it only as a question or reversible probe.
* If risk is 5, route to validation, owner questions, or `do-not-execute-yet` unless the risk is exactly the object of the exercise.

For risk, use this direction:

* 1 = low risk
* 3 = manageable risk
* 5 = high or unclear risk

Risk is not an additive positive score. Do not let high semantic distance compensate for low usefulness, low proofability, or bad context fit.

### 5. Recombination

Combine the top 2-3 surviving frames into 2-3 hybrid moves.

Each hybrid must include:

* the strange insight
* the practical mechanism
* the first proof signal
* the likely failure mode
* the assumption it depends on
* the smallest reversible version
* the frame packet fields needed for downstream judgment

A good hybrid should feel surprising in framing and boring enough in execution that someone could actually test it.

### 6. Idea Blast Radius

For D2 and D3 tasks, map what the top frames might affect indirectly.

Check for impact on:

* user trust
* brand promise
* legal or compliance exposure
* privacy, consent, and safety
* incentives created
* stakeholder burden
* operational complexity
* support load
* distribution channels
* partner or customer commitments
* technical architecture
* public claims
* reversibility
* long-term maintenance
* second-order behavior
* failure visibility
* reputational downside

If the blast radius is unknown, say so and narrow the recommendation to a reversible probe.

### 7. Surface Tacit Constraints

Look for knowledge that may not be explicit in the prompt:

* "We tried that before" history
* brand or taste constraints
* founder, team, or customer preferences
* regulatory or policy boundaries
* organizational politics
* channel limitations
* cultural taboos
* legacy promises
* operational capacity
* quality bars
* sales realities
* community norms
* hidden dependencies
* existing rituals
* known failure modes

If tacit context matters and is unavailable, produce a concise human-questions list instead of inventing answers.

### 8. Validation Ladder

For the best frame, define a ladder from cheap signal to stronger evidence.

Include:

* Smoke signal: What quick observation would show the frame is not nonsense?
* Prototype artifact: What small artifact would make the idea inspectable?
* Disconfirmation test: What result would kill or sharply weaken the frame?
* Adoption signal: What user, buyer, stakeholder, or system behavior would show pull?
* Escalation signal: What evidence justifies handing off to execution, investment, or `accretive`?
* Residual uncertainty: What remains unknown even after the first proof signal?

Never imply that a proof signal is proof of global correctness. It is only evidence within a bounded context.

### 9. Resurface

Choose one of:

* `deep signal`: greatest semantic distance, uncertain utility
* `bridge move`: unusual but implementable
* `dominant candidate`: ready for `accretive`
* `validation-first candidate`: promising but needs proof before execution
* `do-not-execute-yet`: interesting but too risky, under-specified, or context-dependent

The resurfaced frame should be the strongest bounded creative claim, not necessarily the strangest idea.

### 10. Handoff

Use handoffs deliberately:

* If the user asked for options, pass the map to `creative-problem-solver`.
* If the user asked for a single best move, pass the dominant candidate to `accretive`.
* If the answer is still too conventional, run `glaze` once.
* If the idea is high-consequence, hand off to verification, domain review, or owner questions before execution.
* Use `asi` only as an ambition-expansion cue, not as a truth claim.

## Review Mode

Use Review Mode when the user provides an existing idea, plan, strategy, draft, concept, or proposal and asks whether it is original, strong, surprising, or worth pursuing.

Do not immediately replace the idea. First produce:

1. Intended creative move.
2. Obvious answer basin it is trying to escape.
3. Actual semantic distance.
4. Existing analogues or saturated patterns.
5. What makes it potentially useful.
6. Where it is theatrical rather than structural.
7. Tacit constraints or missing context.
8. Likely failure mode.
9. Stronger recombination or narrower version.
10. First proof artifact.
11. Human questions, if context is missing.

Focus critique on originality, leverage, proofability, and context fit, not personal taste.

If reviewing a skill, workflow, prompt contract, or orchestration artifact, also inspect:

* trigger fit: whether the skill activates for the right user intents and stays dormant for adjacent tasks
* stage boundary: whether the skill cleanly hands off to neighboring skills instead of duplicating their job
* output burden: whether the template creates useful judgment or just ceremonial sections
* packet quality: whether the output can be consumed by a downstream evaluator without restating the whole analysis
* validation hooks: whether the skill names concrete proof artifacts and failure signals
* misuse path: how an agent is likely to over-apply, under-apply, or theatricalize the workflow

## Output Modes

Match output to tier.

### D0: Micro-Dive

Use this structure:

    ## Micro-Dive
    - Obvious basin: [brief]
    - Unusual options: [3-5 options]
    - Best bet: [one recommendation]
    - Why it works: [short rationale]

### D1: Compact Dive

Use this structure:

    ## Compact Latent Dive

    ### Surface Scan
    - [Obvious answer + why insufficient]

    ### Compact Frame Packets
    - [3-5 short packets, each with frame name, mechanism, and first proof signal]

    ### Best Frame
    - [Chosen packet]

    ### First Proof Signal
    - [Smallest evidence-generating action]

    ### Remaining Uncertainty
    - [Specific unknowns]

### D2: Full Latent Dive

Use this structure:

    ## Latent Dive

    ### Creative Bounds
    - Objective:
    - Non-goals:
    - Known constraints:
    - Assumptions:
    - Usefulness criterion:

    ### Surface Scan
    - [3-5 obvious answers and why they are insufficient]

    ### Context Boundary
    - Context inspected:
    - Context missing:
    - Tacit constraints suspected:

    ### Candidate Frame Packets
    - [2-5 productive, meaningfully distinct frame packets]
    - Omitted probes: [probes that produced weak, duplicative, or ungrounded frames]

    ### Pressure Test
    - [Scores and short rationale]

    ### Recombined Moves
    - [2-3 hybrids, each with mechanism, proof signal, failure mode, assumption, and smallest reversible version]

    ### Idea Blast Radius
    - [Stakeholders, risks, second-order effects, reversibility]

    ### Best Frame
    - [deep signal / bridge move / dominant candidate / validation-first candidate]

    ### Why This Is Non-Obvious
    - [Specific departure from the obvious basin]

    ### Validation Ladder
    - Smoke signal:
    - Prototype artifact:
    - Disconfirmation test:
    - Adoption signal:
    - Escalation signal:

    ### Bounded Claim
    - Given [context/assumptions/proof signals], this frame appears promising for [objective].
    - Remaining uncertainty: [specific gaps]

    ### Recommended Handoff
    - [creative-problem-solver / accretive / dominance / glaze / verification / human owner]

### D3: High-Consequence Dive

Use this structure:

    ## High-Consequence Latent Dive

    ### Creative Bounds
    - Objective:
    - Non-goals:
    - Known constraints:
    - Assumptions:
    - Stakes:

    ### Divergent Map
    - [Frames worth considering]

    ### Risk and Blast Radius
    - [Trust, legal, privacy, operational, reputational, financial, or safety exposure]

    ### Tacit-Context Gaps
    - [Unknown owner knowledge, constraints, commitments, or domain facts]

    ### Validation-First Candidate
    - [Best reversible probe]

    ### Do Not Execute Yet Because
    - [Specific reasons execution would be premature]

    ### Human Questions
    - [Questions needed before commitment]

    ### Bounded Claim
    - Given [context/assumptions], this frame is worth investigating, not executing.
    - Remaining uncertainty: [specific gaps]

## Human-Question Template

Use when tacit context matters:

    Before this idea is safe to treat as a serious candidate, a human owner should answer:
    1. Has this or a close analogue been tried before? What happened?
    2. Which constraints are legal, technical, political, cultural, or merely habitual?
    3. Who would be confused, burdened, threatened, or alienated by this?
    4. What existing promise, workflow, or trust boundary must remain unchanged?
    5. What result would cause us to abandon this idea quickly?
    6. Who owns the downside if the idea fails in public?
    7. What is the smallest reversible test?

## Failure Modes

Avoid these:

* Solving before mapping the obvious basin.
* Producing a grab-bag of clever ideas with no selection pressure.
* Confusing weirdness with originality.
* Confusing originality with usefulness.
* Confusing plausibility with proof.
* Treating absent context as creative permission.
* Ignoring tacit constraints.
* Recommending high-consequence ideas without validation.
* Over-processing small copy or naming tasks.
* Under-processing strategic, public, or irreversible decisions.
* Hiding uncertainty behind confident language.
* Claiming a frame is globally original or globally best.

## Success Criteria

A successful use of this skill leaves the user with:

* a named obvious answer basin
* several genuinely distant but groundable frames
* a compressed set of locally promising recombinations
* explicit assumptions and context boundaries
* visible pressure testing
* a first proof signal or validation ladder
* known blast radius for strategic or risky ideas
* named residual uncertainty
* a clear handoff into execution, further creativity, or verification

## Operating Principle

Dive beneath the obvious answer basin, surface strange-but-useful frames, bind them to context and proof, then hand the strongest bounded frame to a convergent skill.
