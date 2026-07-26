# Doctrine Induction

Codebase Doctrine is an inference discipline, not a form-filling exercise.

The target is the repository's **latent constitution**:

```text
the smallest set of scoped authorities, governing laws, permitted variations,
historical wounds, proof obligations, and unresolved tensions that explains why
the system is shaped as it is and changes how future work should proceed
```

## The eight operators

### 1. Contrast

Compare nearby cases that differ in one consequential way.

Ask:

- Which subsystem permits an operation that another forbids?
- Where does the same data acquire a different owner?
- Which apparently equivalent path has stronger proof or rollback?
- Which exception reveals the real jurisdiction of a law?

Contrast prevents broad repository vocabulary from hiding local constitutional
regimes.

### 2. Counterfactuality

Mentally remove or bypass a check, owner, transition, representation, or proof
surface.

Ask:

```text
What becomes observably wrong?
Who could now create an invalid state?
Which failure becomes unrecoverable?
Which test should fail but may not?
```

If removal changes nothing observable, the candidate may be incidental rather
than doctrinal.

### 3. Abduction

Seek the smallest hidden constraint that explains several independent surfaces.

A strong abductive candidate can explain combinations such as:

- a constructor shape;
- repeated validation;
- an awkward migration path;
- several regression tests;
- a recurring review concern;
- a rejected historical route.

Prefer one scoped law that explains many observations over one law per wound.
Do not confuse explanatory compression with certainty; retain rivals until a
search discriminates them.

### 4. Selection-pressure recovery

Architecture is sedimented response to pressure.

For every persistent irregularity ask:

```text
What requirement or failure selected this shape?
What would the simpler alternative lose?
Is the pressure still current?
Does the current mechanism remain the smallest honest response?
```

Possible outcomes:

```text
load-bearing structure
bounded defensive duplication
migration structure
temporary containment
obsolete scar tissue
unresolved
```

Selection pressure explains what must survive without canonizing the current
implementation. Never invent pressure or historical rationale to complete an
explanation. When available evidence cannot establish it, record the pressure as
unknown, retain the viable rivals, and lower explanatory or prescriptive
confidence without denying directly observed law.

### 5. Rival-model formation

For a consequential explanation, construct a credible alternative.

Example:

```text
Model A: duplicate validation is defense in depth under one authority.
Model B: duplicate validation reflects split authority and incompatible failure
         policy.

Discriminator: which layer can create valid state, bypass the other, issue the
certificate, and own rollback?
```

A rival need not be equally likely. It must be plausible enough that the
available evidence can meaningfully weaken it.

### 6. Negative-space reading

Look for what the repository prevents, omits, or makes difficult:

- states with no public constructor;
- operations available only after certification;
- callers that cannot mutate directly;
- missing inverse or rollback operations;
- conversions that deliberately lose capability;
- abstractions that expose observations but hide representation;
- tempting shortcuts absent from successful paths.

Negative space often reveals law more clearly than naming.

### 7. Explanatory compression

A doctrine item should reduce the amount of context needed to reason correctly.

Ask whether one statement can explain several concrete decisions while retaining:

- jurisdiction;
- counterexamples;
- exceptions;
- permitted variation;
- proof burden.

Reject generic principles that explain everything only by saying nothing.

### 8. Counterexample transfer

Test candidate doctrine beyond the historical examples that suggested it.

Create a novel but repository-plausible case. Ask whether the law predicts:

- the correct owner;
- the legal transition;
- the forbidden bypass;
- the required proof;
- the allowed implementation freedom.

A statement that merely restates old bug fixes has not yet become doctrine.

## Change-bearing seam method

Trace seams where state, evidence, authority, effects, or required observations
cross a boundary.

For each seam recover:

```text
before authority
action authority
accepted and rejected inputs
state or evidence transferred
observable result
failure and partial-failure behavior
rollback or retirement owner
bypass paths
proof surface
```

Then ask which part is law and which part is one replaceable realization.

## Authority and jurisdiction

Ownership is demonstrated most strongly by:

```text
creation and publication
canonical transitions
certificate issuance
transaction and rollback
retirement and invalidation
validation
consumption
names and documentation
```

A repository may contain overlapping jurisdictions. Do not force one global owner
when authority is scoped by subsystem, state class, lifecycle phase, tenant,
capability, or deployment boundary.

Treat shadow ownership as a hypothesis until the bypass is traced. Treat late
validation as evidence of misplaced authority only when it changes who can admit
invalid state or decide failure behavior.

## Law and freedom

Derive law and freedom as a pair.

```text
Law     the observation or transition constraint that must survive
Freedom the representation, algorithm, layout, ownership-neutral mechanism, or
        control flow that may change while the law remains true
```

A doctrine that states only laws creates preservation theater. A doctrine that
states only freedoms cannot protect correctness.

## Wound memory

A wound becomes durable doctrine only when it contributes at least one of:

- a recurring failure family;
- a discriminating counterexample;
- a selection pressure;
- a rejected route with current applicability;
- a proof obligation;
- an invalidator for a prior law.

Do not preserve every bug story. Preserve the smallest lesson that transfers.

## Governed aporia

A contradiction is acceptable when it is accurately represented and bounded.

Examples:

- documentation and runtime assign different authorities;
- two API generations remain simultaneously binding;
- migration temporarily preserves incompatible observations;
- a performance path bypasses a public abstraction;
- two subsystems embody different architectural regimes.

Record where each claim governs, what operation is conditional, and what would
resolve the tension. Do not force a false global law.

## Doctrine admission

A candidate enters the core doctrine only when forgetting it can plausibly cause
wrong action. Prefer a small basis with high explanatory and behavioral leverage.

Keep outside the core:

- directory tours;
- type catalogues;
- locally obvious facts;
- implementation detail with no decision consequence;
- one-off wounds that imply no transferable law;
- generic best practices not selected by repository evidence;
- unresolved speculation that changes no current action.
