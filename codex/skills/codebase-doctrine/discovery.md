# Doctrine discovery

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
What design decision should callers not need to know?
Who still knows it, and which local change forces coordinated edits?
```

Writes and transitions outrank readers and names when identifying authority.
Architecture is a hypothesis supported by responsibilities, dependency direction,
and preserved observations, not folder names. Trace shared design knowledge, not
just execution phases; keep independent verification and authority boundaries.

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

If not, retain necessary local API knowledge for interface-contract routing;
keep other material as evidence, local implementation detail, or noise.

### 11. Route durable knowledge

Route knowledge only after doctrine induction. Prefer the strongest owner:

```text
representation or code
test, property, model, or static tooling
CI or release gate
local interface contract
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
