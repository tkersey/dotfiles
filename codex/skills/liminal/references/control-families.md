# Control Families

## Table of Contents

1. Operator map
2. Static versus dynamic extent
3. Subcontinuations and zero operators
4. Typing pressure points
5. When to bring in adjacent topics

## Operator map

- `prompts`: delimit continuation capture and make control local; use `[DC-FP-1988]` and `[RKT-GUIDE]`.
- `shift/reset`: the canonical static delimited-control pair; use `[DC-AC-1990]`.
- `control/prompt`: dynamic delimited control with different reinstatement behavior; use `[DC-DYN-2005]` and `[DC-STC-2004]`.
- `multi-prompt control`: first-class prompt tags and meta-continuation structure for typed and modular settings; use `[DC-MFDC-2007]`, `[RKT-REF]`, and `[OCAML-DELIMCC-2012]`.
- `effect handlers`: adjacent structured control surface that often reuses delimited-continuation intuitions; use `[OCAML-MANUAL]` and `[OCAML-RETROEFF-2021]`.

## Static versus dynamic extent

Use this comparison when the prompt asks whether two operator families are "the same":

- `shift/reset`:
  - static delimitation
  - resumed computation is re-delimited
  - commonly explained through extended CPS with meta-continuations
- `control/prompt`:
  - dynamic extent matters directly
  - resumed computation is not wrapped in the same extra delimiter
  - useful for examples where the dynamic stack discipline itself matters

Good answer pattern:

1. show the reduction contrast
2. state the behavioral consequence
3. point to a non-toy witness such as BFS
4. if needed, lift that witness into a translation or runtime consequence

Use `[DC-DYN-2005]` for the BFS witness and `[DC-STC-2004]` when the prompt asks about expressiveness or CPS relations.
Use `references/witness-programs.md` when you need a teaching-ready separating example instead of a bare claim.

## Subcontinuations and zero operators

- `[DC-MFDC-2007]` is the core citation for typed prompt and subcontinuation APIs such as `newPrompt`, `pushPrompt`, `withSubCont`, and `pushSubCont`.
- `[DC-0OPS-2005]` is the right paper when the prompt turns to `shift0`, `control0`, or the claim that static and dynamic operators are macro-expressible in one another.
- `[RKT-REF]` is the practical operator surface for `shift0`, `reset0`, `prompt0`, and adjacent control operators.
- Use zero operators only when the prompt actually asks about stripped delimiters, explicit subcontinuations, or operator-library correspondences.

## Typing pressure points

- `answer-type modification`: central for typed delimited control; do not ignore it when a prompt asks about typing or embedding
- `prompt typing`: multi-prompt systems often need prompt tags with typed boundaries
- `one-shot versus multi-shot`: this is a semantic and implementation distinction, not just a performance tweak
- `effects versus continuations`: effect handlers can be described through delimited control, but the mapping must name the handler discipline and runtime constraints

Use `[DC-MFDC-2007]`, `[TYPE4D-2022]`, and `[OCAML-MANUAL]` when the prompt makes the type or one-shot surface explicit.

## When to bring in adjacent topics

Bring in CPS, handlers, or prompt hierarchies when they make one of these tasks easier:

- comparing expressiveness across operator families
- deriving a type discipline
- explaining a runtime strategy
- translating a high-level semantics into a machine or implementation

Keep the answer narrower when the user only wants a local semantic fact.
If the prompt is pedagogical, prefer one witness from `references/witness-programs.md` before widening the scope.
