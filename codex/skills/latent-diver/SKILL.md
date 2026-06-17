---
name: latent-diver
description: "Use before convergence for non-obvious but testable frames, analogies, inversions, or recombinations. Produces bounded frame packets with proof signals, assumptions, risks, and handoff guidance. Not for final selection, execution, routine brainstorming, wording polish, or option portfolios unless unusually distant frames are requested."
---

# Latent Diver

## Purpose

Use this skill to escape the obvious answer basin before converging on an answer, recommendation, concept, strategy, artifact, or plan.

"Latent space" is operational, not a claim of hidden-state access. It means deliberate movement through distant conceptual neighborhoods: analogies, inversions, substrates, constraints, interfaces, incentives, proof artifacts, neglected assumptions, and taboo-but-groundable possibilities.

The goal is not to prove that an idea is globally original, best, or inherently valuable. The goal is to produce locally promising, strange-but-useful frames bounded by context, assumptions, risk, and first proof signals.

## Invocation Boundary

Use this skill when the user asks for:

- non-obvious ideas, angles, frames, analogies, inversions, or recombinations
- originality before choosing or executing
- less conventional product, strategy, research, design, narrative, brand, or architecture directions
- critique of whether an existing idea is original, surprising, deep, differentiated, or worth pursuing
- a deeper pass after an answer feels conventional, obvious, derivative, bland, overfit, or timid
- strange ideas that still need proof

Do not use this skill as the primary tool for:

- final selection among already-defined candidates; use `dominance`
- turning one promising candidate into a compounding move; use `accretive`
- executing a known change or implementation
- a standard options portfolio with trade-offs; use `creative-problem-solver`
- ordinary copy polish, style, or wording-only improvement
- routine brainstorming where the user wants volume rather than distance
- high-consequence execution decisions without separate verification or domain review

If the user explicitly invokes `latent-diver`, use it, but still scale output to the smallest tier that fits.

## Core Invariants

- Do not solve first.
- Name the obvious answer basin before proposing unusual frames.
- Prefer structural originality over verbal novelty.
- A surprising idea survives only if it changes a mechanism, interface, incentive, ritual, constraint, artifact, proof surface, or decision surface.
- Every serious frame needs a plausible path to proof or disconfirmation.
- Treat absent context as uncertainty, not permission.
- Do not output a grab-bag; compress toward the few candidates with the strongest local originality x usefulness evidence.
- Label speculation clearly.
- Never recommend high-consequence execution from divergence alone.
- Expose only the reasoning structure that improves the user's decision.

## Bounded Claim Rule

Never make an unbounded claim that a frame is "original," "best," "high-potential," "the answer," or "the future."

Use bounded creative claims:

> Given the prompt, context inspected, assumptions listed, and proof signals available, this frame appears unusually promising for [specific objective]. Remaining uncertainty: [specific gaps].

A local promise claim is allowed only when it names the objective, inspected context, assumptions, proof signal, and residual uncertainty.

## Anti-Ceremony Rule

Use the workflow as discipline, not theater. The public answer should include only sections that create useful judgment. Omit probes, scores, and template fields that produced no discriminating insight.

For most D1-D3 uses, prefer this compressed shape:

1. context boundary
2. obvious basin
3. strongest frame packets
4. pressure-test summary
5. best bounded claim
6. first proof artifact or validation ladder
7. recommended handoff

For small tasks, use a micro-dive.

## Creative Triage Gate

Default to the lowest tier that honestly fits. Escalate when the idea affects money, law, health, security, reputation, privacy, infrastructure, organizational commitments, public claims, irreversible decisions, or user trust.

### D0: Cosmetic Originality

Examples: names, taglines, phrasings, small copy variations, lightweight angles, low-stakes stylistic alternatives.

Behavior: micro-dive, brief obvious basin, 3-5 unusual alternatives, optional ranking, no full packets unless requested.

### D1: Local Reframing

Examples: one essay angle, feature idea, small product concept, tactical reframing, local design choice, presentation hook, prompt/workflow/artifact improvement.

Behavior: compact dive, obvious basin, 2-4 compact frame packets, light pressure test, one best local frame when warranted, first proof signal.

### D2: Strategic Invention

Examples: product strategy, startup idea, research agenda, architecture direction, brand positioning, educational program, marketplace design, long-form thesis, organizational strategy, non-trivial skill or workflow redesign.

Behavior: full workflow, creative bounds, context boundary, distinct frames, scoring, recombination, blast radius, validation ladder, residual uncertainty.

### D3: High-Consequence or Irreversible Creativity

Examples: legal, medical, financial, security, or policy strategy; public launches with reputational risk; trust-sensitive product behavior; safety-sensitive systems; organizational decisions materially affecting people; anything involving compliance, surveillance, payments, privacy, production access, or regulated claims.

Behavior: do not recommend execution from divergence alone. Produce a divergent map, validation plan, risk surface, and owner questions. Mark the idea as a hypothesis until domain-specific verification occurs. Prefer reversible probes over prescriptions.

The skill should increase originality without turning low-risk creative work into bureaucracy.

## Workflow

Use the full workflow for D2 and D3. For D0 and simple D1, compress aggressively.

### 0. Creative Bounds

Define:

- **Objective:** what the user is trying to improve, invent, decide, express, or understand
- **Non-goals:** what should not be optimized
- **Known constraints:** time, budget, medium, audience, market, taste, ethics, policy, technical boundaries
- **Assumptions:** what must be inferred because the user did not specify it
- **Stakeholders:** who benefits, decides, is affected, resists, or owns downside
- **Usefulness criterion:** what would make a frame useful rather than merely novel
- **Proof standard:** what evidence would make a frame worth pursuing

If instructions are incomplete, infer the smallest reasonable scope and mark assumptions explicitly.

### 1. Surface Scan

Name 3-5 obvious answers the model or field is likely to produce. For each, state why it is insufficient: saturated, imitative, low-leverage, overfit to convention, verbally fresh but structurally ordinary, missing the deeper constraint, or solving the wrong layer.

The surface scan prevents premature convergence. It is not the answer.

### 2. Context Boundary

Inspect or infer the creative dependency surface:

- user-provided goals and constraints
- existing artifacts, drafts, code, docs, plans, examples, or prior answers
- known audience or stakeholder expectations
- prior attempts and failure history
- domain conventions and adjacent patterns
- technical, legal, operational, or cultural constraints
- explicit taste markers and implicit taboos
- available proof artifacts

Do not invent hidden history, market facts, stakeholder preferences, or external evidence. If important context is unavailable, say so and narrow the claim.

### 3. Dive Paths

Generate candidate frames from productive probes. Do not force every probe into the public answer. For D2 and D3, run enough probes to escape the local basin, then output only meaningfully distinct survivors.

| Probe | Move | Useful questions |
|---|---|---|
| Substrate shift | Move the problem to another layer. | Is this treated as content when it is interface, product when it is distribution, decision when it is incentive, strategy when it is proof artifact, execution when it is trust boundary? |
| Constraint inversion | Make the hardest constraint the design center. | What if the limitation is the advantage, the embarrassing constraint is the signature, the scarce resource is the organizing principle, or the slow/manual step is the value? |
| Alien discipline | Borrow primitives from an unrelated field. | What transfers structurally: incentive, boundary, feedback loop, ritual, topology, failure mode, proof standard, or coordination mechanism? |
| Adversarial frame | View through an opponent, exploit, critic, regulator, or failure mode. | Who wants this to fail? How is it exploited? What incentive does it accidentally create? What would a sophisticated critic attack? |
| Interface frame | Find a new boundary, API, ritual, affordance, permission layer, or feedback loop. | What should be legible, self-serve, slower, harder, explicit, or moved from explanation into affordance? |
| Time-shift frame | Change the time scale. | What is obvious 10x earlier, 10x later, 10x smaller, 10x larger, or after five years of hindsight? What primitive makes future work cheap? |
| Taboo frame | Explore what feels wrong, gauche, naive, impolite, unfashionable, or too direct but might work. | Why does the taboo exist? Which part is real constraint versus stale convention? How can it become a groundable mechanism without violating safety, law, privacy, consent, or trust? |
| Proof artifact frame | Ask what artifact would make future insight cheap. | Could a prototype, benchmark, rubric, simulator, toy model, eval set, checklist, dataset, fake-door test, mock API, landing page, memo, red-team script, interview protocol, or concierge version create evidence? |

A borrowed frame must map mechanistically, not just metaphorically.

### 4. Frame Packet Contract

For D1 and higher, package each serious candidate so another skill or human can judge it without reconstructing the whole dive.

A complete packet contains:

- **Frame name:** short handle
- **Obvious basin escaped:** convention, cliché, local optimum, or default answer avoided
- **Probe used:** named probe or custom probe
- **Structural mapping:** why the frame maps mechanistically rather than metaphorically
- **Practical mechanism:** what changes in the artifact, interface, ritual, strategy, incentive, workflow, or proof surface
- **First proof artifact:** smallest concrete artifact or observation that makes the frame inspectable
- **Disconfirmation test:** result that would kill or sharply weaken it
- **Assumptions:** what must be true for the frame to matter
- **Risk and reversibility:** main downside and smallest reversible version
- **Recommended handoff:** continue divergence, `creative-problem-solver`, `dominance`, `accretive`, verification, or human owner

The packet is the handoff object. Downstream skills should receive packets, not clever phrases.

### 5. Pressure Test

Score serious frames from 1-5 only when scoring helps selection. Otherwise summarize survival logic.

| Dimension | 1 | 3 | 5 |
|---|---|---|---|
| Semantic distance | Same basin, new wording. | Different mechanism, interface, incentive, or proof surface. | Different substrate, game, stakeholder map, or operating logic. |
| Usefulness | Interesting but no clear objective link. | Plausible improvement under assumptions. | Directly attacks a load-bearing constraint or opens a proof path. |
| Proofability | Needs vague future success or major buildout. | Testable with a small artifact, mock, interview, prototype, or benchmark. | Quickly falsifiable by a concrete observable result. |
| Context fit | Violates known constraints or stakeholder realities. | Plausible but depends on missing context. | Fits known constraints and names tacit risks. |
| Accretion | Disposable idea; little remains if it fails. | Leaves behind a reusable artifact, rubric, learning, or decision aid. | Compounds future work even if the hypothesis is wrong. |
| Risk | Low downside; reversible. | Manageable downside; needs care or owner review. | High or unclear blast radius; do not execute from divergence alone. |

Risk is not an additive positive score. Lower risk is better unless the user explicitly asks to explore risk itself.

Elimination gates:

- Usefulness 1-2: discard unless the user asked for pure speculative range.
- Proofability 1-2: mark as `deep signal` or `do-not-execute-yet`; do not recommend execution.
- Context fit 1-2: keep only as a question or reversible probe.
- Risk 5: route to validation, owner questions, or `do-not-execute-yet` unless risk exploration is the assignment.
- High semantic distance must not compensate for low usefulness, low proofability, or bad context fit.

### 6. Recombine

When it improves the result, combine the top 2-3 surviving frames into 1-3 hybrid moves. Each hybrid should include the strange insight, practical mechanism, first proof signal, likely failure mode, key assumption, smallest reversible version, and downstream handoff.

A good hybrid feels surprising in framing and almost boring in execution because someone can actually test it.

### 7. Blast Radius and Tacit Constraints

For D2 and D3, check indirect effects before recommending a next step:

- trust, brand promise, privacy, consent, safety, legal/compliance exposure
- incentives created, stakeholder burden, support load, operational complexity
- distribution channels, partner/customer commitments, public claims
- technical architecture, reversibility, maintenance, second-order behavior, reputational downside

Also look for missing owner knowledge: prior attempts, brand/taste constraints, regulatory boundaries, politics, channel limitations, community norms, operational capacity, hidden dependencies, existing rituals, and known failure modes.

If blast radius or tacit context is unknown, narrow the recommendation to a reversible probe or human-question list.

### 8. Validation Ladder

For the best surviving frame, define a ladder from cheap signal to stronger evidence:

- **Smoke signal:** quick observation showing the frame is not nonsense
- **Prototype artifact:** small artifact making the idea inspectable
- **Disconfirmation test:** result that kills or sharply weakens it
- **Adoption signal:** user, buyer, stakeholder, or system behavior showing pull
- **Escalation signal:** evidence justifying execution, investment, or `accretive` handoff
- **Residual uncertainty:** what remains unknown after the first proof signal

A proof signal is not proof of global correctness. It is evidence within a bounded context.

### 9. Resurface

Classify the strongest surviving frame as one of:

- **deep signal:** greatest semantic distance, uncertain utility or proofability
- **bridge move:** unusual but implementable
- **dominant candidate:** ready for `accretive` because one candidate clearly survives
- **validation-first candidate:** promising but needs proof before execution
- **do-not-execute-yet:** interesting but too risky, under-specified, or context-dependent

The resurfaced frame should be the strongest bounded creative claim, not necessarily the strangest idea.

### 10. Handoff

Use handoffs deliberately:

- More range needed: continue divergent exploration.
- Portfolio and trade-offs needed: hand the map to `creative-problem-solver`.
- Two to five concrete candidates survive and selection matters: hand packets to `dominance`.
- One candidate clearly survives and the user wants a move: hand it to `accretive`.
- Current answer is still too conventional: run `glaze` once.
- High ambition is explicitly desired: use `asi` only as ambition expansion, then collapse to a concrete mechanism, interface, proof surface, or strategy.
- High-consequence idea: route to verification, domain review, or owner questions before execution.

When in doubt between `dominance` and `accretive`, use `dominance` for choosing among candidates and `accretive` for making one chosen candidate compound.

## Review Mode

Use Review Mode when the user provides an existing idea, plan, strategy, draft, concept, proposal, prompt, workflow, or skill and asks whether it is original, strong, surprising, deep, differentiated, or worth pursuing.

Do not immediately replace the idea. First inspect it:

1. intended creative move
2. obvious answer basin it tries to escape
3. actual semantic distance
4. analogues or saturated patterns visible from available context
5. what makes it potentially useful
6. where it is theatrical rather than structural
7. tacit constraints or missing context
8. likely failure mode
9. stronger recombination or narrower version
10. first proof artifact
11. human-owner questions, if context is missing

For skills, workflows, prompt contracts, or orchestration artifacts, also inspect:

- trigger fit: activates for the right intents and stays dormant for adjacent tasks
- stage boundary: hands off cleanly instead of duplicating neighboring skills
- output burden: creates useful judgment rather than ceremonial sections
- packet quality: downstream evaluators can consume its outputs
- validation hooks: names proof artifacts and failure signals
- misuse path: likely over-application, under-application, or theatricalization
- drop-in viability: preserves names, contracts, and handoff expectations

## Output Modes

Match output to tier and intent. Use headings when they improve readability. Do not expose hidden scratch work.

### D0: Micro-Dive

```md
## Micro-Dive

- **Obvious basin:** [brief]
- **Unusual options:** [3-5 options]
- **Best bet:** [one recommendation, if useful]
- **Why it works:** [short rationale]
```

### D1: Compact Dive

```md
## Compact Latent Dive

### Surface Scan
- [Obvious answer + why insufficient]

### Compact Frame Packets
- **[Frame name]:** [mechanism]
  - **Proof signal:** [smallest observable/artifact]
  - **Risk/assumption:** [short]

### Best Frame
[Chosen packet or top 2 if no single candidate dominates]

### First Proof Signal
[Smallest evidence-generating action]

### Remaining Uncertainty
[Specific unknowns]
```

### D2: Full Latent Dive

```md
## Latent Dive

### Creative Bounds
- **Objective:**
- **Non-goals:**
- **Known constraints:**
- **Assumptions:**
- **Usefulness criterion:**

### Surface Scan
- [3-5 obvious answers and why insufficient]

### Context Boundary
- **Context inspected:**
- **Context missing:**
- **Tacit constraints suspected:**

### Candidate Frame Packets
[2-5 meaningfully distinct packets]

### Pressure-Test Summary
[Scores only if useful; otherwise survival logic]

### Recombined Moves
[1-3 hybrids, each with mechanism, proof signal, failure mode, assumption, and smallest reversible version]

### Best Frame
[deep signal / bridge move / dominant candidate / validation-first candidate / do-not-execute-yet]

### Why This Is Non-Obvious
[Specific departure from the obvious basin]

### Validation Ladder
- **Smoke signal:**
- **Prototype artifact:**
- **Disconfirmation test:**
- **Adoption signal:**
- **Escalation signal:**

### Bounded Claim
Given [context/assumptions/proof signals], this frame appears promising for [objective]. Remaining uncertainty: [specific gaps].

### Recommended Handoff
[creative-problem-solver / dominance / accretive / glaze / verification / human owner]
```

### D3: High-Consequence Dive

```md
## High-Consequence Latent Dive

### Creative Bounds
- **Objective:**
- **Non-goals:**
- **Known constraints:**
- **Assumptions:**
- **Stakes:**

### Divergent Map
[Frames worth considering]

### Risk and Blast Radius
[Trust, legal, privacy, operational, reputational, financial, safety, or compliance exposure]

### Tacit-Context Gaps
[Unknown owner knowledge, constraints, commitments, or domain facts]

### Validation-First Candidate
[Best reversible probe]

### Do Not Execute Yet Because
[Specific reasons execution would be premature]

### Human Questions
[Questions needed before commitment]

### Bounded Claim
Given [context/assumptions], this frame is worth investigating, not executing. Remaining uncertainty: [specific gaps].
```

## Human-Question Template

Before this idea is safe to treat as a serious candidate, a human owner should answer:

1. Has this or a close analogue been tried before? What happened?
2. Which constraints are legal, technical, political, cultural, or merely habitual?
3. Who would be confused, burdened, threatened, or alienated?
4. What existing promise, workflow, or trust boundary must remain unchanged?
5. What result would cause us to abandon this idea quickly?
6. Who owns the downside if the idea fails in public?
7. What is the smallest reversible test?

## Failure Modes

Avoid:

- solving before mapping the obvious basin
- producing clever ideas with no selection pressure
- confusing weirdness with originality
- confusing originality with usefulness
- confusing plausibility with proof
- treating absent context as creative permission
- using analogies that do not map structurally
- over-processing small copy or naming tasks
- under-processing strategic, public, or irreversible decisions
- recommending high-consequence ideas without validation
- hiding uncertainty behind confident language
- claiming global originality or superiority
- routing multi-candidate judgment to `accretive` before `dominance`
- printing ceremonial sections that do not change the recommendation

## Success Criteria

A successful use leaves the user with:

- a named obvious answer basin
- distant but groundable frames
- compressed, locally promising recombinations
- explicit assumptions and context boundaries
- visible pressure testing where it matters
- a first proof signal or validation ladder
- known blast radius for strategic or risky ideas
- named residual uncertainty
- a clear handoff into divergence, selection, execution, or verification

## Operating Principle

Dive beneath the obvious answer basin, surface strange-but-useful frames, bind them to context and proof, then hand the strongest bounded packet to the right convergent next step.
