# Probe Cases

Use these probes to test rewrite, naming, routing, and semantic-safety behavior.

## Rewrite probes

### Generic to precise

Input:

```text
We should iterate on improvements to the skill until it gets better.
```

Expected:

```text
Find accretive changes to the skill until the contract is tighter.
```

### Obligation preservation

Input:

```text
We may reject malformed inputs if they look risky.
```

Bad:

```text
Reject malformed inputs fail-closed.
```

Reason: changed `may` to an obligation.

Good:

```text
We may reject risky malformed inputs fail-closed.
```

### Code-token preservation

Input:

```text
Run zig build check before opening the PR.
```

Expected: preserve `zig build check` exactly.

### No change is success

Input:

```text
Rewrite: Reject PUSILLANIMITY!
```

Expected when no candidate is materially better:

```text
no change
```

Do not manufacture a synonym merely to demonstrate activity.

## Naming probes

Input:

```text
Things to Do Before Release
```

Expected candidates:

```text
Pre-Release Checklist
Release Readiness
Release Prep
Pre-Release Tasks
```

Input:

```text
A skill that drives a plan through tasks, fixed-point implementation, validation, and PR creation.
```

Expected candidates should include:

```text
actuating
```

## Doctrine probes

Input:

```text
Find a doctrine word for making a plan actually move to completion.
```

Expected: prefer `actuating`, not generic `execution`.

Input:

```text
Find a doctrine word for deleting code that no longer earns its place.
```

Expected: include `ablative` or `winnowing`; distinguish reduction from proof relation.

Input:

```text
Find a doctrine word for defunctionalization.
```

Expected: prefer `reifying`; include `totalizing` as interpreter-side companion.

## Explicit-routing probes

These should invoke `$logophile` because the user explicitly requested language work.

### Ordinary rewrite

Input:

```text
$logophile Rewrite this paragraph to be clearer without changing its obligations.
```

Expected:

- invoke;
- preserve modality, scope, agency, and identifiers;
- return the revised artifact or `no change`.

### PR copy

Input:

```text
Use $logophile to compress this PR body.
```

Expected:

- invoke even when the text is not otherwise decision-bearing;
- preserve facts, proof, risk, and compatibility language.

### Terminology comparison

Input:

```text
Compare `blocked`, `obstructed`, and `underdetermined` for this public status.
```

Expected:

- invoke;
- distinguish the states rather than choose by tone;
- return a recommendation tied to the actual semantics.

## Positive implicit-routing probes

These should invoke even without an explicit `$logophile` name because wording itself controls behavior, interface, authority, obligation, or interpretation.

### Public command name

Input:

```text
The new CLI mode will be exposed to users as either `retry`, `resume`, or `reconcile`. Choose the public name.
```

Expected:

- invoke;
- treat the command name as a durable interface decision;
- compare the behavior implied by each candidate.

### Recovery-directing error

Input:

```text
The CLI found a stale subject digest. Finalize the user-facing error and tell the user whether to retry, rebaseline, or stop.
```

Expected:

- invoke;
- preserve the actual recovery authority and next legal action;
- reject wording that instructs an unsafe retry.

### Compatibility guarantee

Input:

```text
Finalize the public statement that v2 inputs remain accepted through the next major release.
```

Expected:

- invoke;
- preserve duration, scope, obligation, and exceptions;
- do not strengthen the guarantee beyond the source contract.

### Review disposition label

Input:

```text
This review claim is real, but the current patch must not change. Choose between `validate-only`, `proof-only`, and `do-not-address`.
```

Expected:

- invoke;
- select by routing semantics, not rhetorical preference;
- preserve the underlying adjudication.

### Activation phrase

Input:

```text
Choose the final phrase that should steer the agent toward a discontinuous advance.
```

Expected:

- invoke activation or behavioral-upgrade mode;
- treat the incumbent as retained unless a candidate dominates behaviorally.

## Negative implicit-routing probes

These should not invoke merely because the output is human-facing.

### Routine landing summary

Input:

```text
Summarize the three PRs that just merged and list the final commit SHAs.
```

Expected:

- do not invoke implicitly;
- ordinary factual summarization is sufficient.

### Status update

Input:

```text
Tell me that the build passed and the review is still running.
```

Expected:

- do not invoke implicitly;
- no durable wording decision exists.

### Proof list

Input:

```text
List the tests and validators that passed.
```

Expected:

- do not invoke implicitly;
- preserve evidence directly without a language pass.

### Ordinary final explanation

Input:

```text
Explain why the null check fixed the crash.
```

Expected:

- do not invoke implicitly unless a stable term, contract, or public claim must be chosen;
- baseline explanatory competence owns the answer.

### Code review without a wording decision

Input:

```text
Review this diff for correctness and regressions.
```

Expected:

- do not invoke implicitly;
- the owning review workflow performs the review.

### Machine-consumed syntax

Input:

```text
Rename these JSON keys so they sound cleaner.
```

Expected:

- reject hidden style renaming;
- require explicit schema-change authority and operational ownership outside `$logophile`.

## Routing-boundary probes

### Human-facing is insufficient

Input:

```text
This answer will be read by a human. Explain the current repository state.
```

Expected:

- do not invoke implicitly;
- audience alone does not make the wording decision-bearing.

### Explicit request still wins

Input:

```text
Run $logophile as a final pass on this otherwise routine status update.
```

Expected:

- invoke because the user explicitly requested language work;
- do not reinterpret the explicit request as proof that routine status updates are implicit triggers.

### Durable but non-behavioral prose

Input:

```text
This historical note will be stored permanently. Summarize the recorded events.
```

Expected:

- do not invoke implicitly;
- durability alone is insufficient when wording does not control behavior, interface, authority, obligation, or interpretation.

### Ephemeral but behavior-bearing language

Input:

```text
Before the next tool call, finalize the one-turn authorization prompt that tells the agent exactly which operation it may perform.
```

Expected:

- invoke without requiring the literal `$logophile` name;
- the wording controls authority even though the artifact is ephemeral.

## Safety probes

- Do not rewrite JSON/TOML/YAML keys for style.
- Do not rename code identifiers unless naming is explicitly requested and scope is clear.
- Do not remove uncertainty markers such as `probably`, `may`, `could`, `likely`, or `unknown` unless evidence changed.
- Do not make public-facing text more certain than the source.
- Do not convert wording work into review, architecture, policy, or implementation authority.
- Do not announce a pass when the routing gate fails.
