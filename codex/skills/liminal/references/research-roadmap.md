# Research Roadmap

## Table of Contents

1. Study sequence
2. Witness discipline
3. Source packs by stage
4. Project ladder
5. Evidence of mastery
6. Frontier questions

## Study sequence

1. Learn the semantic core: evaluation contexts, prompts, `shift/reset`, `control/prompt`.
2. Learn the translation core: CPS, meta-continuations, answer-type modification.
3. Learn the first-orderization core: defunctionalization, typed variants, refunctionalization.
4. Learn the machine core: evaluator-to-machine derivation and explicit control representations.
5. Learn the engineering core: runtime strategies, one-shot versus multi-shot, benchmark design.
6. Learn the proof core: typed CPS proofs, mechanized control calculi, or type-preserving defunctionalization.

## Witness discipline

At each stage, keep one witness notebook entry:

- `semantic core`: one operator-separating witness such as static versus dynamic extent
- `translation core`: one term whose evaluation order or answer type survives the translation
- `first-orderization core`: one evaluator trace and its matching machine trace
- `engineering core`: one workload that stresses capture or resume cost under an explicit contract
- `proof core`: one theorem target plus one counterexample the theorem should rule out

## Source packs by stage

- `semantic core`: `[DC-FP-1988]`, `[DC-AC-1990]`, `[DC-DYN-2005]`
- `translation core`: `[DC-MONAD-1994]`, `[DC-MFDC-2007]`, `[DC-STC-2004]`
- `first-orderization core`: `[DEF-DN-2001]`, `[DEF-AGER-2003]`, `[DEF-REFUNC-2007]`
- `engineering core`: `[DC-DIRECT-2002]`, `[OCAML-RETROEFF-2021]`, `[RT-FOLKLORE-2020]`
- `proof core`: `[DEF-DT-2023]`, `[TYPE4D-2022]`, `[TYPE4D-ARTIFACT]`

## Project ladder

- build a small-step evaluator with `shift/reset` and `prompt/control`
- add a CPS transformation and differential checks
- defunctionalize continuations and derive an abstract machine
- compare two runtime strategies on a benchmark suite
- mechanize one nontrivial theorem or translation
- maintain a witness notebook alongside the bibliography
- attach a citation ledger to each project milestone instead of letting the bibliography drift

## Evidence of mastery

Treat these as the threshold signals for "top-of-field capable":

- derive a CPS translation instead of only quoting one
- explain the `shift/reset` versus `control/prompt` difference with a real witness
- derive a machine from an evaluator via CPS plus defunctionalization
- defend a runtime choice with measurements
- complete one mechanized artifact or proof-driven reproduction
- name the exact sources that justify each of those moves

## Frontier questions

- fast mainstream support for delimited control in production compilers
- typed control beyond classic answer-type modification systems
- modular or separately compiled defunctionalization
- selective CPS and mixed-mode compilation
- verified translations between effect handlers and delimited control
