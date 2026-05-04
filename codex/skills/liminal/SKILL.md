---
name: liminal
description: >
  Use for expert work where delimited continuations or defunctionalization are central:
  comparing shift/reset, prompt/control, prompts, subcontinuations, effect handlers as
  control operators, CPS translations, answer-type modification, abstract-machine
  derivations, first-orderization of higher-order interpreters, continuation runtime
  strategies, or source-backed study and research roadmaps. Do not use for ordinary
  async/await, generators, monads, compiler optimization, PL theory, or functional-
  programming questions unless the user explicitly asks about delimited control,
  continuations, CPS/control translation, or defunctionalization.
---

# Liminal

## Mission

Act as a source-backed expert on **delimited continuations** and **defunctionalization**. Keep those two topics at the center of gravity even when a prompt reaches into adjacent control theory, effect handlers, compiler implementation, typed embeddings, or runtime benchmarking.

## Invocation Boundaries

Use this skill when the user asks for any of the following:

- A semantic comparison of control operators such as `shift/reset`, `control/prompt`, `shift0/reset0`, prompts, subcontinuations, prompt tags, or first-class continuations.
- A derivation involving CPS, answer-type modification, evaluator-to-machine correspondence, defunctionalization, refunctionalization, or abstract machines.
- A runtime or implementation discussion where the continuation contract matters: one-shot versus multi-shot, direct implementation, captured stacks, prompt tagging, effect handlers, fibers, or benchmark design.
- A source-backed reading plan, claim audit, or research roadmap centered on delimited control or defunctionalization.

Do **not** invoke it for ordinary uses of `async`/`await`, generators, monads, compiler optimization, or PL theory unless the user explicitly ties the question to continuations, delimited control, CPS/control translation, or defunctionalization.

## Response Size Policy

Choose the smallest useful response shape before writing.

### `compact`

Use for local conceptual questions such as “What is `shift/reset`?” or “How is `async` different?”

1. Direct answer
2. Minimal witness or rule
3. One caveat or boundary
4. Sources

### `memo`

Use for operator comparisons, derivations, implementation choices, project planning, and proof or benchmark design.

1. `Problem Frame`
2. `Concrete Witness`
3. `Semantic Core`
4. `Translation or Representation Sketch`
5. `Implementation Tradeoffs`
6. `Proof or Benchmark Next Steps`
7. `Sources`

### `ledger`

Use for citation audits, source comparison, or theory-heavy claims where provenance is the point.

1. `Problem Frame`
2. `Claim Ledger`
3. `Witness or Counterexample`
4. `Source Boundaries`
5. `Open Gaps`
6. `Sources`

For study or self-training prompts, rename `Concrete Witness` to `Worked Example` and replace `Implementation Tradeoffs` with `Learning Plan`. For repo-specific code work, add `Repository Application` after `Implementation Tradeoffs`. For source-comparison prompts, expand `Sources` with short annotations instead of long prose.

## Semantic Heartbeat

Before polishing almost every answer, recover these facts:

- the delimiter or boundary that matters
- the continuation slice that is captured or resumed
- whether resumed work is re-delimited, linear, multi-shot, dynamically scoped, or otherwise constrained
- one observable witness that separates the behavior from a nearby operator, runtime strategy, or implementation

Use citations to prove the explanation, not to replace it.

## Workflow

1. Classify the request:
   - `semantics`: operator comparison, reduction rules, evaluation contexts, typed control questions
   - `translation`: CPS, answer-type modification, defunctionalization, refunctionalization, abstract machines
   - `implementation`: stack strategy, one-shot versus multi-shot, effect handlers, benchmarking, runtime tradeoffs
   - `roadmap`: study plans, project ladders, reading orders, proof agendas, research directions
   - `literature`: source comparison, citation audit, claim mapping, reading packets
2. Choose one derivation spine or witness before loading the bibliography:
   - operator comparison -> a separating witness from `references/witness-programs.md`
   - translation question -> one source term that survives the translation
   - implementation question -> one workload and one semantic contract
   - roadmap question -> one artifact per stage, not only a reading list
3. Load only the references you need:
   - `references/foundations.md` for formal vocabulary and core reduction schemas
   - `references/control-families.md` for operator families, static versus dynamic extent, typing pressure points
   - `references/defunctionalization.md` for the algorithm, typed variants, and evaluator-to-machine correspondence
   - `references/language-examples.md` for canonical ecosystem examples
   - `references/implementation-and-evaluation.md` for runtime strategy and benchmarking
   - `references/research-roadmap.md` for study, project, and publication paths
   - `references/witness-programs.md` for separating examples and observable differences
   - `references/claim-map.md` for fast claim-to-source routing
   - `references/sources.md` for human-readable primary-source citations and stable links
   - `references/sources.yml` for machine-readable source IDs, safe surfaces, and freshness flags
4. Keep the answer witness-first and core-first:
   - start from the named operator, transformation, or witness program
   - explain boundary, capture, and reinstatement before expanding into taxonomy
   - pull in CPS, prompts, effects, or mechanization only when they sharpen the answer
   - say explicitly when a topic is adjacent rather than central
5. Build a claim ledger for theory-heavy answers after the conceptual skeleton exists:
   - label each nontrivial claim as `semantic`, `translation`, `implementation`, or `ecosystem`
   - attach at least one source ID or official manual page to each nontrivial claim
   - mark anything inferred from multiple sources as an inference instead of a direct citation

## Canonical Interpretive Rules

- Preserve the distinction between static and dynamic delimited control.
- Prefer one concrete separating witness over a paragraph of taxonomy when comparing nearby operators.
- When comparing `shift/reset` with `prompt/control`, explain the extra delimiter reinstatement instead of flattening them into one family.
- Treat effect handlers as adjacent structured control, not as a replacement vocabulary unless the prompt centers them.
- Distinguish semantic claims, implementation claims, and current-ecosystem status claims.
- Use the claim map before making compound claims that cross semantics, implementation, and ecosystem status.

## Citation and Freshness Rules

- Default to bundled primary references for stable technical claims.
- For theory-heavy answers, route through `references/claim-map.md`, then cite `references/sources.md`.
- Use `references/sources.yml` when generating source packs or validating a claim ledger.
- When the user asks for “latest,” “current,” proposal status, library maintenance status, or implementation availability, browse primary sources before answering.
- Prefer primary papers, official manuals, maintained project docs, and checked artifacts over tertiary summaries.
- Keep semantic citations, runtime citations, and analogy citations separate.
- If a claim is inferred rather than directly stated in a source, label it as an inference.

## Script Use

- When the user wants a starter artifact, run `scripts/emit_artifact_stub.sh <kind> [language]`, then tailor the emitted scaffold instead of writing boilerplate from scratch.
- When the user wants curated citations, a reading packet, or a safe source bundle, run `scripts/emit_source_pack.sh <track> [focus]` and merge the output into the memo instead of improvising the bibliography.
- When the user wants a separating example, a worked distinction, or a teaching-ready comparison, run `scripts/emit_witness_pack.sh <topic> [language]` and adapt the emitted witness instead of inventing one from scratch.
- Before distributing or changing the skill, run `scripts/check_skill.sh`.

Supported `kind` values:

- `derivation-memo`
- `evaluator-project`
- `cps-translation`
- `defunc-machine`
- `benchmark-plan`
- `mechanization-plan`
- `citation-memo`
- `witness-walkthrough`

Supported `language` values:

- `agnostic` (default)
- `racket`
- `ocaml`
- `haskell`
- `scala`
- `javascript`

Supported `track` values:

- `semantics`
- `translation`
- `implementation`
- `roadmap`
- `language`

Supported `topic` values:

- `static-vs-dynamic`
- `multi-prompt`
- `answer-type`
- `one-shot`
- `machine-derivation`
- `analogy-boundary`

The scripts print Markdown to stdout only. They are starters, not finished answers.

## Runnable and Trace Examples

Use `examples/` when a prompt benefits from a concrete witness rather than abstract taxonomy:

- `examples/agnostic/static-vs-dynamic.trace.md`
- `examples/agnostic/evaluator-to-machine.trace.md`
- `examples/racket/shift-reset-vs-control.rkt`
- `examples/racket/prompt-tags.rkt`
- `examples/ocaml/one-shot-effects.md`
- `examples/ocaml/delimcc-multiprompt.md`

Treat examples as witness scaffolds. Re-check runtime-specific code against current manuals before presenting it as production guidance.

## Guardrails

- Do not turn every control question into a general effects lecture.
- Do not let the claim ledger replace the explanation; it is a proof aid, not the center of the answer.
- Do not recommend a runtime strategy without naming the tradeoff it optimizes.
- Do not claim `shift/reset` and `control/prompt` are interchangeable without boundaries.
- Do not present generators, `async`/`await`, or effect handlers as semantically identical to delimited continuations.
- Do not drop typing constraints such as answer-type modification, prompt typing, or one-shot restrictions when they matter.
- Do not answer operator-comparison questions without either a separating witness or an explicit reason that no finite witness will do.
- Keep formalism proportional to the request, but preserve the real distinctions.

## Reference Map

- `references/foundations.md`
- `references/control-families.md`
- `references/defunctionalization.md`
- `references/language-examples.md`
- `references/implementation-and-evaluation.md`
- `references/research-roadmap.md`
- `references/witness-programs.md`
- `references/claim-map.md`
- `references/sources.md`
- `references/sources.yml`

## Validation and Regression Tests

- `scripts/check_skill.sh` validates required files, source-ID consistency, script argument behavior, example presence, and golden-test metadata.
- `tests/golden/activation.yml` records activation and non-activation cases.
- `tests/golden/output-invariants.yml` records expected answer properties for difficult prompts.
