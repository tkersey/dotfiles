# OCaml `delimcc` Multi-Prompt Witness

This is a library-specific sketch. Check current package availability and exact API before presenting it as runnable code.

## Distinction

A multi-prompt library needs prompt identity. Capturing under prompt `p` must not capture through prompt `q` unless the API explicitly targets `q`.

## Witness shape

```ocaml
(* Pseudocode shape inspired by multi-prompt delimited-control APIs. *)
let p = new_prompt ()
let q = new_prompt ()

push_prompt p (fun () ->
  before_p ();
  push_prompt q (fun () ->
    before_q ();
    shift0 q (fun k -> resume_only_q k));
  after_p ())
```

## What the answer must show

- Which prompt identity is targeted.
- What context fragment is captured.
- Why a single global delimiter model would be too weak for modular code.

Source anchors: `[OCAML-DELIMCC-2010]`, `[OCAML-DELIMCC-2012]`, `[DC-MFDC-2007]`.
