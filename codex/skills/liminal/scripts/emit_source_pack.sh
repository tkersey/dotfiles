#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
Usage: emit_source_pack.sh <track> [focus]

Tracks:
  semantics
  translation
  implementation
  roadmap
  language

Focus values depend on the track. If omitted, a broad pack is emitted.
EOF
  exit 1
}

track="${1:-}"
focus="${2:-broad}"

[[ -n "$track" ]] || usage

case "$track" in
  semantics|translation|implementation|roadmap|language) ;;
  *) usage ;;
esac

emit_header() {
  cat <<EOF
# Source Pack

- Track: $track
- Focus: $focus

## Core Sources
EOF
}

emit_footer() {
  cat <<'EOF'

## Companion Files

- `references/witness-programs.md`
- `references/claim-map.md`
- `references/sources.md`

## Watchouts

- Separate semantic citations from runtime citations.
- Mark cross-source synthesis as an inference.
- Browse live primary docs when maintenance status or availability might have drifted.
EOF
}

case "$track:$focus" in
  semantics:broad|semantics:shift-reset)
    emit_header
    cat <<'EOF'
- `[DC-AC-1990]`: canonical `shift/reset` rules and CPS framing.
- `[DC-FP-1988]`: prompts as delimiters and operational-equivalence repair.
- `[DC-DYN-2005]`: static versus dynamic extent and the BFS witness.
- `[DC-STC-2004]`: expressiveness and CPS relations between static and dynamic control.

## Safe Claims

- `shift/reset` and `control/prompt` differ in delimiter reinstatement behavior.
- The difference shows up in real examples, not only toy rules.
- Prompt-centered explanations and reduction-rule explanations should usually travel together.
EOF
    emit_footer
    ;;
  semantics:control-prompt)
    emit_header
    cat <<'EOF'
- `[DC-FP-1988]`: prompts and prompt-motivated examples.
- `[DC-DYN-2005]`: dynamic-extent witness and BFS.
- `[DC-STC-2004]`: expressiveness relation to `shift/reset`.
- `[RKT-REF]`: practical operator surface in a living system.

## Safe Claims

- `control/prompt` should not be flattened into `shift/reset`.
- Dynamic extent is the center of gravity, not a footnote.
- Racket is the quickest practical surface for checking operator behavior.
EOF
    emit_footer
    ;;
  semantics:multi-prompt)
    emit_header
    cat <<'EOF'
- `[DC-MFDC-2007]`: typed prompt and subcontinuation APIs.
- `[OCAML-DELIMCC-2012]`: direct typed multi-prompt control in OCaml.
- `[RKT-REF]`: prompt tags and operator inventory.

## Safe Claims

- Multi-prompt control is a real API and typing design space, not only a paper convenience.
- Prompt tags and subcontinuation APIs are the right vocabulary for modular control libraries.
- Practical operator surfaces differ, so name the host language before generalizing.
EOF
    emit_footer
    ;;
  translation:broad|translation:defunctionalization)
    emit_header
    cat <<'EOF'
- `[DEF-DN-2001]`: defunctionalization as a whole-program transformation.
- `[DEF-AGER-2003]`: evaluator-to-machine derivation through closure conversion, CPS, and defunctionalization.
- `[DEF-REFUNC-2007]`: path back to higher-order structure.
- `[DEF-DT-2023]`: type-preserving dependent-type setting.

## Safe Claims

- Defunctionalization is more than "replace closures with tags" when proofs or machines matter.
- Machine derivations should name closure conversion when environments become explicit.
- Refunctionalization is the right companion when the question runs in the opposite direction.
EOF
    emit_footer
    ;;
  translation:abstract-machine)
    emit_header
    cat <<'EOF'
- `[DEF-AGER-2003]`: machine derivation pipeline.
- `[DEF-DN-2001]`: defunctionalized evaluation contexts and proof transfer.
- `[DC-MFDC-2007]`: typed prompt and subcontinuation structure when control operators are central.

## Safe Claims

- Derive the machine from the evaluator instead of designing it ad hoc.
- Keep the derivation chain explicit so correctness obligations stay visible.
- Pull in prompt or subcontinuation APIs only when the machine needs them.
EOF
    emit_footer
    ;;
  translation:mechanization)
    emit_header
    cat <<'EOF'
- `[DEF-DT-2023]`: type-preserving defunctionalization in a dependently typed setting.
- `[TYPE4D-2022]`: typed comparison across four delimited-control operator families.
- `[TYPE4D-ARTIFACT]`: checked artifact layout.

## Safe Claims

- Mechanization tasks need both the paper-level theorem story and the artifact-level entrypoint.
- Typed operator comparisons should cite the paper, not only the repository.
- If the proof obligation changes shape, mark it as a new inference instead of stretching an old theorem.
EOF
    emit_footer
    ;;
  implementation:broad|implementation:runtime)
    emit_header
    cat <<'EOF'
- `[DC-DIRECT-2002]`: direct `shift/reset` implementation.
- `[DC-DIRECT-2009]`: compiler-level direct implementation in MinCaml.
- `[RT-ONE-SHOT-1996]`: one-shot continuations as an implementation opportunity.
- `[RT-FOLKLORE-2020]`: comparative implementation methodology.

## Safe Claims

- Runtime advice should name what it optimizes: capture, resume, baseline overhead, or modularity.
- One-shot versus multi-shot is a semantic contract, not just a perf toggle.
- Comparative claims need benchmark evidence, not only folklore or one implementation anecdote.
EOF
    emit_footer
    ;;
  implementation:ocaml-effects)
    emit_header
    cat <<'EOF'
- `[OCAML-MANUAL]`: deep versus shallow handlers, one-shot linearity, operational limits.
- `[OCAML-RETROEFF-2021]`: runtime design and measured costs.
- `[OCAML-DELIMCC-2012]`: adjacent multi-prompt delimited-control surface in the same ecosystem.

## Safe Claims

- OCaml effects are adjacent to delimited continuations, not a synonym for them.
- The language-level manual and the runtime paper play different roles: semantics versus measured implementation.
- `delimcc` is the better citation when the question is really about multi-prompt delimited control.
EOF
    emit_footer
    ;;
  implementation:javascript-analogy)
    emit_header
    cat <<'EOF'
- `[JS-GEN]`: generators and `yield`.
- `[JS-ASYNC]`: `async` and `await` through promises and microtasks.

## Safe Claims

- Generators and `async` or `await` are structured suspension surfaces.
- They are good analogies or compilation targets, not direct semantic equivalents of delimited continuations.
- If the prompt needs true capture and reinstatement semantics, leave JavaScript and return to the control papers.
EOF
    emit_footer
    ;;
  roadmap:broad|roadmap:study)
    emit_header
    cat <<'EOF'
- `[DC-FP-1988]`, `[DC-AC-1990]`, `[DC-DYN-2005]`: semantic core.
- `[DC-MONAD-1994]`, `[DC-MFDC-2007]`: translation and typed-control core.
- `[DEF-DN-2001]`, `[DEF-AGER-2003]`, `[DEF-REFUNC-2007]`: first-orderization and machines.
- `[OCAML-RETROEFF-2021]`, `[RT-FOLKLORE-2020]`: implementation and benchmarking.
- `[DEF-DT-2023]`, `[TYPE4D-2022]`: proof and mechanization.

## Safe Claims

- A serious study path alternates semantics, translation, implementation, and proof.
- Each stage should end with a small artifact and a citation ledger.
- Runtime questions should arrive only after the semantic distinctions are stable.
EOF
    emit_footer
    ;;
  roadmap:publication)
    emit_header
    cat <<'EOF'
- `[DC-DYN-2005]`, `[DC-STC-2004]`: operator-family distinctions with real witnesses.
- `[DEF-AGER-2003]`, `[DEF-DT-2023]`: derivation and proof backbone.
- `[RT-FOLKLORE-2020]`, `[OCAML-RETROEFF-2021]`: measurement discipline.

## Safe Claims

- Publication-grade work usually needs one strong semantic result and one proof or measurement story.
- Use witness programs or checked artifacts, not only prose distinctions.
- Separate novelty claims from tutorial or systems-engineering claims.
EOF
    emit_footer
    ;;
  language:broad|language:racket)
    emit_header
    cat <<'EOF'
- `[RKT-GUIDE]`: prompt and abort mental model.
- `[RKT-REF]`: operator inventory and exact semantics.
- `[DC-FP-1988]`: prompt lineage.

## Safe Claims

- Racket is the quickest practical surface for operational demonstrations.
- The Guide gives intuition; the Reference gives the exact contract.
- Cite the papers when you need historical or theoretical framing.
EOF
    emit_footer
    ;;
  language:ocaml)
    emit_header
    cat <<'EOF'
- `[OCAML-DELIMCC-2012]`: direct typed multi-prompt control.
- `[OCAML-MANUAL]`: effect-handler semantics and limitations.
- `[OCAML-RETROEFF-2021]`: runtime evidence.

## Safe Claims

- OCaml splits the story between `delimcc` and effect handlers.
- One-shot limitations belong to the effect-handler surface, not to all delimited-control discussions.
- Runtime claims should lean on the retroeff paper rather than the manual.
EOF
    emit_footer
    ;;
  language:haskell)
    emit_header
    cat <<'EOF'
- `[DC-MFDC-2007]`: typed monadic framework and multi-prompt vocabulary.
- `[DC-MONAD-1994]`: reflection and reification background.

## Safe Claims

- Haskell is strongest for typed CPS and abstraction-heavy control encodings.
- Monadic and prompt-typed explanations belong together here.
- Avoid implying that the cited papers standardize one production Haskell runtime surface.
EOF
    emit_footer
    ;;
  language:scala)
    emit_header
    cat <<'EOF'
- `[SCALA-CONT]`: archived ecosystem status.
- `[SCALA-CONT-DOC]`: `shift`, `reset`, `@cps`, and `@cpsParam`.

## Safe Claims

- Scala continuations are historically important but not a current mainstream language feature.
- Answer-type modification is the real technical content to cite.
- Do not describe the plugin as current production support without checking live status.
EOF
    emit_footer
    ;;
  language:javascript)
    emit_header
    cat <<'EOF'
- `[JS-GEN]`: generators and `yield`.
- `[JS-ASYNC]`: `async` and `await`.

## Safe Claims

- JavaScript gives structured suspension, not standardized delimited continuation operators.
- Generators and promises are good teaching or compilation surfaces.
- If the prompt asks about semantic equivalence, return to the control literature instead of stretching the analogy.
EOF
    emit_footer
    ;;
  *)
    usage
    ;;
esac
