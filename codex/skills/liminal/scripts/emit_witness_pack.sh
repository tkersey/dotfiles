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

cat <<EOF
# Witness Pack: $topic / $language

$(language_notes)
EOF

case "$topic" in
  static-vs-dynamic)
    cat <<'EOF'
## Distinction

`shift/reset` reinstalls the captured continuation under a delimiter; `control/prompt` resumes without the same automatic re-delimitation.

## Minimal Rule Contrast

```text
(reset E[shift k . e])
  -> reset((lambda k. e) (lambda x. reset E[x]))

(prompt E[control k . e])
  -> prompt((lambda k. e) (lambda x. E[x]))
```

## Observable Witness Shape

Use a nested-resume or BFS-style traversal where the extra `reset` changes whether later captures see the same boundary.

## Source Anchors

- [DC-AC-1990]
- [DC-DYN-2005]
- [DC-STC-2004]
EOF
    ;;
  multi-prompt)
    cat <<'EOF'
## Distinction

A single undifferentiated delimiter cannot model modular prompt identity. A capture under prompt tag `p` must not accidentally cross an unrelated prompt tag `q`.

## Minimal Witness Shape

```text
pushPrompt p (
  A;
  pushPrompt q (
    B;
    capture q k . ...
  );
  C
)
```

The captured continuation for `q` includes the `q`-local context but must not capture through the `p` boundary unless the operator explicitly targets it.

## Source Anchors

- [DC-MFDC-2007]
- [RKT-REF]
- [OCAML-DELIMCC-2012]
EOF
    ;;
  answer-type)
    cat <<'EOF'
## Distinction

Delimited control can expose answer-type pressure: the captured continuation may be used in a context with a different answer type from the surrounding computation.

## Minimal Witness Shape

```text
reset { 1 + shift k . "answer changed" }
```

The sketch is not a full typing derivation. Its purpose is to force the answer type of the captured continuation and the answer type of the whole delimited expression to be named.

## Source Anchors

- [DC-MFDC-2007]
- [TYPE4D-2022]
- [SCALA-CONT-DOC]
EOF
    ;;
  one-shot)
    cat <<'EOF'
## Distinction

A multi-shot continuation can be invoked repeatedly; a one-shot continuation can be resumed at most once unless the implementation clones or rejects the second use.

## Minimal Witness Shape

```text
capture k;
resume k 1;
resume k 2;  -- allowed, rejected, or cloned?
```

The answer must state whether the surface language forbids the second resume statically, traps dynamically, or copies continuation state.

## Source Anchors

- [RT-ONE-SHOT-1996]
- [OCAML-MANUAL]
- [OCAML-RETROEFF-2021]
EOF
    ;;
  machine-derivation)
    cat <<'EOF'
## Distinction

Defunctionalization does not merely "remove lambdas"; it makes the evaluator's latent continuation shapes explicit as first-order machine frames.

## Minimal Witness Shape

```text
Source: ((lambda x. x + 1) 41)
Continuation before defunctionalization: lambda v. v
Machine frame after defunctionalization: Halt
Application frame: Arg(term, env, kont) or Fun(value, kont)
```

Track one evaluator step and the corresponding machine transition.

## Source Anchors

- [DEF-DN-2001]
- [DEF-AGER-2003]
- [DEF-REFUNC-2007]
EOF
    ;;
  analogy-boundary)
    cat <<'EOF'
## Distinction

Generators, `async`/`await`, and effect handlers can be useful analogies or compilation targets, but they are not automatically semantic equivalents to delimited continuations.

## Minimal Witness Shape

Use a scenario that requires capturing an arbitrary delimited evaluation context rather than yielding only from the current generator frame or awaiting a promise.

## Source Anchors

- [JS-GEN]
- [JS-ASYNC]
- [OCAML-MANUAL]
- plus the relevant core control source, usually [DC-AC-1990] or [DC-DYN-2005]
EOF
    ;;
esac

cat <<'EOF'

## Failure Modes To Avoid

- Replacing the witness with taxonomy.
- Citing an analogy source for a semantic equivalence claim.
- Dropping the delimiter or resumption contract.
EOF
