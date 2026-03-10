# Foundations

## Table of Contents

1. Formal vocabulary
2. Minimum citation bundle
3. Core reduction schemas
4. Why the extra delimiter matters
5. Correctness targets

## Formal vocabulary

- `Continuation`: the rest of the computation from a program point, modeled denotationally, with evaluation contexts, or with an abstract machine.
- `Delimiter` or `prompt`: a marker that bounds how much continuation may be captured or aborted.
- `Delimited continuation`: the captured slice of continuation up to the nearest relevant delimiter.
- `Evaluation context`: the grammar of single-hole contexts that determines where reduction occurs and what gets captured.
- `CPS transformation`: a meaning-preserving translation that makes control flow explicit by passing continuations.
- `Defunctionalization`: the whole-program transformation that replaces higher-order function values with first-order tags plus an `apply` dispatcher.
- `Correctness`: usually stated as simulation, semantic preservation, type preservation, contextual equivalence, or machine-evaluator correspondence.

## Minimum citation bundle

- `[DC-FP-1988]`: prompts as delimiters, operational-equivalence repair, and prompt-motivated examples.
- `[DC-AC-1990]`: canonical `shift/reset` rules and CPS framing.
- `[DC-DYN-2005]` and `[DC-STC-2004]`: static versus dynamic extent, BFS witness, and dynamic-control translations.
- `[DEF-DN-2001]` and `[DEF-AGER-2003]`: correctness vocabulary for defunctionalization and machine correspondence.

## Core reduction schemas

Use these as the canonical contrast when a prompt asks about static versus dynamic delimited control:

```text
(reset v) -> v
(reset E[shift k . e]) -> (reset ((lambda k. e) (lambda x. reset E[x])))

(prompt v) -> v
(prompt E[control k . e]) -> (prompt ((lambda k. e) (lambda x. E[x])))
```

Use `[DC-AC-1990]` for the `shift/reset` rule family and pair it with `[DC-FP-1988]`, `[DC-DYN-2005]`, or `[DC-STC-2004]` when the question turns on prompt-centered behavior.
Do not quote the rules without explaining the operational consequence.

## Why the extra delimiter matters

- In `shift/reset`, the captured continuation is reinstalled under `reset`, so resumed work remains delimited. Cite `[DC-AC-1990]` for the canonical rule and `[DC-STC-2004]` when the prompt turns into an expressiveness or translation question.
- In `control/prompt`, the resumed continuation is not automatically re-delimited in the same way, which changes dynamic extent and compositional behavior. Use `[DC-FP-1988]` for prompts as delimiters and `[DC-DYN-2005]` for the dynamic-extent witness.
- This difference is not cosmetic. It appears in non-toy examples such as breadth-first traversal and in the translation discipline needed for dynamic control.

## Correctness targets

When the user asks whether a transformation or implementation is "correct", choose the right notion:

- `semantic preservation`: source and target produce the same observable result
- `simulation`: each source reduction corresponds to one or more target reductions
- `type preservation`: typing is maintained across the translation
- `machine correspondence`: the defunctionalized machine matches the evaluator or CPS-transformed source
- `contextual equivalence`: source programs remain indistinguishable in all contexts

Use `[DEF-DN-2001]` for transformation-level correctness claims and `[DEF-AGER-2003]` for evaluator-to-machine correspondence.
