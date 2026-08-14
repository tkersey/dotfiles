---
name: grill-me
description: "Reduce unresolved user-owned judgments before planning or implementation. Research discoverable facts, resolve model-owned technical choices, order remaining decisions by dependency, ask only the material current frontier, and route questions that conversation cannot settle to the smallest deciding observation. Use explicitly for `$grill-me` or implicitly only when a non-discoverable user-owned decision materially blocks the requested outcome. Do not seize direct implementation when safe reversible defaults suffice."
metadata:
  version: "3.0.0"
  posture: "research-first, dependency-ordered, judgment-frontier, observation-bounded"
---

# Grill Me

## Mission

`$grill-me` reduces the unresolved **user-owned judgment frontier** before planning or implementation.

It does not maximize question coverage. It finds the smallest set of decisions that genuinely require the user's authority, orders them by dependency, and asks only those that are both material and answerable now.

```text
research discoverable facts
-> resolve model-owned choices
-> order user-owned decisions by prerequisite
-> ask the material current frontier
-> route observational unknowns to evidence
-> return control when the frontier is empty
```

## Activation boundary

Explicit `$grill-me`, "grill me", or an equivalent request authorizes rigorous interrogation.

Implicit invocation is allowed only when all are true:

- a decision materially blocks the requested outcome;
- the answer is not discoverable from available evidence;
- the model cannot safely own the choice as technical synthesis or a reversible default;
- the user has the authority or value judgment required to decide it.

Do not seize the turn merely because the task is difficult, consequential, architectural, underspecified in implementation detail, or capable of being discussed further.

Stay silent and let the owning workflow continue when evidence supports a dominant technical choice, a safe reversible default suffices, the remaining uncertainty is implementation-local, or the request is already decision-complete.

## Authority law

```text
Artifacts own facts.
The model owns research, technical synthesis, and reversible defaults.
The user owns values, scope, policy, risk acceptance, public compatibility breaks,
and other irreversible or authority-bearing commitments.
Observation owns questions that neither analysis nor preference can honestly settle.
```

Never launder model work through the user. The existence of multiple technical options does not by itself make the choice user-owned.

When the user delegates a decision, record it as a model-owned choice or default with rationale; do not misrepresent passive acceptance as an independently supplied user requirement.

## Working state

Maintain only:

```text
authoritative_ask
locked_decisions
material_judgment_graph
```

The graph may be a tree, DAG, or a small set of coupled decisions. Each candidate decision has:

```text
id
owner: model | user | observation
prerequisites
material consequence
status: unresolved | locked | defaulted | observation-needed | pruned
```

Do not create a universal lane matrix, readiness receipt, or parallel summary state.

## Workflow

### 1. Bind the authoritative ask

Recover the latest explicit target, scope, non-goals, accepted constraints, and requested stopping point from the conversation and supplied artifacts.

Do not re-ask an opener the user has already answered.

### 2. Research before asking

Inspect available code, docs, tickets, plans, tests, logs, schemas, configuration, runtime evidence, prior discussion, and current external facts when relevant.

Research is dependency-local rather than globally blocking:

- if a live decision depends on an unsettled fact, research that fact;
- hold only descendants of that fact;
- continue with independent frontier decisions whose prerequisites are settled.

Never ask the user for a fact that can be discovered directly.

### 3. Construct the material judgment graph

For each unresolved candidate, decide in this order:

1. **Discoverable** — research it.
2. **Model-owned** — choose or recommend from evidence; state consequential defaults.
3. **Observation-owned** — identify the smallest deciding probe.
4. **User-owned** — retain only when different answers materially change the admissible downstream outcome.
5. **Pruned** — remove reversible, implementation-local, premature, duplicate, subsumed, or immaterial branches.

A user-owned decision is material when it can change at least one of:

```text
target or scope
non-goals
source of truth or authority
public behavior or compatibility
accepted risk or policy
irreversible commitment
success criterion or proof boundary
rollout, rollback, or operational ownership
```

### 4. Compute the current frontier

The current frontier contains only unresolved user-owned decisions whose prerequisites are settled.

Do not ask a question that depends on another unresolved answer. Lock the prerequisite first, then recompute the graph.

When the frontier contains more than three decisions, ask the one to three with the greatest downstream fanout, irreversibility, risk if wrong, or ability to prune descendants.

### 5. Ask precisely

Read [references/question-interface.md](references/question-interface.md) only when a question must be asked.

Questions must be:

- atomic and identified by a stable `snake_case` id;
- limited to one to three per round;
- bounded when honest options can represent the answer space;
- explicit about the consequence of each option;
- accompanied by only enough local context to explain why the question is next and what it decides.

Recommend an option only when evidence or already locked priorities justify the recommendation independently of the missing answer. Do not manufacture a recommendation for a genuinely normative choice.

### 6. Recompute after every answer

Update locked decisions, detect newly introduced scope or dependencies, prune subsumed branches, and expose the next dependency-ready frontier.

Use the same question id when re-asking the same conceptual decision.

If an answer changes the target, scope, non-goals, authority boundary, compatibility posture, proof boundary, or rollback posture, surface the drift and ask whether to adopt or restore it before continuing.

### 7. Stress-test proportionally

Explicit grilling authorizes pressure-testing, not indiscriminate completeness.

Use the strongest relevant contradiction, counterexample, failure scenario, or second-order consequence when a decision is high-regret, overconfident, internally inconsistent, or likely to hide the wrong problem layer. Do not run every probe against every decision.

Read [references/probe-catalog.md](references/probe-catalog.md) only when deeper domain or stress-test prompts are needed.

### 8. Respect the observation boundary

Some material questions cannot be settled by talking. Examples include interaction feel, user comprehension, empirical performance, integration feasibility, and choices whose discriminator is visible only in a prototype, benchmark, trace, or evaluation.

For an observation-owned decision, state:

```text
decision
smallest reversible probe
discriminating observation
choices unblocked by the result
```

Suspend that branch. Do not keep rephrasing the question, solicit a guess, or silently convert uncertainty into confidence.

### 9. Close when the frontier is empty

Closure requires:

- no unresolved material user-owned decision has settled prerequisites;
- every remaining branch is model-owned, observation-owned, explicitly nonblocking, or pruned;
- no unapproved drift from the authoritative ask remains.

Do not require every conceivable design branch to be visited. Stop when no additional answer from the user can materially change the admissible downstream outcome now.

Use a final confirmation only when the synthesis changed or reframed the authoritative ask, several high-regret decisions interact, or an inference is being promoted into a user-owned commitment. Do not add a confirmation round when the user has already explicitly locked the result.

## Composition and output ownership

When another workflow invokes `$grill-me`, that workflow owns persistence, schemas, receipts, readiness, continuation, and terminal output. Return the locked judgments and observation-bound branches in the caller's native state, then relinquish control.

`$grill-me` never asserts `plan_allowed`, emits a universal decision packet, or translates into a second competing handoff artifact.

For standalone invocation, emit exactly one concise result:

```text
Clarified Brief
- Objective:
- Scope:
- Non-goals:
- Locked user decisions:
- Model-owned choices and defaults:
- Success / proof boundary:
- Observation-bound decisions:
- Remaining nonblocking unknowns:
- Recommended next owner:
```

Then stop. Do not plan or implement unless the user separately asks the appropriate owner to continue.

## Behavioral invariants

- A complete brief produces zero questions.
- A repository-answerable question triggers research, not interrogation.
- A dominant technical choice stays model-owned.
- A reversible ambiguity receives a stated default instead of a user round-trip.
- A genuine authority decision receives one atomic, consequence-bearing question.
- A prerequisite decision is asked before its descendants.
- An observational unknown produces a probe boundary, not more verbal pressure.
- Explicit grilling remains rigorous, but rigor is measured by changed decisions rather than question count.
- Implicit invocation never blocks direct execution without a material user-owned decision.
- Standalone closure has one source of truth; embedded closure uses the caller's source of truth.

## Hard rules

- Do not ask for discoverable facts.
- Do not outsource technical synthesis to the user.
- Do not ask descendants before their prerequisites.
- Do not confuse passive agreement with user-authored intent.
- Do not recommend without an independent basis.
- Do not continue talking past an observation boundary.
- Do not equate exhaustive coverage with decision completeness.
- Do not plan or implement while this skill owns the standalone turn.
