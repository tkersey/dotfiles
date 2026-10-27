---
name: codebase-doctrine
description: "Derive or refresh durable, evidence-backed repository doctrine, including correctness atlases, doctrine audits, task-context projections, and repository-skill recommendations. Not quick onboarding, ordinary implementation, or generic review."
metadata:
  version: "3.0.0"
  activation_cost: high
  default_depth: standard
---

# Codebase Doctrine

## Mission

Recover the repository's **latent constitution** and render the smallest context
that will materially improve a named future consumer's decisions.

```text
repository evidence
-> rival explanations
-> selection pressures
-> authorities, laws, freedoms, wounds, proof, and aporia
-> exact consumer context
```

The result is not a schema-shaped inventory of everything discovered. It is the
smallest explanatory basis that changes what a future maintainer or agent will
inspect, preserve, reject, change freely, or prove.

## Activation boundary

Use when the request combines deep repository understanding with durable
correctness doctrine, a correctness atlas, authority/law/failure/proof analysis,
doctrine refresh, an audit against doctrine, a task-specific doctrine projection,
or evidence-based repository-skill recommendations.

Do not use for:

- quick onboarding or an architecture summary;
- one feature, bug trace, or isolated invariant;
- ordinary implementation or generic review;
- skill brainstorming without repository evidence;
- direct skill creation.

The workflow is read-only. Persistence, implementation, skill creation, commits,
pushes, and publication require their own explicit authority.

## Inquiry dimensions

Infer these dimensions independently; do not force them into one mode enum.

```text
operation   discover | refresh
search      provisional | standard | deep
rendering   doctrine | task-context | audit | portfolio
```

Also establish the **consumer** and **change horizon**: who will use the context,
which classes of future change it should improve, and which consequences matter.
Use a reasonable provisional frame when the prompt already supplies enough
context.

Uncertain user intent does not stop descriptive discovery. It prevents the model
from silently collapsing materially different normative branches. Continue
learning the current system, expose the branch, and ask only when a user-owned
choice becomes necessary to choose among target doctrines or effects.

## Evidence discipline

Research before asserting. Keep these categories distinct:

```text
observed fact
inference
current behavior
current governing law
documented intent
explicit user target
proposal
governed aporia
open question
```

Prefer, in order:

1. current creation, mutation, transition, certification, publication, rollback,
   and invalidation paths;
2. current executable proof and observable behavior;
3. current runtime evidence;
4. several independent current evidence lanes;
5. exact history, regressions, reverts, and failed routes;
6. current repository guidance;
7. names and comments.

Generated reports, prompts, examples, memory summaries, and prior agent
narratives are possible contamination, not independent proof.

Keep search notes and evidence working material internal unless they help the
consumer evaluate a consequential claim. Do not manufacture protocol artifacts,
synthetic IDs, bidirectional graph bookkeeping, schemas, validators, compilers,
or validation receipts merely to perform the inquiry. Never use `validated` as a
generic synonym for convincing.

Read [doctrine-induction.md](references/doctrine-induction.md) when inducing or
reconstructing doctrine; projection alone does not require a new induction.

## Selected inquiry

Select from the existing inquiry dimensions, not a new mode enum:

| Current need | Read before proceeding |
|---|---|
| Discover doctrine, or reconstruct an unsupported part | [discovery.md](discovery.md); it retains the complete induction and adequacy workflow. |
| Refresh existing doctrine | Refresh below; reopen changed/invalidated seams, using discovery only where the prior basis must be reconstructed. |
| Project doctrine for a named task | Task-context projection below and [context-rendering.md](references/context-rendering.md); verify relevant current evidence rather than rerunning whole-repository discovery. |
| Deep search or an unresolved high-impact question needs specialists | [specialists.md](specialists.md); all specialist authority remains read-only. |
| Portfolio or skill recommendations | Induce the relevant doctrine first, then [skill-candidacy.md](references/skill-candidacy.md); an explicit portfolio request is required. |

Do not treat an old doctrine or a summary as current authority. Missing evidence
reopens only the affected claim and its dependencies, not an automatic repo tour.
The complete law form remains required for consequential laws in every rendering:

```text
Law                  what must remain true
Jurisdiction         where and when it applies
Selection pressure   why the repository needs it
Evidence              current observations supporting it
Counterexample        a trace that would violate it
Permitted variation  what may change without violating it
Operational effect   how future work should change because of it
Proof burden          what must establish preservation or refinement
Invalidators          what would make the law obsolete, local, or contested
```

<a id="workflow"></a>
The discovery workflow is in [discovery.md](discovery.md#workflow).
<a id="read-only-specialists"></a>
Specialist rules are in [specialists.md](specialists.md#read-only-specialists).

## Task-context projection

Bind the named consumer, task, and change horizon. Recover the exact existing
doctrine and inspect current evidence for its relevant jurisdictions, freedoms,
proof obligations, and invalidators. Project only what could change this task's
decisions; preserve governing contradictions and evidence limits rather than
turning a descriptive observation into a requirement.

Refresh invalidated claims using Refresh below. Use the relevant parts of
[discovery.md](discovery.md) when the evidence basis is missing; a projection is
not permission to invent doctrine. Apply the existing
[behavioral adequacy](references/behavioral-adequacy.md) to the projected context
and the task's plausible changes. No implementation, persistence, or skill creation
is authorized by this rendering.

## Evidence providers

Codebase Doctrine owns analysis and synthesis. It may consume bounded evidence
from existing architecture maps, direct repository research, `$seq`,
`$negative-ledger`, and `$grill-me`. Missing optional providers do not block
direct research. Providers never become competing doctrine owners.

See [evidence-provider-handoffs.md](references/evidence-provider-handoffs.md).

## Output

Read [context-rendering.md](references/context-rendering.md) for the requested
repository doctrine, task-context, audit, or portfolio view. Use the complete law
form in Selected inquiry; render only decision-relevant evidence and do not dump raw search notes.
Portfolio analysis requires already-induced doctrine and an explicit request.

## Refresh

A refresh reopens the doctrine from current evidence. It does not compare two
prose snapshots and call the difference semantic refresh.

1. Reinspect changed and invalidated seams.
2. Ask which prior authorities, laws, freedoms, wounds, proofs, or aporia the
   changes could affect.
3. Re-falsify affected doctrine against current code and proof.
4. Preserve unaffected doctrine only when its jurisdiction and evidence still
   apply.
5. Report retained, revised, added, retired, and newly aporetic doctrine in plain
   language.
6. Re-render the requested consumer context and rerun behavioral adequacy.

## Persistence

Default output is conversational. Persist only when requested:

```text
.codebase-doctrine/doctrine.md
```

Local-exclude by default unless the user explicitly requests versioned doctrine.
Do not silently create repository files.

## Skill-creation handoff

Codebase Doctrine recommends; it does not create. When skill creation is already
user-authorized, use the bounded `$tune create` handoff in
[skill-candidacy.md](references/skill-candidacy.md). Preserve the exact authority
and package scope; a model-authored assertion does not grant permission.

## Empirical evolution

When a generated repository skill has actual decision episodes, use the evaluation
and evolution guidance in [skill-candidacy.md](references/skill-candidacy.md).

## Hard rules

- Read-only.
- Research before asserting.
- Trace change-bearing seams, not directory tours.
- Form rivals before committing to a consequential explanation.
- Recover selection pressures; do not preserve complexity merely because it
  exists.
- Current behavior, documented intent, explicit target, proposal, and aporia
  remain distinct.
- No law without jurisdiction, selection pressure, counterexample, freedoms,
  operational consequence, proof burden, and invalidators.
- No invariant without owner, initialization, preserving transitions,
  counterexample, boundary, exception ownership, and proof posture.
- Writes and transitions outrank readers and names for authority.
- Preserve real contradiction as governed aporia rather than forcing false
  closure.
- Route knowledge after doctrine and prefer stronger enforcement over skills.
- Zero skills is valid.
- Render the smallest decision-shaping context for the consumer.
- No persistence or skill creation without explicit authorization.
- Never claim exhaustive understanding.
