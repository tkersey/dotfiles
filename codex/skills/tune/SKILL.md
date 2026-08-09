---
name: tune
description: "Diagnose the smallest evidence-backed change that would improve an existing Codex skill's future decisions. Use for intended-vs-observed behavior, missed or false activation, ceremonial activation, wrong routing, ignored clauses, outcome regressions, repeated workarounds, progressive-disclosure defects, and explicit $refine handoff. Stop at audit or proposal unless apply or publication is explicit."
---
# Tune

## Mission

Compare an intended decision contract with observed decision episodes and
outcomes, then name the smallest change expected to alter future decisions.

```text
activation evidence -> was the skill present?
decision evidence   -> what changed because of it?
outcome evidence    -> was that change useful?
```

`$tune` diagnoses. `$refine` alone edits the skill package.

## Common path

1. Bind the exact target skill, artifact state, evidence window, and user
   objective.
2. Recover intended behavior from the current package.
3. Obtain observed behavior through the owning `$seq` definition or a supplied
   `$shadow` STE packet.
4. Classify one primary gap.
5. State the expected decision delta and the weakest intervention that could
   produce it.
6. Name a behavioral observation that can falsify the proposal.
7. Stop at proposal unless package mutation is explicitly authorized.

## Gap classes

Use the narrowest truthful class:

```text
missed-activation
false-activation
ceremonial-activation
wrong-route
ignored-clause
authority-leak
stopping-defect
proof-defect
outcome-regression
progressive-disclosure
no-skill-defect
insufficient-evidence
```

`progressive-disclosure` includes any of:

- the ordinary route requires loading deep material;
- a conditional resource lacks a direct link or adjacent loading predicate;
- a near-miss request loads expensive or irrelevant context;
- parent kernels contain worker-only procedure;
- kernel and resource duplicate the same full treatment;
- a resource is orphaned or unreachable.

Do not diagnose a disclosure defect from line count alone. Name the decision or
context consequence.

## Conditional disclosure

The complete pre-split contract is preserved byte-for-byte in
[FULL_CONTRACT.md](FULL_CONTRACT.md). Do not load it for ordinary diagnosis.
Load it only for exact STE/SDC schemas, passive Seq definition mechanics,
historical compatibility, apply/publication procedure, or an unported edge
case. Its frontmatter is archived source, not another skill definition.

## Handoff

A `$refine` handoff must carry:

```text
target skill and artifact state
evidence-backed gap
expected decision delta
smallest admissible intervention
must-preserve behavior
named post-change observation
explicit apply authority, when present
```

Never turn a plausible diagnosis into an edit merely because `$refine` is
available.
