# Witness Programs

Use this file when an answer needs a concrete separating example rather than only a taxonomy.
Pick the smallest witness that forces the distinction, then attach the source IDs from `references/sources.md`.

## Table of Contents

1. Static versus dynamic extent
2. Multi-prompt separation
3. Answer-type pressure
4. One-shot versus multi-shot resumption
5. Evaluator-to-machine correspondence
6. Analogy boundaries

## Static versus dynamic extent

- Use when: comparing `shift/reset` with `control/prompt` or explaining why delimiter reinstatement matters.
- Minimal witness shape: a captured continuation resumed in a context where re-delimitation changes the observable behavior, or a BFS-style traversal witness.
- What to show:
  - where the delimiter sits
  - whether resumed work stays under that delimiter
  - one behavioral difference such as traversal order or nested-resume behavior
- Source anchors: `[DC-AC-1990]`, `[DC-DYN-2005]`, `[DC-STC-2004]`

## Multi-prompt separation

- Use when: prompt tags, subcontinuations, or modular control libraries are central.
- Minimal witness shape: two prompt identities where capture under one boundary must not cross the other.
- What to show:
  - the prompt identity or tag that matters
  - what continuation fragment each prompt may capture
  - why a single undifferentiated delimiter story is too weak
- Source anchors: `[DC-MFDC-2007]`, `[RKT-REF]`, `[OCAML-DELIMCC-2012]`

## Answer-type pressure

- Use when: typed embeddings, CPS typing, or language support such as Scala `@cps` are under discussion.
- Minimal witness shape: a computation whose captured continuation changes the surrounding answer type or forces that change to be made explicit.
- What to show:
  - the source answer type versus the continuation answer type
  - where the type pressure appears in the operator or API surface
  - whether the host language hides or exposes the change
- Source anchors: `[DC-MFDC-2007]`, `[TYPE4D-2022]`, `[SCALA-CONT-DOC]`

## One-shot versus multi-shot resumption

- Use when: comparing effect handlers with multi-shot delimited continuations or defending a runtime strategy.
- Minimal witness shape: resume the same captured continuation twice, or explain why the workload would need cloning to make sense.
- What to show:
  - whether the continuation may be reused
  - whether the runtime enforces linear use, traps, or clones
  - what that means for search, generators, or repeated suspension
- Source anchors: `[RT-ONE-SHOT-1996]`, `[OCAML-MANUAL]`, `[OCAML-RETROEFF-2021]`

## Evaluator-to-machine correspondence

- Use when: the prompt asks for an abstract machine, defunctionalized continuations, or proof of correspondence.
- Minimal witness shape: one small source term with an evaluator trace and the matching machine-state trace.
- What to show:
  - the continuation shape before defunctionalization
  - the first-order constructor or machine frame after defunctionalization
  - the step where closure conversion or environment reification matters
- Source anchors: `[DEF-DN-2001]`, `[DEF-AGER-2003]`, `[DEF-REFUNC-2007]`

## Analogy boundaries

- Use when: the prompt compares delimited continuations with generators, `async` or `await`, or effect handlers.
- Minimal witness shape: a scenario that needs arbitrary delimited-context capture rather than coroutine-style suspension or single-shot resumption.
- What to show:
  - what the adjacent abstraction does provide
  - what control capability it does not provide directly
  - whether the relation is semantic equivalence, compilation strategy, or only a teaching analogy
- Source anchors: `[JS-GEN]`, `[JS-ASYNC]`, `[OCAML-MANUAL]`, plus the relevant core control source
