# Protocol evolution guardrail

Stateful abstractions often look removable until you model the protocol they encode. Do not flatten them without a transition table.

## Use this when

- allowed operations depend on current status/state/phase;
- retries, cancellation, timers, audit steps, or human approvals are present;
- workflow/state manager/tooling is under audit;
- UI steps, checkout flows, onboarding flows, or background jobs have lifecycle rules;
- deleting a framework abstraction could leave ad hoc booleans and nullable fields.

## Required transition table

```md
| From state | Command/event | Guard | To state | Side effects | Proof |
|---|---|---|---|---|---|
```

Add invalid-transition rows too:

```md
| From state | Disallowed command | Expected rejection |
|---|---|---|
```

## Preserve these facts

- state set;
- allowed commands per state;
- guards;
- side effects;
- retries and idempotency;
- cancellation behavior;
- audit/logging behavior;
- persistence shape;
- public/wire/storage compatibility.

## Good reductions

- workflow engine -> explicit reducer plus job queue for actual async work;
- global state manager -> local reducer for one flow;
- framework wizard component -> HTML forms plus explicit transition table;
- enum + optional fields -> coproduct behind legacy DTO adapter;
- event bus for local synchronous behavior -> direct function calls plus explicit side-effect boundary.

## Bad reductions

- state machine -> string status plus scattered `if` checks;
- reducer -> loose DOM event handlers with no invalid-transition tests;
- workflow engine -> cron script that loses retries/auditability;
- tagged union -> bag of optional fields;
- guarded command handler -> public mutation endpoints with duplicated validations.

## Split guidance

When protocol value is real but wrapper tax is high:

```md
Move: split
Reduce wrapper:
Preserve protocol as:
Transition table:
First seam:
Proof:
Rollback:
```

The safest first seam is usually a single command handler or reducer path with old and new behavior compared by fixtures.
