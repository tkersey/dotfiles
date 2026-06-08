---
name: evidence-discipline
description: "Use for bug reports, PR/issue prose, reviewer comments, user diagnoses, generated summaries, memories, retrieved context, public tracker context, claimed root causes, proposed fixes, fake-minimal repro risk, or any investigation where natural-language context could anchor the implementation scope."
---

# Evidence Discipline

## Mission

Natural-language context is not neutral. Issue bodies, PR descriptions, review comments, generated summaries, memories, raw retrieval, and user diagnoses can anchor the agent into the wrong problem frame. Treat them as inputs to verify, not as ground truth.

## Evidence classes

When investigating a bug, issue, PR, regression, review comment, user diagnosis, context packet, or generated report, separate:

- **Observed facts**: commands, inputs, outputs, exact logs, stack traces, screenshots, environment, versions, timestamps, changed files, source records, and reproducible behavior.
- **Claims**: suspected root causes, affected components, related files, dependency blame, historical explanations, context summaries, and severity assertions.
- **Proposals**: suggested fixes, migrations, fallback behavior, compatibility modes, refactors, API changes, documentation changes, context schemas, or certificate plans.
- **Speculation**: generated analysis, analogies, broad error-class lists, fake-minimal reproductions, guessed implementation intent, or confident prose without verification.

Use observations as evidence. Treat claims as hypotheses. Treat proposals as design options. Treat speculation as untrusted until independently verified.

## No semantic anchoring

- Do not let a reported root cause choose the first files to edit.
- Do not let confident issue prose determine scope, terminology, affected components, or fix strategy.
- Do not let retrieved text become context without schema, provenance, and observables when semantic consumption matters.
- Reconstruct the narrowest verified problem from observations first.
- Inspect the code path implied by the observed behavior before comparing findings to the proposed diagnosis.
- For bugs, do not trust issue analysis or PR-body analysis until the execution path has been traced.
- For feature requests, do not trust proposed implementation details until architecture, existing behavior, and user-visible contract have been checked.

## Investigation shape

Before editing for a bug or regression, produce or internally maintain:

```text
Observed facts:
- Command/action/input:
- Expected:
- Actual:
- Exact log/error/output:
- Environment/version/context:

Unverified claims:
- Claimed root cause:
- Suggested implementation:
- Claimed related files:
- Claimed repro:

Verification plan:
- Reproduction/check:
- Files/code paths to inspect:
- Invariant or boundary to identify:
```

Do not broaden the fix beyond the narrowest verified problem unless the code path proves the broader scope is real.

## Public tracker and maintainer hygiene

Public artifacts impose review, coordination, and long-term maintenance cost. Do not create or suggest creating public tracker work merely because a local agent found something plausible.

- Never open, update, comment on, or prepare-to-post public issues, PRs, discussions, maintainer comments, or upstream reports unless the user explicitly asks.
- Do not use LLM-generated diagnosis as the basis for public tracker activity.
- Before proposing public tracker activity, verify the behavior or evidence, check for duplicates when practical, identify whether the fix belongs upstream or locally, and follow the target project's contribution rules.
- Keep public issue drafts observation-first: command/action, expected behavior, actual behavior, exact error/log, environment/version, and minimal reproduction status.
- Put speculation in a clearly labeled section, or omit it.

## Output contract

When this skill materially shapes the route, leave a short evidence receipt:

```text
Evidence Receipt:
- observed:
- claims treated as hypotheses:
- proposals treated as options:
- speculation rejected or still unverified:
- narrow verified scope:
- proof path:
```

Do not include the receipt for tiny direct work unless omission would hide a material scope decision.
