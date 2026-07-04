# `$tune` Mode Routing Probes

Use these probes when refining or validating `$tune` mode and evidence-source selection.

## Audit Only

Prompt:

```text
Is the docx skill being used as intended?
```

Expected mode: `audit-only`

Expected source: `history`, recent default unless the user supplies another scope.

Reason: The user asks for a diagnostic answer, not a change plan or file edit.

Prompt:

```text
Did the slides skill just miss an activation in this conversation?
```

Expected mode: `audit-only`

Expected source: `in-flight`

Reason: The user asks about current behavior, not historical recurrence or edits.

## Proposal Only

Prompt:

```text
Do a deep analysis of my tune skill so we can make it perform in the optimal way.
```

Expected mode: `proposal-only`

Expected source: `mixed` if historical usage is needed; otherwise `worktree` + `provided/current feedback`.

Reason: The dominant request is analysis and optimization guidance. There is no explicit instruction to edit files now.

Prompt:

```text
What should change in the pdf skill based on recent usage?
```

Expected mode: `proposal-only`

Expected source: `history`, recent window.

Reason: The user asks what should change, not for the change to be applied.

Prompt:

```text
Tune the docx skill based on all relevant session history, but don't edit yet.
```

Expected mode: `proposal-only`

Expected source: `history`, arbitrary scope.

Reason: The user explicitly asks for arbitrary history and blocks edits.

Prompt:

```text
Use this current conversation as the evidence and tell me whether tune should change.
```

Expected mode: `proposal-only`

Expected source: `in-flight`

Reason: Current-turn evidence is sufficient for a proposal, but edits were not requested.

## Apply with `$refine`

Prompt:

```text
Use $tune on the slides skill and apply the smallest validated fix.
```

Expected mode: `apply-with-refine`

Expected source: `mixed`: usage evidence plus `worktree` for validation and publication status.

Reason: The user explicitly asks to apply a fix and requires validation. Apply authority permits local edits and validation only; commit and push should be reported as `blocked:not-requested`.

Prompt:

```text
Patch the gh skill based on recent usage evidence and validate it.
```

Expected mode: `apply-with-refine`

Expected source: `history` + `worktree`

Reason: The user explicitly asks to patch files and validate. Patch authority permits local edits and validation only; commit and push should be reported as `blocked:not-requested`.

Prompt:

```text
Apply the smallest validated update to the tune skill, commit it, and push it.
```

Expected mode: `apply-with-refine`

Expected source: `mixed`

Reason: The user explicitly requests file changes plus commit/push publishing. Because `$tune` is self-targeted, the edit must remain narrow and validation must pass before commit or push.

Prompt:

```text
Here is a complete evidence-backed refinement brief. Apply it to the target skill now.
```

Expected mode: `$refine` handoff or `$refine` phase only

Expected source: `provided` + `worktree`

Reason: Diagnosis is already supplied; direct editing is owned by `$refine`.

## Protected and Self-Targeted Skills

Prompt:

```text
Analyze whether $seq should be updated.
```

Expected mode: `proposal-only`

Reason: `$seq` is protected and the user did not explicitly ask to edit files.

Prompt:

```text
Deeply analyze $tune itself and give me the optimal changes.
```

Expected mode: `proposal-only`

Reason: Self-targeted `$tune` changes require explicit file-edit permission.

## Non-Triggers and Handoffs

Prompt:

```text
Create a new skill for managing OpenAPI specs.
```

Expected owner: `$ms`

Reason: New skill creation is not tuning an existing skill.

Prompt:

```text
Mine arbitrary sessions for interesting skill patterns.
```

Expected owner: `$seq`

Reason: No target skill is provided; this is broad session mining.

Prompt:

```text
Open a PR for these skill changes.
```

Expected owner: `$ship`

Reason: PR creation is not `$tune`'s responsibility. `$tune` may commit and push only when explicit publish intent exists and validation passes; `$ship` owns PR creation.
