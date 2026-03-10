#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
Usage: emit_witness_pack.sh <topic> [language]

Topics:
  static-vs-dynamic
  multi-prompt
  answer-type
  one-shot
  machine-derivation
  analogy-boundary

Languages:
  agnostic (default)
  racket
  ocaml
  haskell
  scala
  javascript
EOF
  exit 1
}

topic="${1:-}"
language="${2:-agnostic}"

[[ -n "$topic" ]] || usage

case "$topic" in
  static-vs-dynamic|multi-prompt|answer-type|one-shot|machine-derivation|analogy-boundary) ;;
  *) usage ;;
esac

case "$language" in
  agnostic|racket|ocaml|haskell|scala|javascript) ;;
  *) usage ;;
esac

language_notes() {
  case "$language" in
    agnostic)
      cat <<'EOF'
- Language target: agnostic
- Keep the witness in language-neutral syntax unless the host language matters to the distinction.
EOF
      ;;
    racket)
      cat <<'EOF'
- Language target: Racket
- Prefer prompt-tag or reduction-ready examples that can be run against a living operator surface.
EOF
      ;;
    ocaml)
      cat <<'EOF'
- Language target: OCaml
- Name whether the witness uses `delimcc` or effect handlers, and make one-shot boundaries explicit.
EOF
      ;;
    haskell)
      cat <<'EOF'
- Language target: Haskell
- Make answer-type pressure or prompt typing explicit when the witness depends on it.
EOF
      ;;
    scala)
      cat <<'EOF'
- Language target: Scala
- Name the plugin or typed API surface and show where answer-type modification becomes visible.
EOF
      ;;
    javascript)
      cat <<'EOF'
- Language target: JavaScript
- Be explicit about whether the witness is only an analogy or a compilation target, not a semantic equivalent.
EOF
      ;;
  esac
}

header() {
  cat <<EOF
# Witness Pack

- Topic: $topic
$(language_notes)

## Goal
EOF
}

case "$topic" in
  static-vs-dynamic)
    header
    cat <<'EOF'
- Force the difference between `shift/reset` and `control/prompt` to become observable.

## Minimal Witness Shape

- choose a nested-resume or BFS-style example
- mark the delimiter that should or should not be reinstated
- resume the captured continuation in a context where dynamic extent changes the outcome

## What To Observe

- whether resumed work stays delimited
- whether traversal order, nesting, or continuation composition changes
- which explanation fails if you pretend the two operator families are interchangeable

## Source Anchors

- `[DC-AC-1990]`
- `[DC-DYN-2005]`
- `[DC-STC-2004]`

## Failure Modes

- describing the difference as only "more dynamic" without naming the delimiter story
- giving a rule without a witness or a witness without the rule
EOF
    ;;
  multi-prompt)
    header
    cat <<'EOF'
- Force prompt identity to matter.

## Minimal Witness Shape

- introduce two prompt identities or tags
- capture under one boundary and explain why the other must remain intact
- show the smallest operation that would go wrong if prompts were collapsed into one undifferentiated delimiter

## What To Observe

- which prompt owns the captured continuation slice
- why typed or modular APIs care about prompt identity
- what breaks if prompt tags are ignored

## Source Anchors

- `[DC-MFDC-2007]`
- `[RKT-REF]`
- `[OCAML-DELIMCC-2012]`

## Failure Modes

- talking about multi-prompt libraries as if they only rename `reset`
- omitting prompt identity from the example
EOF
    ;;
  answer-type)
    header
    cat <<'EOF'
- Make answer-type modification visible instead of treating typing as a side note.

## Minimal Witness Shape

- choose a computation whose captured continuation changes the surrounding answer type
- point to the exact operator or annotation where that pressure appears
- explain whether the host language exposes the change directly

## What To Observe

- where the source answer type and continuation answer type diverge
- whether the API, type system, or translation accounts for that divergence
- what misconception appears if answer types are flattened away

## Source Anchors

- `[DC-MFDC-2007]`
- `[TYPE4D-2022]`
- `[SCALA-CONT-DOC]`

## Failure Modes

- describing typed delimited control without naming answer-type modification
- using an example whose answer type never changes
EOF
    ;;
  one-shot)
    header
    cat <<'EOF'
- Force the runtime contract around reuse of continuations to become visible.

## Minimal Witness Shape

- resume the same captured continuation twice, or explain why the workload would require that ability
- state whether the runtime forbids, traps, clones, or reuses the continuation
- tie the witness to one workload such as search, generators, or repeated suspension

## What To Observe

- whether the continuation is linear or reusable
- what the runtime wins by enforcing one-shot use
- what semantic behaviors become awkward or impossible without cloning

## Source Anchors

- `[RT-ONE-SHOT-1996]`
- `[OCAML-MANUAL]`
- `[OCAML-RETROEFF-2021]`

## Failure Modes

- treating one-shot as only a performance optimization
- forgetting to say whether the surface is handlers, delimited control, or a specific runtime contract
EOF
    ;;
  machine-derivation)
    header
    cat <<'EOF'
- Show how one evaluator trace becomes one machine trace.

## Minimal Witness Shape

- pick one small source term with a nontrivial continuation shape
- show the evaluator continuation before defunctionalization
- show the machine frame or constructor after defunctionalization
- say whether closure conversion matters to the step you are showing

## What To Observe

- which higher-order continuation becomes which first-order artifact
- where the derivation preserves behavior rather than inventing a machine
- how refunctionalization would recover the higher-order view

## Source Anchors

- `[DEF-DN-2001]`
- `[DEF-AGER-2003]`
- `[DEF-REFUNC-2007]`

## Failure Modes

- skipping straight from evaluator to machine without naming the derivation chain
- describing defunctionalization only as closure replacement
EOF
    ;;
  analogy-boundary)
    header
    cat <<'EOF'
- Keep analogies honest when the prompt reaches for generators, `async` or `await`, or effect handlers.

## Minimal Witness Shape

- pick a control scenario that needs arbitrary delimited-context capture, multi-shot reuse, or prompt identity
- compare it with the adjacent surface that offers only suspension, promises, or one-shot handlers
- state whether the relationship is semantic, compilational, or pedagogical

## What To Observe

- what the adjacent abstraction does provide
- what it does not provide directly
- which false equivalence the witness prevents

## Source Anchors

- `[JS-GEN]`
- `[JS-ASYNC]`
- `[OCAML-MANUAL]`
- one relevant core control source from `references/sources.md`

## Failure Modes

- calling the adjacent abstraction "the same thing" without boundaries
- using implementation similarity as proof of semantic equivalence
EOF
    ;;
esac
