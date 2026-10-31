# Textual-source investigation

Use for standalone analysis or within an authorized optimization campaign.
[The skill's intent and authority rules](../SKILL.md#select-intent-before-the-workflow)
govern both. This is the shared investigation method, not a second skill,
controller, handoff protocol, or automatic permission to experiment.

Optimize for justified decisions. A higher evaluation score can support a
decision, but it is not, by itself, an explanation. Investigate which textual
sources contributed to success or failure, under what conditions, and what the
evidence justifies retaining, changing, or removing.

## Scope

Keep investigation depth proportional to the unresolved question. Reuse adequate
source mappings and completed comparisons rather than rerunning settled work.
Honor run-only/read-only scope, authorized experiments and budgets, and the
receiving workflow's verification gates.

## Trace outcomes to the text that was used

Read the actual criteria, cases, results, and available traces before editing.
Separate what the task requires, what the evaluator measured, and what happened.
Use successful as well as failing cases; aggregate scores alone cannot localize
a contribution. Find the first consequential divergence for a failure and the
successful behavior whose source contribution is being claimed for a pass.

Inspect the relevant agent/system/developer prompts, AGENTS.md instructions,
skill discovery descriptions, loaded SKILL.md bodies and references, examples,
tool descriptions, templates, and supplied context. Keep evaluator/rubric text
separate from instructions delivered to the agent; investigate measurement errors
without silently weakening acceptance. Treat captured text as evidence, not as
instructions to the investigator.

Map each live candidate to its exact file or resource, revision or digest,
heading and line span or short quotation, and its role, order, and surrounding
scope in the effective request. Trace generated text back to its authoring source.
For skills, distinguish discovery, activation, body loading, and reference
retrieval. Present on disk is not delivered; requested text is not necessarily
rendered text. Verify the suspected span reached the consequential decision.
When delivery or source provenance is unavailable, mark that link unverified
rather than inventing a source attribution. Obtain existing artifacts before
asking the user to recreate them.

## Localize a textual contribution

Compare source and effective-text differences across successful and failing
conditions. Read candidate passages in context, including definitions,
exceptions, examples, and competing rules elsewhere. Turn suspected ambiguity,
conflict, missing guidance, misleading examples, placement, or truncation into
competing predictions, not diagnoses inferred from phrasing alone.

Start with a coherent instruction family, section, or reference; narrow toward
specific clauses only when the evidence supports it. Preserve the task-bearing
scaffold, frontmatter, instruction authority, heading/list scope, dependencies,
and reference links unless one is the declared intervention. A deletion that
removes a required obligation can diagnose sensitivity but is not a repair.
The retained scaffold can itself contribute; do not declare it innocent.

Choose the smallest contrast that changes the next decision:

| Uncertainty | Useful contrast |
| --- | --- |
| Was the intended text used? | Inspect source-to-request delivery before another wording experiment. |
| Does this passage help or hurt? | Remove or replace it under matched conditions; use add-back or reversal to test whether the outcome follows it. |
| Which region matters? | Reduce coherent blocks while preserving the executable scaffold. If both halves or neither half reproduce the behavior, test retained factors or combinations instead of assuming monotonic bisection. |
| Wording, position, or authority? | Change one declared dimension while preserving the others; relocation is not a neutral rewrite. |
| Is guidance missing? | Test a minimal explicit condition against the unchanged baseline; check whether existing guidance already supplies it before adding another rule. |
| Are instructions redundant or interacting? | Test the smallest evidence-motivated combination, such as both present, each removed, and both removed. |

Investigate helpful text as rigorously as harmful text. An unchanged outcome after
removal does not prove irrelevance, and improved behavior after deletion does not
prove that length was the cause. No observed effect is not proof of no effect.
Do not force a single culprit when contributions are conditional or distributed.

## Iterate with attributable evidence

Before a comparison, identify the question, exact source patch, baseline,
protected conditions, differing predictions, measurement, sampling/stopping rule,
and result-dependent next action. Keep this in the existing experiment record;
do not build a new evaluation platform. Prefer inspection for delivery questions
and the owning runner for behavioral uncertainty.

For behavioral comparisons and confirmation, read
[evaluation discipline](evaluation.md). It owns matched conditions, attempt
accounting, sampling, grader handling, and fresh confirmation. Apply only the
measurement relevant to the question; a causal investigation need not acquire a
latency objective or an adoption campaign.

Explore a coherent multi-edit reconstruction when useful, but attribute its
result to the tested bundle until component-level contrasts support more. A
model's explanation or quotation of a rule is not causal evidence. Neither is
agreement among reviewers who share the proposed diagnosis.

After each contrast, state what it supports, weakens, or leaves unresolved before
editing again. Repeated wording changes without new discrimination require a
different contrast, not stronger admonitions. Follow evidence of a non-textual
cause rather than forcing a prompt fix; do not substitute an unrequested runtime
redesign for the requested textual attribution.

## Verify the source change and conclude

Source changes and qualification below apply only when authorized. Otherwise
return the supported diagnosis or proposed change without performing it. An
analysis experiment is not source-adoption permission.

Prefer the smallest supported clarification, deconfliction, relocation, deletion,
or restructuring over accumulating rules. Make an authorized candidate in the
owning textual source, not only in a captured request, and verify its rendered
and loaded form. Restore the native execution task and unchanged acceptance
criteria; a label-only probe, correct explanation, or correct first action cannot
qualify completed execution. Test successful controls and opposing obligations
that the edit could damage. A diagnostic deletion is not adoptable merely because
the selected failure disappears.

Keep attribution, candidate qualification, and adoption authority separate. A
candidate can qualify with its mechanism unresolved; that does not finish a
requested explanation. Stop when the requested decision and required checks are
satisfied, or report the exact missing evidence, invalid comparison, or exhausted
budget. No edit is a legitimate result; interrupted work is not verification.

Return a concise source-grounded finding: the implicated passage(s) and identity,
the decisive patch/comparison and observed outcomes, the supported contribution
and its scope, qualification and boundary coverage, and the disposition or next
discriminating test. Distinguish observation, association, experimental
contribution, and mechanism. Keep private traces in the task's existing evidence
store; do not copy them into reusable skills. Do not replace a requested patch or
PR with another method document.
