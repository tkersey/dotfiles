# Claim Map

Use this file to choose citations before writing a theory-heavy answer. Start here, then pull exact titles and links from `references/sources.md`. For machine-readable source boundaries, consult `references/sources.yml`.

Before picking sources, pick the smallest separating witness from `references/witness-programs.md` that forces the distinction you need.

## Semantics and operator comparison

- Claim: prompts delimit control and repair the earlier control-calculus mismatch.
  - Sources: `[DC-FP-1988]`
  - Do not lean on: `[JS-GEN]`, `[JS-ASYNC]`
- Claim: `shift/reset` re-delimits resumed work, while `control/prompt` does not.
  - Sources: `[DC-AC-1990]`, `[DC-DYN-2005]`, `[DC-STC-2004]`
  - Good witness: BFS or nested-resumption behavior from `[DC-DYN-2005]`
- Claim: delimiter hierarchies or prompt families matter.
  - Sources: `[DC-HIER-1990]`, `[DC-MFDC-2007]`, `[RKT-REF]`

## Translation and machines

- Claim: delimited continuations support reflection and reification of monads.
  - Sources: `[DC-MONAD-1994]`
- Claim: standard CPS is enough for common delimited-control operator families.
  - Sources: `[DC-MFDC-2007]`, `[DC-STC-2004]`
- Claim: derive the machine from the evaluator instead of inventing it.
  - Sources: `[DEF-AGER-2003]`, `[DEF-DN-2001]`
  - Good witness: one evaluator trace and one matching machine trace
  - Watchout: include closure conversion when functions and environments must be made explicit.
- Claim: move back from machine code to higher-order structure.
  - Sources: `[DEF-REFUNC-2007]`

## Defunctionalization and typing

- Claim: defunctionalization is a whole-program higher-order to first-order transformation.
  - Sources: `[DEF-DN-2001]`
- Claim: the broader origin story starts from definitional interpreters.
  - Sources: `[DEF-REYNOLDS-1972]`
- Claim: type-preserving or dependently typed defunctionalization is available.
  - Sources: `[DEF-DT-2023]`
- Claim: there is a checked artifact for four delimited-control operator families.
  - Sources: `[TYPE4D-2022]`, `[TYPE4D-ARTIFACT]`
  - Watchout: use the paper for theory claims and the repository for artifact layout.

## Implementation and benchmarking

- Claim: `shift/reset` can be implemented directly rather than encoded through `call/cc`.
  - Sources: `[DC-DIRECT-2002]`, `[DC-DIRECT-2009]`
- Claim: one-shot continuations expose a real implementation opportunity.
  - Sources: `[RT-ONE-SHOT-1996]`, `[OCAML-MANUAL]`, `[OCAML-RETROEFF-2021]`
  - Good witness: resume the same continuation twice and state whether the surface forbids, traps, or clones it.
- Claim: modern implementation comparisons should be benchmark-backed rather than folklore-backed.
  - Sources: `[RT-FOLKLORE-2020]`, `[OCAML-RETROEFF-2021]`
- Claim: OCaml effects are adjacent to delimited control but come with one-shot and operational constraints.
  - Sources: `[OCAML-MANUAL]`, `[OCAML-RETROEFF-2021]`

## Adjacent surfaces and non-equivalences

- Claim: `delimcc` is the classic OCaml multi-prompt surface.
  - Sources: `[OCAML-DELIMCC-2010]`, `[OCAML-DELIMCC-2012]`
- Claim: Scala continuations rely on a historical compiler-plugin CPS transform with answer-type modification.
  - Sources: `[SCALA-CONT]`, `[SCALA-CONT-DOC]`
- Claim: JavaScript generators and `async`/`await` are analogies or compilation targets, not semantic equivalents.
  - Sources: `[JS-GEN]`, `[JS-ASYNC]`
  - Good witness: a control scenario that needs capture of an arbitrary delimited context rather than coroutine-style suspension.
- Claim: zero operators or subcontinuations matter.
  - Sources: `[DC-0OPS-2005]`, `[DC-MFDC-2007]`, `[RKT-REF]`
