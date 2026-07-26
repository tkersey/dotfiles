---
name: codebase-doctrine
description: "Recover a repository's latent constitution: the scoped authorities, governing laws, permitted variations, historical wounds, proof obligations, and governed aporia that explain how it remains correct and how future agents should act. Use for deep codebase learning plus durable doctrine, correctness atlases, authority/law/failure/proof analysis, doctrine refresh, audit, task-context projection, or evidence-based repository-skill candidacy. Research before asserting and preserve rival models until evidence discriminates them. Not for quick onboarding, one isolated invariant, implementation, generic review, or direct skill creation."
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

See [doctrine-induction.md](references/doctrine-induction.md).

## Workflow

### 1. Frame the decision horizon

Name:

- the intended consumer;
- the repository scope;
- the likely classes of future change;
- the consequences the doctrine must protect;
- whether the requested posture is descriptive, prescriptive, comparative, or
  intentionally undecided.

Do not ask the user for repository facts that can be discovered. Ask only for
material user-owned judgments that cannot be inferred or safely branched.

### 2. Trace change-bearing seams

Do not tour directories. Follow places where correctness can change:

```text
creation
mutation
validation
certification
publication
irreversible effect
authority transfer
compatibility conversion
migration
rollback
retirement or invalidation
```

At each seam ask:

```text
Who may act?
What state or evidence crosses?
What becomes observable?
What plausible bypass exists?
What can fail?
Who may reverse or retire it?
What proof makes the transition credible?
```

Writes and transitions outrank readers and names when identifying authority.
Architecture is a hypothesis supported by responsibilities, dependency direction,
and preserved observations, not folder names.

### 3. Form rival explanations

Before accepting an architectural or doctrinal explanation, construct at least
one credible rival when the evidence permits.

For each rival record privately:

```text
what it explains
what it fails to explain
which evidence strengthens it
which evidence weakens it
what exact search would discriminate it
```

Do not let the first coherent narrative become doctrine.

### 4. Recover selection pressures

For every apparent law, awkward abstraction, duplicated check, fallback, or
boundary ask:

```text
Why did this survive?
What recurring failure or requirement selected it?
What cleaner-looking alternative would lose a required observation?
Which earlier route was rejected?
Is this design principled structure, temporary migration, defensive duplication,
or scar tissue?
```

History is useful when it explains current structure. Current code and current
proof outrank stale historical rationale.

### 5. Derive jurisdictions and authorities

For important state, evidence, and effects determine who may create, mutate,
validate, certify, publish, transfer, consume, roll back, retire, or invalidate
them.

Name:

- the jurisdiction in which the authority applies;
- the canonical transition paths;
- shadow owners and bypasses;
- late validation;
- ambiguous or conditional authority transfer;
- exceptions and their owners.

A validator or reader is not an owner merely because it observes the state.

### 6. Derive laws and freedoms together

A governing law is not a field-complete sentence. It is a scoped constraint that
explains observations and changes future decisions.

For each consequential law state:

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

Record freedoms and deliberate non-laws prominently. Doctrine must prevent cargo
cult preservation by distinguishing required observations from replaceable
representations, algorithms, layouts, and control flow.

Begin invariant work with a bad trace:

```text
valid state -> transition -> invalid observable state
```

Downgrade an invariant that lacks an owner, initialization, preserving
transitions, a violating counterexample, enforcement boundary, exception owner,
and proof posture.

### 7. Perform failure archaeology

Normalize local wounds:

```text
local failure
-> recurring family
-> violated law or authority
-> incorrect representation, boundary, transition, or proof shape
-> selection pressure on the surviving design
```

Distinguish:

- one failed attempt from a recurring route failure;
- historical rationale from current doctrine;
- scar tissue from a still-live constraint;
- witnessed negative evidence from fuzzy similarity.

Only a current canonical negative-ledger projection may forbid a route. Other
failure evidence may warn, prioritize inquiry, or suggest a falsifier, but may
not silently prohibit action.

### 8. Map proof as claim coverage

For each law or invariant identify how the repository currently establishes it:

```text
representation or type
opaque constructor
canonical transition
static analysis
test or property
state-machine/model proof
integration proof
runtime witness
manual or reviewer judgment
CI or release gate
```

Distinguish proof design, current execution, historical execution, and manual
judgment. A test path is not evidence that the test currently passes, and a
passing suite is not evidence that it covers the claimed law.

Ask whether the proof:

- targets the law or only one historical example;
- covers transitions, failure, rollback, and exceptions;
- can pass a bad implementation;
- transfers to a novel case;
- has an invalidation trigger.

### 9. Preserve governed aporia

Do not average incompatible claims. A material contradiction may remain when it
is real.

A governed aporia names:

```text
the incompatible claims
where each is authoritative
the evidence for each
which operations are unsafe or conditional because of the tension
what evidence or owner decision could resolve it
how future changes must behave while it remains unresolved
```

The inquiry may stop with unresolved material tension when the tension is
represented and behaviorally bounded. The stopping condition is not "no
contradiction"; it is "no material contradiction remains hidden or operationally
unbounded."

### 10. Compress to the doctrine basis

Admit a finding to durable doctrine only when forgetting it could produce a
plausible wrong decision.

Use this admission test:

1. Is it nonlocal or easy to misinfer from local code?
2. Would forgetting it materially change implementation, review, migration, or
   proof?
3. Does it apply beyond one isolated incident?
4. Is it stable enough to survive several future changes?
5. Can evidence and a meaningful counterexample be named?
6. Can its jurisdiction, freedoms, and invalidators be stated?
7. Does it change what a future agent inspects, preserves, rejects, changes, or
   proves?

If not, keep it as evidence, local implementation detail, or noise.

### 11. Route durable knowledge

Route knowledge only after doctrine induction. Prefer the strongest owner:

```text
representation or code
test, property, model, or static tooling
CI or release gate
concise repository guidance
ADR or reference
canonical negative ledger
repository-specific skill for recurring judgment
retain in doctrine
reject
```

Important does not imply skill-worthy. Zero repository-specific skills is a
valid result.

See [knowledge-routing.md](references/knowledge-routing.md) and
[skill-candidacy.md](references/skill-candidacy.md).

### 12. Render exact context

Separate:

```text
research record      material used to reason honestly
doctrine             compressed latent constitution
consumer context     the doctrine projection needed for one decision horizon
evidence appendix    support for consequential claims
```

Default to readable Markdown. Do not emit YAML merely because indentation looks
formal. Use a machine format only when a real downstream consumer requires one
and its contract is supplied by that owner.

See [context-rendering.md](references/context-rendering.md).

### 13. Test behavioral adequacy

Before finalizing, rehearse the context against future decisions:

- simulate an extension, a migration, and removal of an apparent workaround;
- test whether it defeats the repository's most tempting wrong mental model;
- apply its laws to a novel case;
- ablate each doctrine item and remove those whose absence changes no plausible
  decision;
- name the drift that would invalidate each consequential law.

If the context fails, perform the smallest targeted inquiry that could repair the
failure. Do not respond by adding ceremonial fields.

See [behavioral-adequacy.md](references/behavioral-adequacy.md).

## Read-only specialists

Use specialists in deep search or for unresolved high-impact questions. Launch
only workers whose answer could change the doctrine or rendering.

Recommended sequence:

```text
1. codebase_cartographer + authority_state_mapper
2. behavioral_law_miner / failure_forensics_analyst /
   codebase_doctrine_proof_mapper for identified seams
3. doctrine_portfolio_skeptic only when a portfolio is requested
4. search_saturation_auditor after a complete draft
```

Assignments must be discriminating questions or bounded seam excavations, not
requests to fill a doctrine section.

Every specialist is read-only, does not spawn children, and returns:

```text
scope inspected
observations with concrete evidence
rival models supported or weakened
selection pressures or counterexamples found
unresolved questions
why the result changes or fails to change the doctrine
```

Specialists do not author the final doctrine, propose pseudo-patches, or return
schema-shaped packets. The root rechecks high-impact claims and owns synthesis.

## Evidence providers

Codebase Doctrine owns analysis and synthesis. It may consume bounded evidence
from `$codebase-archaeology`, `$seq`, `$negative-ledger`, `$retrace`, and
`$grill-me`. Providers never become competing doctrine owners.

See [evidence-provider-handoffs.md](references/evidence-provider-handoffs.md).

## Output

### Repository doctrine

Default shape:

```markdown
# Repository Doctrine

## Scope and consumer
## Governing pressures
## Jurisdictions and authorities
## Load-bearing laws
## Freedoms and non-laws
## Wound memory and rejected routes
## Governed aporia
## Change index
## Knowledge destinations
## Evidence appendix
## Confidence and next inquiries
```

For each law use the complete law form from this skill. Do not dump raw search
notes or every discovered type.

### Task-context projection

For a named change, render only:

```text
inspect
preserve
free to change
reject or treat as suspicious
prove
reopen when
```

### Audit

Compare current guidance, skills, and enforcement surfaces with the doctrine.
Report omissions, contradictions, cargo-cult rules, stale guidance, and knowledge
that should move to a stronger owner.

### Portfolio

Evaluate repository-specific skill candidacy only from already-induced doctrine
and only when requested. Do not rerun the entire repository inquiry unless the
doctrine is stale.

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

Codebase Doctrine recommends; it does not create.

After explicit user authorization, hand `$ms` the smallest sufficient context:

- the candidate mission;
- the governing doctrine and jurisdiction;
- recurring triggers and non-triggers;
- consequential decisions;
- required context and outputs;
- success, failure, narrowing, and retirement signals;
- routes excluded by current canonical negative evidence;
- the allowed package boundary.

The effect owner must verify current user authority. A model-authored statement
that authorization exists is not itself authority.

## Empirical evolution

After a generated repository skill has real decision episodes:

```text
$seq skill-decision-audit
-> $tune
-> $refine
```

Evaluate decision quality, trigger quality, missed and ceremonial activation,
outcome association, and whether knowledge has become better owned by code,
tests, tooling, CI, or guidance. Return changed law, authority, boundary, proof,
freedom, or target posture to `$codebase-doctrine` refresh. Do not tune from raw
mention counts.

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
