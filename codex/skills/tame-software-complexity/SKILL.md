---
name: tame-software-complexity
description: Use when a task involves ambiguous or shifting software requirements, architecture or system design choices, build-vs-buy decisions, thin prototypes, incremental delivery planning, or evaluating tools/frameworks/AI systems without treating them as a silver bullet. Use it to separate essential complexity from accidental friction and to produce a grounded plan before or alongside implementation. Do not use for straightforward code edits, isolated bug fixes with clear reproduction steps, rote migrations, or purely syntactic refactors unless the user explicitly asks for broader design guidance.
---

# Tame Software Complexity

Approach software work as a conceptual design problem first.

Treat languages, frameworks, tooling, and automation as useful for removing accidental friction, but not as substitutes for understanding the problem, interfaces, constraints, and change pressures.

## When to use

Use this skill when the hard part is one or more of the following:

- figuring out what should actually be built
- choosing between building, buying, or reusing
- shaping a coherent architecture or system boundary
- planning a spike, prototype, or thin end-to-end slice
- deciding how to grow a system safely over time
- evaluating a proposed "silver bullet" technology claim

Do **not** use this skill when the task is already well-specified and the main work is mechanical implementation.

## Core operating principles

1. **Diagnose essence before accidents.**
   - Essential complexity = domain rules, user workflows, policy constraints, correctness requirements, multi-system interfaces, data semantics, coordination, and organizational realities.
   - Accidental complexity = syntax, framework ceremony, boilerplate, local tooling, repetitive plumbing, and incidental build friction.
   - Say explicitly which kind of complexity dominates the task.

2. **Prefer buy/reuse before build.**
   - Check whether the repository, platform, framework, or external services already provide most of the needed capability.
   - Prefer reuse when it satisfies the core need with acceptable constraints.
   - When reuse is imperfect, define the narrow custom layer rather than defaulting to a full custom system.

3. **Prototype to learn.**
   - For ambiguous requirements, propose a thin prototype or spike that exercises the mainline path.
   - State what the prototype is intended to validate or falsify.
   - Deliberately defer edge cases and exception handling unless they are central to the risk being explored.

4. **Grow the system incrementally.**
   - Start with a running skeleton, stubbed flow, or narrow vertical slice.
   - Add one capability at a time.
   - After each increment, keep the system buildable, testable, and demoable.

5. **Protect conceptual integrity.**
   - Prefer one coherent design over a grab bag of patterns.
   - Minimize competing abstractions, duplicate representations, and parallel workflows.
   - When presenting alternatives, recommend one default unless trade-offs are genuinely close.

6. **Make the invisible visible.**
   - Externalize structure with concise artifacts such as:
     - domain glossary
     - interface map
     - state model
     - invariants list
     - decision log
     - risk register
     - phased rollout plan

7. **Validate the specification, not just the code.**
   - Use examples, tests, fixtures, and prototype walkthroughs to expose wrong assumptions.
   - Treat surprising behavior as feedback about the specification first, not only about the implementation.

## Required workflow

Follow this sequence unless the user explicitly asks for something narrower:

### 1) Frame the problem

Extract or infer:

- user goal
- primary actors
- important workflows
- interfaces to people, systems, or policies
- invariants and correctness constraints
- likely sources of change
- what must be true for the work to count as done

If the request is underspecified, state the most important assumptions plainly.

### 2) Separate essential from accidental complexity

Produce a short diagnosis:

- **Essential complexity**: what is inherently hard here?
- **Accidental complexity**: what is merely tooling/process friction?
- **Dominant risk**: what is most likely to cause rework or failure?

### 3) Check build vs buy vs reuse

Before proposing a custom design, inspect what already exists:

- existing modules in the repo
- platform/framework features
- internal services or APIs
- mature libraries or managed services

Then recommend one of:

- **Reuse directly**
- **Wrap or adapt an existing solution**
- **Build a thin custom layer**
- **Build fully custom** only when requirements truly force it

Explain the reason in terms of fit, constraints, and maintenance burden.

### 4) Define the thinnest learning artifact

For ambiguous work, specify the smallest useful prototype:

- scope of the prototype
- what it intentionally omits
- what question it answers
- what evidence would count as success or failure

If a prototype is unnecessary, say why.

### 5) Plan incremental delivery

Break the work into a minimal sequence of running increments. Favor vertical slices over deep infrastructure-first plans.

For each increment, identify:

- capability added
- interfaces affected
- tests or checks
- rollback or containment strategy

### 6) Surface the invisible design

When useful, output one or more compact artifacts in text form, such as:

- a component map
- request/response contracts
- state transitions
- invariants
- change hot spots

### 7) Recommend the next action

End with the smallest credible next step, not a grand rewrite.

## Default response shape

Use this structure unless the user requested a different format:

1. **Diagnosis**
   - essential vs accidental complexity
   - dominant risk

2. **Recommendation**
   - build/buy/reuse choice
   - primary design direction

3. **Prototype or first slice**
   - thin learning artifact or first running increment

4. **Increment plan**
   - 2-5 concrete stages

5. **Risks and assumptions**
   - what may change
   - what is being deferred

6. **Next action**
   - one concrete step to take now

## Interaction rules

- Be concrete. Name files, modules, endpoints, commands, data entities, or UI flows when known.
- Avoid promising order-of-magnitude gains from a new tool alone.
- When recommending a new framework, say what accidental pain it removes and what essential complexity will remain.
- Prefer reversible decisions early.
- Do not overengineer for speculative future change; isolate likely change points instead.
- Do not hide ambiguity. Mark it and design a small experiment around it.

## Ask these questions implicitly while working

- What is truly hard here because of the problem itself?
- What pain is just accidental tooling friction?
- Can we buy or reuse most of this?
- What is the smallest prototype that would reduce uncertainty?
- What is the smallest running version we can grow from?
- What design choice preserves conceptual integrity?
- What artifact will make the invisible structure legible?

## Read next when needed

- For the conceptual basis and translations from Brooks's paper, read [references/brooks-principles.md](references/brooks-principles.md).
