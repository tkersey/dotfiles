# Language Examples

## Table of Contents

1. Racket and Scheme
2. OCaml
3. Haskell
4. Scala
5. JavaScript

## Racket and Scheme

- Racket is the clearest production environment for prompts, aborts, and composable continuations.
- Use `[RKT-GUIDE]` for the prompt-and-abort mental model and `[RKT-REF]` for the exact operator surface.
- Use it for operational demonstrations, especially when the user wants to see prompt behavior instead of only paper rules.
- Scheme standards are useful as the baseline full-continuation story that delimited control refines.

## OCaml

- `delimcc` is the classic library-level multi-prompt reference in a strict typed language; use `[OCAML-DELIMCC-2010]` or `[OCAML-DELIMCC-2012]`.
- OCaml 5 effect handlers are the mainstream adjacent runtime surface for continuation-based control; use `[OCAML-MANUAL]` for semantics and limitations and `[OCAML-RETROEFF-2021]` for runtime evidence.
- Name the one-shot and no-effect-safety constraints when you compare OCaml effects with general multi-shot delimited continuations.
- Use OCaml when the prompt asks about typed embeddings, runtime tradeoffs, effects, or practical systems engineering.

## Haskell

- Use Haskell for typed CPS discussions, multi-prompt frameworks, and abstraction-heavy encodings.
- `[DC-MFDC-2007]` is the main source-backed entry point here.
- It is a strong fit for monadic or type-directed accounts of delimited continuations.

## Scala

- Scala continuations are now a historical compiler-plugin surface rather than a current mainstream feature; use `[SCALA-CONT]` for ecosystem status and `[SCALA-CONT-DOC]` for the API surface.
- The important sharp edge is answer-type modification through `@cps` and `@cpsParam`, not the archived plugin alone.
- Use Scala when the user asks about compiler-plugin CPS transforms, historical language support, or answer-type-modifying APIs.

## JavaScript

- JavaScript does not standardize `shift/reset`, but generators and `async`/`await` are useful compilation targets and pedagogical analogues; use `[JS-GEN]` and `[JS-ASYNC]`.
- Be explicit that they are structured suspension abstractions, not drop-in semantic equivalents.
- Generators preserve local state across re-entry; `async` and `await` route through promises and microtasks.
- Use JavaScript when the prompt asks how to compile or explain the ideas in a ubiquitous runtime.
