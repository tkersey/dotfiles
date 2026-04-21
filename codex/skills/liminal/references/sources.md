# Sources

Use these as the primary citation surface. Prefer DOI landings, official manuals, maintained project pages, and checked artifacts over brittle direct-PDF links. Use the `Use for` note to stay inside the safe claim surface, and browse live primary docs when the prompt is time-sensitive.

## Delimited control

- `[DC-FP-1988]` Felleisen, "The Theory and Practice of First-Class Prompts" (1988)
  - Canonical: https://doi.org/10.1145/73560.73576
  - Accessible copy: https://www.cs.tufts.edu/~nr/cs257/archive/matthias-felleisen/prompts.pdf
  - Use for: prompts as delimiters, operational-equivalence repair, and prompt-motivated examples.
- `[DC-AC-1990]` Danvy and Filinski, "Abstracting Control" (1990)
  - Canonical: https://doi.org/10.1145/91556.91622
  - Use for: the canonical `shift/reset` rule family and CPS framing.
- `[DC-HIER-1990]` Sitaram and Felleisen, "Control Delimiters and Their Hierarchies" (1990)
  - Canonical: https://doi.org/10.1007/BF01806126
  - Accessible copy: https://www2.ccs.neu.edu/racket/pubs/lasc1990-sf.pdf
  - Use for: delimiter hierarchies and why unrestricted `call/cc` is often too strong.
- `[DC-MONAD-1994]` Filinski, "Representing Monads" (1994)
  - Canonical: https://doi.org/10.1145/174675.178047
  - Accessible copy: https://www.cs.tufts.edu/~nr/cs257/archive/andrzej-filinski/RM.ps
  - Use for: reflection and reification, and the classic direct-style-via-delimited-control story.
- `[DC-MFDC-2007]` Dybvig, Peyton Jones, and Sabry, "A Monadic Framework for Delimited Continuations" (2007)
  - Canonical: https://doi.org/10.1017/S0956796807006259
  - Official page: https://www.microsoft.com/en-us/research/publication/a-monadic-framework-for-delimited-continuations/
  - Use for: typed prompt and subcontinuation APIs, standard CPS sufficiency, and `runCC`-style encapsulation.
- `[DC-DYN-2005]` Biernacki, Danvy, and Shan, "On the Dynamic Extent of Delimited Continuations" (2005)
  - Canonical: https://doi.org/10.1016/j.ipl.2005.04.003
  - Extended report: https://doi.org/10.7146/brics.v12i13.21879
  - Use for: the static-versus-dynamic distinction and the BFS witness.
- `[DC-STC-2004]` Shan, "Shift to Control" (2004)
  - Primary source: https://homes.luddy.indiana.edu/ccshan/recur/recur.pdf
  - Use for: expressiveness and CPS relations between static and dynamic delimited control.
- `[DC-DIRECT-2002]` Gasbichler and Sperber, "Final shift for call/cc: direct implementation of shift and reset" (2002)
  - Canonical: https://doi.org/10.1145/581478.581504
  - Use for: direct runtime implementation of `shift/reset` without simulating them through `call/cc`.
- `[DC-DIRECT-2009]` Masuko and Asai, "Direct implementation of shift and reset in the MinCaml compiler" (2009)
  - Canonical: https://doi.org/10.1145/1596627.1596636
  - Use for: compiler-level direct implementation in an ML-family setting.
- `[DC-0OPS-2005]` Kiselyov, "How to remove a dynamic prompt: static and dynamic delimited continuation operators are equally expressible" (2005)
  - Primary source: https://okmij.org/ftp/continuations/impromptu-shift-tr.pdf
  - Use for: `shift0`, `control0`, and operator-family macro-expressibility.

## Defunctionalization and machines

- `[DEF-REYNOLDS-1972]` Reynolds, "Definitional Interpreters for Higher-Order Programming Languages" (1972)
  - Canonical: https://doi.org/10.1145/800194.805852
  - Use for: the definitional-interpreter origin story and constructive variation between interpreter styles.
- `[DEF-DN-2001]` Danvy and Nielsen, "Defunctionalization at Work" (2001)
  - Canonical: https://doi.org/10.1145/773184.773202
  - Open report: https://doi.org/10.7146/brics.v8i23.21684
  - Use for: defunctionalization as a whole-program transformation and proof-structure transfer.
- `[DEF-AGER-2003]` Ager, Biernacki, Danvy, and Midtgaard, "A Functional Correspondence between Evaluators and Abstract Machines" (2003)
  - Canonical: https://doi.org/10.1145/888251.888254
  - Open report: https://doi.org/10.7146/brics.v10i13.21783
  - Use for: evaluator-to-machine derivation through closure conversion, CPS, and defunctionalization.
- `[DEF-REFUNC-2007]` Danvy and Millikin, "Refunctionalization at Work" (2007)
  - Canonical: https://doi.org/10.1016/j.scico.2007.10.007
  - Open report: https://doi.org/10.7146/brics.v14i7.21930
  - Use for: the left-inverse story and repair heuristics for almost-defunctionalized programs.

## Typed and mechanized work

- `[DEF-DT-2023]` Huang and Yallop, "Defunctionalization with Dependent Types" (2023)
  - Canonical: https://doi.org/10.1145/3591241
  - Open version: https://doi.org/10.48550/arXiv.2304.04574
  - Use for: soundness and type preservation in a dependently typed defunctionalization setting.
- `[TYPE4D-2022]` Ishio and Asai, "Type System for Four Delimited Control Operators" (2022)
  - Canonical: https://doi.org/10.1145/3564719.3568691
  - Use for: a typed comparison across four delimited-control operator families.
- `[TYPE4D-ARTIFACT]` `type4d` Agda artifact
  - Repository: https://github.com/chiaki-i/type4d
  - Use for: the checked artifact and file layout, not as the primary theory citation.

## Official docs and implementation surfaces

- `[RKT-GUIDE]` Racket Guide: prompts and aborts
  - Official: https://docs.racket-lang.org/guide/prompt.html
  - Use for: the practical prompt and abort mental model.
- `[RKT-REF]` Racket Reference: continuations and control operators
  - Official: https://docs.racket-lang.org/reference/cont.html
  - Use for: exact operator names, prompt tags, composable continuations, and `racket/control` surfaces.
- `[OCAML-MANUAL]` OCaml manual: effect handlers
  - Official: https://ocaml.org/manual/effects.html
  - Use for: deep versus shallow handlers, one-shot linearity, and operational limitations.
- `[OCAML-RETROEFF-2021]` Sivaramakrishnan et al., "Retrofitting Effect Handlers onto OCaml" (2021)
  - Canonical: https://doi.org/10.1145/3453483.3454039
  - Official page: https://anil.recoil.org/papers/2021-pldi-retroeff
  - Use for: runtime design, microbenchmarks, and low-overhead retrofitting evidence.
- `[OCAML-DELIMCC-2010]` Kiselyov, "Delimited Control in OCaml, Abstractly and Concretely: System Description" (2010)
  - Canonical: https://doi.org/10.1007/978-3-642-12251-4_22
  - Use for: the published `delimcc` system description.
- `[OCAML-DELIMCC-2012]` Kiselyov, "Delimited control in OCaml, abstractly and concretely" (2012)
  - Canonical: https://doi.org/10.1016/j.tcs.2012.02.025
  - Use for: direct, typed, multi-prompt delimited control in OCaml without runtime changes.
- `[SCALA-CONT]` Scala continuations plugin repository
  - Project page: https://github.com/scala/scala-continuations
  - Use for: historical ecosystem status and archival context.
- `[SCALA-CONT-DOC]` Scala continuations package docs
  - API surface: https://raw.githubusercontent.com/scala/scala-continuations/master/library/src/main/scala/scala/util/continuations/package.scala
  - Use for: `reset`, `shift`, and answer-type modification via `@cps` and `@cpsParam`.
- `[JS-GEN]` MDN generators and `yield`
  - Official: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/function*
  - Official: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/yield
  - Use for: structured suspension, local-state preservation, and bidirectional control transfer.
- `[JS-ASYNC]` MDN `async function` and `await`
  - Official: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/async_function
  - Official: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/await
  - Use for: promise-based suspension and microtask resumption, not for delimited-control equivalence claims.

## Runtime evidence

- `[RT-ONE-SHOT-1996]` Bruggeman, Waddell, and Dybvig, "Representing Control in the Presence of One-Shot Continuations" (1996)
  - Canonical: https://doi.org/10.1145/231379.231395
  - Use for: the implementation opportunity exposed by one-shot continuations.
- `[RT-FOLKLORE-2020]` Farvardin and Reppy, "From Folklore to Fact: Comparing Implementations of Stacks and Continuations" (2020)
  - Canonical: https://doi.org/10.1145/3385412.3385994
  - Use for: comparative implementation methodology instead of folklore-driven benchmarking.

## Freshness notes

- Treat proposal status, library maintenance, and implementation availability as drift-prone.
- Treat runtime performance and library maintenance status as drift-prone even when the theory is stable.
- For drift-prone questions, browse primary sources before finalizing.
