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

Common focus values:
  broad
  static-vs-dynamic
  multi-prompt
  answer-type
  one-shot
  machine-derivation
  analogy-boundary
  racket
  ocaml
  haskell
  scala
  javascript
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

header() {
  printf '# Source Pack: %s / %s\n\n' "$track" "$focus"
  cat <<'EOF'
Use this as a starter source bundle. Check `references/sources.md` for titles and URLs, and browse primary docs for drift-prone ecosystem or implementation-status claims.
EOF
}

source_note() {
  local id="$1"
  local why="$2"
  cat <<EOF
- [$id] $why
EOF
}

header

case "$track:$focus" in
  semantics:static-vs-dynamic)
    source_note DC-AC-1990 "canonical shift/reset rules and CPS framing"
    source_note DC-DYN-2005 "static-versus-dynamic extent and BFS-style witness"
    source_note DC-STC-2004 "expressiveness and CPS relations between static and dynamic control"
    ;;
  semantics:multi-prompt)
    source_note DC-MFDC-2007 "typed prompt and subcontinuation APIs"
    source_note RKT-REF "Racket prompt tags and composable continuation surfaces"
    source_note OCAML-DELIMCC-2012 "direct typed multi-prompt control in OCaml"
    ;;
  semantics:answer-type)
    source_note DC-MFDC-2007 "typed prompts and CPS sufficiency"
    source_note TYPE4D-2022 "typed comparison of four delimited-control operators"
    source_note SCALA-CONT-DOC "historical answer-type-modifying Scala API surface"
    ;;
  semantics:broad)
    source_note DC-FP-1988 "prompts as delimiters"
    source_note DC-AC-1990 "canonical static delimited control"
    source_note DC-DYN-2005 "dynamic extent and separating witnesses"
    source_note DC-MFDC-2007 "typed multi-prompt and subcontinuation framework"
    ;;
  translation:machine-derivation)
    source_note DEF-DN-2001 "whole-program defunctionalization"
    source_note DEF-AGER-2003 "evaluator-to-machine derivation chain"
    source_note DEF-REFUNC-2007 "refunctionalization when recovering higher-order structure"
    ;;
  translation:answer-type)
    source_note DC-MFDC-2007 "typed prompt and CPS framework"
    source_note TYPE4D-2022 "operator family type systems"
    source_note DEF-DT-2023 "type-preserving defunctionalization with dependent types"
    ;;
  translation:broad)
    source_note DC-MONAD-1994 "reflection and reification"
    source_note DC-MFDC-2007 "standard CPS sufficiency for delimited control"
    source_note DEF-DN-2001 "defunctionalization transformation"
    source_note DEF-AGER-2003 "machine correspondence"
    ;;
  implementation:one-shot)
    source_note RT-ONE-SHOT-1996 "one-shot implementation opportunity"
    source_note OCAML-MANUAL "one-shot operational boundaries in OCaml effects"
    source_note OCAML-RETROEFF-2021 "runtime evidence for effect handlers"
    ;;
  implementation:broad)
    source_note DC-DIRECT-2002 "direct implementation of shift/reset"
    source_note DC-DIRECT-2009 "compiler-level direct implementation"
    source_note RT-FOLKLORE-2020 "benchmark methodology"
    source_note OCAML-RETROEFF-2021 "modern runtime evidence anchor"
    ;;
  roadmap:broad)
    source_note DC-AC-1990 "semantic core"
    source_note DC-DYN-2005 "separating witness discipline"
    source_note DEF-DN-2001 "defunctionalization core"
    source_note DEF-AGER-2003 "evaluator-to-machine project path"
    source_note RT-FOLKLORE-2020 "benchmarking discipline"
    source_note TYPE4D-2022 "typed and mechanized direction"
    ;;
  language:racket)
    source_note RKT-GUIDE "prompt and abort mental model"
    source_note RKT-REF "operator names, prompt tags, and control surfaces"
    source_note DC-FP-1988 "prompt theory anchor"
    ;;
  language:ocaml)
    source_note OCAML-DELIMCC-2010 "published delimcc system description"
    source_note OCAML-DELIMCC-2012 "direct typed multi-prompt control"
    source_note OCAML-MANUAL "effect handler boundaries"
    source_note OCAML-RETROEFF-2021 "runtime design and evidence"
    ;;
  language:haskell)
    source_note DC-MFDC-2007 "monadic framework and typed prompt APIs"
    source_note DC-MONAD-1994 "representing monads with delimited control"
    ;;
  language:scala)
    source_note SCALA-CONT "historical plugin status"
    source_note SCALA-CONT-DOC "reset/shift and @cps API surface"
    source_note TYPE4D-2022 "typed control comparison if theory matters"
    ;;
  language:javascript)
    source_note JS-GEN "generator suspension analogy"
    source_note JS-ASYNC "async/await promise scheduling surface"
    source_note DC-AC-1990 "core delimited-control anchor to prevent overclaiming"
    ;;
  language:broad)
    source_note RKT-REF "Racket control operators"
    source_note OCAML-MANUAL "OCaml effect handlers"
    source_note OCAML-DELIMCC-2012 "OCaml multi-prompt delimited control"
    source_note SCALA-CONT-DOC "Scala answer-type-modifying continuations"
    source_note JS-GEN "JavaScript generator analogy boundary"
    ;;
  *)
    cat >&2 <<EOF
Unsupported focus '$focus' for track '$track'. Try 'broad' or consult SKILL.md.
EOF
    exit 1
    ;;
esac

cat <<'EOF'

## Safe-use reminder

- Separate semantic, implementation, ecosystem, and analogy claims.
- Browse primary docs before answering questions about current status, library maintenance, or proposal availability.
- Use `references/claim-map.md` to map claims to source IDs before final prose.
EOF
