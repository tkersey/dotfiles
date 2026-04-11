# Brooks Principles Behind This Skill

This reference translates the main lessons from *No Silver Bullet* into concrete behaviors for Codex.

## 1. Essential vs accidental difficulties

The core distinction:

- **Essential difficulties** come from the nature of the software problem itself.
- **Accidental difficulties** come from the current tools, languages, process, or machine constraints used to express that solution.

### How to apply this

When evaluating a task, first decide whether the pain is mainly:

- conceptual: unclear requirements, complex domain rules, many interacting systems, inconsistent constraints, invisible state, change pressure
- mechanical: repetitive edits, boilerplate, syntax, weak tooling, flaky local setup

If the problem is conceptual, do not respond as though a framework switch or automation alone will solve it.

## 2. The four essential properties

### Complexity

Software contains many distinct elements whose interactions grow nonlinearly.

**Codex behavior:**
- avoid pretending a giant plan is "simple"
- reduce scope aggressively
- decompose by interfaces and invariants
- prefer a thin vertical slice over a large speculative design

### Conformity

Software must conform to arbitrary external interfaces: organizations, laws, APIs, legacy systems, and human workflows.

**Codex behavior:**
- enumerate external constraints explicitly
- assume integration boundaries create real complexity
- do not propose redesigning the whole world when the system must conform to it

### Changeability

Successful software is always pressured to change.

**Codex behavior:**
- identify likely change hot spots
- make early decisions reversible where possible
- isolate volatile parts behind narrow seams
- avoid premature generalization everywhere else

### Invisibility

Software has no natural geometric representation.

**Codex behavior:**
- produce explicit textual artifacts: data model, state machine, interface list, sequence outline, risk log
- summarize architecture in a way humans can inspect quickly

## 3. Why many breakthroughs only help a little

High-level languages, timesharing, unified environments, better tools, workstations, and many fashionable paradigms mostly reduce accidental complexity.

**Codex behavior:**
- welcome productivity tools
- avoid claiming that tools erase the conceptual challenge
- when recommending a tool, say exactly what accidental friction it reduces
- then state what hard conceptual work remains

## 4. Buy versus build

One of the strongest productivity moves is to avoid building what can be bought or reused.

**Codex behavior:**
- inspect the repo and the platform first
- look for libraries, services, templates, CLIs, or modules already covering most of the need
- prefer adaptation over greenfield work when fit is acceptable
- define the smallest custom layer that preserves local needs

## 5. Requirements refinement through prototyping

The hardest part is often deciding what to build. Requirements become clearer only after people interact with something concrete.

**Codex behavior:**
- suggest a prototype when requirements are fuzzy or contested
- keep the prototype thin and mainline-focused
- specify what it omits and what question it answers
- use prototypes to discover interface, workflow, and usability issues early

## 6. Grow, don't build

Complex software is better grown through incremental development than fully specified and assembled in one pass.

**Codex behavior:**
- create a running skeleton first
- add capability incrementally
- keep each stage working
- prefer end-to-end slices to deep layers of untested infrastructure
- let tests and demos evolve with each increment

## 7. Great designers and conceptual integrity

The best systems usually reflect a coherent design mind rather than a loose committee compromise.

**Codex behavior:**
- present a recommended direction, not just a menu of unrelated choices
- reduce abstraction sprawl
- preserve naming consistency and one dominant conceptual model
- when trade-offs are real, compare them clearly and then recommend a default

## 8. Verification is useful but limited

Formal correctness against a wrong or incomplete specification does not solve the main problem.

**Codex behavior:**
- use tests and review to challenge the specification itself
- confirm behavior with examples and walkthroughs
- treat discovered contradictions as specification defects, not just code defects

## 9. What this skill should output

For strategic software tasks, good outputs usually include:

- essential vs accidental diagnosis
- build vs buy recommendation
- thin prototype or first slice
- incremental delivery plan
- assumptions, risks, and deferred edge cases
- one immediate next action

## 10. What this skill should avoid

Avoid:

- grand rewrites justified mainly by a new tool or framework
- vague architecture talk with no interfaces or increments
- overpromising reliability from verification or testing alone
- giant option lists with no recommendation
- solving accidental friction while leaving the conceptual problem undefined
