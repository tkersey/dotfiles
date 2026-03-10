# Implementation and Evaluation

## Table of Contents

1. Runtime strategy map
2. Benchmark families
3. Metrics and source discipline
4. Common tradeoff patterns

## Runtime strategy map

Use a source-backed strategy matrix instead of generic folklore:

| Strategy | Source IDs | Optimizes | Costs or boundaries |
| --- | --- | --- | --- |
| Direct `shift/reset` runtime | `[DC-DIRECT-2002]`, `[DC-DIRECT-2009]` | avoids `call/cc` encoding overhead and makes the operator primitive explicit | runtime or compiler complexity |
| Prompt-tag or subcontinuation APIs | `[DC-MFDC-2007]`, `[RKT-REF]`, `[OCAML-DELIMCC-2012]` | modular multi-prompt composition and typed boundaries | more API surface and prompt discipline |
| One-shot captured stacks or fibers | `[RT-ONE-SHOT-1996]`, `[OCAML-RETROEFF-2021]`, `[OCAML-MANUAL]` | cheap resume under a linear-use contract | single-use restrictions must be enforced |
| Comparative implementation studies | `[RT-FOLKLORE-2020]` | apples-to-apples evidence for stack and continuation strategies | benchmark design burden |

When recommending a strategy, always say what it optimizes:

- cheaper capture
- cheaper resume
- lower baseline overhead
- cleaner multi-prompt composition
- easier typing or linearity discipline

When you need a concrete runtime evidence anchor, `[OCAML-RETROEFF-2021]` is the strongest single citation in this corpus: it reports low baseline overhead on programs that do not use effects, phase-level continuation costs, and competitive web-server latency.

## Benchmark families

- `capture/resume loop`: isolates raw continuation overhead
- `generator-style workloads`: repeated suspend/resume
- `backtracking or nondeterminism`: many captures and resumes, space pressure
- `BFS versus DFS examples`: semantic distinction between operator families
- `effect-handler workloads`: handler dispatch plus resumption structure

Pair the workload with the semantic contract it assumes: one-shot or multi-shot, prompt tags or single delimiter, deep or shallow handlers, static or dynamic control.

## Metrics and source discipline

- wall-clock time with stable repeated measurement
- allocation and GC pressure
- capture cost versus stack depth
- resume cost
- one-shot versus multi-shot restrictions
- semantic overhead introduced by delimiter reinstatement or prompt tagging

Use `[RT-FOLKLORE-2020]` for comparative implementation methodology and `[OCAML-RETROEFF-2021]` for a concrete modern runtime case study.
Do not cite `[OCAML-MANUAL]`, `[RKT-REF]`, or `[JS-ASYNC]` for performance claims; use them for semantics and operational boundaries instead.

## Common tradeoff patterns

- Faster control operations often mean more runtime machinery.
- Simpler semantics often cost less explanation debt but can cost more performance.
- One-shot optimization is powerful only when the semantic contract can actually enforce single use.
- Effect handlers may simplify the user-facing surface while hiding a continuation strategy underneath.
- JavaScript generators and `async`/`await` are analogy or compilation-target surfaces, not direct evidence about delimited-continuation runtimes.
