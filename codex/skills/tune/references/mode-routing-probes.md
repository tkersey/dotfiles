# `$tune` Mode Routing Probes

Use these probes when refining or validating `$tune` mode selection.

## Audit Only

Prompt:

```text
Is the docx skill being used as intended?
```

Expected mode: `audit-only`

Reason: The user asks for a diagnostic answer, not a change plan or file edit.

Prompt:

```text
Show me how the pdf skill has been used recently.
```

Expected mode: `audit-only`

Reason: The user asks for observed usage evidence.

## Proposal Only

Prompt:

```text
Do a deep analysis of my tune skill so we can make it perform in the optimal way.
```

Expected mode: `proposal-only`

Reason: The dominant request is analysis and optimization guidance. There is no explicit instruction to edit files now.

Prompt:

```text
What should change in the pdf skill based on recent usage?
```

Expected mode: `proposal-only`

Reason: The user asks what should change, not for the change to be applied.

Prompt:

```text
Tune the docx skill based on recent sessions, but don't edit yet.
```

Expected mode: `proposal-only`

Reason: The user explicitly blocks edits.

## Apply with `$refine`

Prompt:

```text
Use $tune on the slides skill and apply the smallest validated fix.
```

Expected mode: `apply-with-refine`

Reason: The user explicitly asks to apply a fix and requires validation.

Prompt:

```text
Patch the gh skill based on recent usage evidence and validate it.
```

Expected mode: `apply-with-refine`

Reason: The user explicitly asks to patch files and validate.

Prompt:

```text
Here is a complete evidence-backed refinement brief. Apply it to the target skill now.
```

Expected mode: `$refine` handoff or `$refine` phase only

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

Prompt:

```text
Apply the smallest validated self-tune update to $tune now.
```

Expected mode: `apply-with-refine`

Reason: The user explicitly names the protected self-target and asks to apply a narrow validated update.

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

Reason: PR creation is not `$tune`'s responsibility.
