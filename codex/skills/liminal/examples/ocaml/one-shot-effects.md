# OCaml One-Shot Effects Witness

This is a witness sketch, not a version-pinned OCaml program. Check the current OCaml manual before presenting exact syntax.

## Distinction

A multi-shot delimited continuation can be resumed more than once. OCaml effects expose continuations with a one-shot discipline, so a second resume of the same continuation is outside the intended contract.

## Witness shape

```ocaml
(* Pseudocode shape. Verify syntax against the current OCaml manual. *)
let saved = ref None

try
  perform Choose
with effect Choose k ->
  saved := Some k;
  continue k true;
  continue k false  (* the witness question: allowed, rejected, or requires cloning? *)
```

## What the answer must say

- Whether the continuation is one-shot or multi-shot.
- Whether the runtime rejects reuse, clones continuation state, or exposes only a linear-use contract.
- Which workloads are invalidated by one-shot use, such as search that resumes the same continuation many times.

Source anchors: `[OCAML-MANUAL]`, `[OCAML-RETROEFF-2021]`, `[RT-ONE-SHOT-1996]`.
