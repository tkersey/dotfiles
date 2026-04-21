#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
Usage: emit_artifact_stub.sh <kind> [language]

Kinds:
  derivation-memo
  evaluator-project
  cps-translation
  defunc-machine
  benchmark-plan
  mechanization-plan
  citation-memo
  witness-walkthrough

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

kind="${1:-}"
language="${2:-agnostic}"
[[ -n "$kind" ]] || usage

case "$language" in
  agnostic|racket|ocaml|haskell|scala|javascript) ;;
  *) usage ;;
esac

language_notes() {
  case "$language" in
    agnostic)
      cat <<'EOF'
- Language target: agnostic
- Keep notation neutral until the concrete implementation language is known.
EOF
      ;;
    racket)
      cat <<'EOF'
- Language target: Racket
- Prefer evaluation contexts, prompt-oriented examples, and runnable reduction witnesses.
- Check `racket/control` names against `[RKT-REF]` before making API claims.
EOF
      ;;
    ocaml)
      cat <<'EOF'
- Language target: OCaml
- Name typing constraints, runtime representation choices, and effect-handler adjacency where relevant.
- Distinguish OCaml 5 one-shot effects from general multi-shot delimited continuations.
EOF
      ;;
    haskell)
      cat <<'EOF'
- Language target: Haskell
- Make CPS types explicit and call out monadic or multi-prompt encoding choices.
EOF
      ;;
    scala)
      cat <<'EOF'
- Language target: Scala
- Name answer-type modification, compiler-plugin boundaries, and whether the surface is historical or current.
EOF
      ;;
    javascript)
      cat <<'EOF'
- Language target: JavaScript
- Distinguish true delimited continuations from generator or async compilation targets.
EOF
      ;;
  esac
}

case "$kind" in
  derivation-memo)
    cat <<EOF
# Derivation Memo

## Problem Frame

- State the exact operator family, transformation, or runtime question.
$(language_notes)

## Concrete Witness

- Choose the smallest term, program, or trace that forces the distinction.
- State the delimiter or prompt boundary.
- State what the user should observe if the explanation is right.

## Semantic Core

- Name the continuation slice that is captured or resumed.
- State the relevant reduction or evaluation-context rule.
- Identify the nontrivial distinction that must survive the explanation.

## Claim Ledger

- Claim:
  - category: semantic | translation | implementation | ecosystem
  - source ids:
  - safe wording:
  - boundary or counterexample:

## Translation or Representation Sketch

- Decide whether the right lens is CPS, defunctionalization, a prompt-tag model, or a machine derivation.
- Show the smallest trustworthy sketch.

## Implementation Tradeoffs

- Name the primary runtime choice.
- State what it optimizes and what it costs.

## Proof or Benchmark Next Steps

- Give one proof obligation and one measurement obligation.

## Sources

- List primary paper, manual, or artifact IDs.
EOF
    ;;
  evaluator-project)
    cat <<EOF
# Evaluator Project Scaffold

## Goal

- Build a small evaluator that makes delimited control explicit.
$(language_notes)

## Minimum Surface

- values
- lambda application
- evaluation contexts or an equivalent machine view
- one delimited-control family
- one witness program that fails if the semantics are wrong

## Milestones

1. Implement the core language.
2. Add the delimiter and capture operators.
3. Add trace output for one witness example.
4. Add a comparison example against a nearby operator family.
5. Add a source ledger for each semantic rule.

## Source Anchors

- semantic rule source ids:
- implementation or runtime source ids:
- witness-program source ids:

## Checks

- one normal-form example
- one control-capture example
- one operator-separation witness
EOF
    ;;
  cps-translation)
    cat <<EOF
# CPS Translation Scaffold

## Source Fragment

- Define the source syntax under translation.
$(language_notes)

## Target Fragment

- Define value continuations.
- Define any needed meta-continuation layer.
- State answer-type changes if typing matters.

## Translation Cases

- variable
- lambda
- application
- delimiter
- control operator

## Invariants

- preserve evaluation order
- preserve delimiter boundaries
- preserve or expose answer-type changes

## Validation

- one hand-worked example
- one simulation claim to prove or test

## Source Anchors

- translation source ids:
- typing source ids:
- operator-separation source ids:
EOF
    ;;
  defunc-machine)
    cat <<EOF
# Defunctionalized Machine Scaffold

## Starting Point

- Name the evaluator or CPS-transformed program you are first-orderizing.
- State whether closure conversion is part of the derivation chain.
$(language_notes)

## Continuation Constructors

- list each continuation shape
- record captured free variables for each constructor

## Apply or Step Function

- define the dispatcher
- show the transition for each constructor

## Machine State

- control term
- environment if needed
- continuation or stack
- delimiter or prompt state if needed

## Checks

- one evaluator-to-machine trace comparison
- one example that crosses a delimiter boundary

## Source Anchors

- defunctionalization source ids:
- machine-correspondence source ids:
- refunctionalization source ids:
EOF
    ;;
  benchmark-plan)
    cat <<EOF
# Benchmark Plan

## Question

- State the runtime choice being compared.
$(language_notes)

## Semantic Contract

- one-shot or multi-shot:
- prompt tags or single delimiter:
- deep or shallow handlers if relevant:

## Workloads

- capture/resume loop
- generator-style workload
- nondeterminism or backtracking
- one semantic witness such as BFS versus DFS where applicable

## Metrics

- wall-clock time
- allocation or GC pressure
- capture cost by depth
- resume cost

## Method

- warmup policy
- repeated runs
- fixed input sizes
- explicit note about one-shot versus multi-shot assumptions

## Source Anchors

- runtime-strategy source ids:
- benchmark-methodology source ids:
- language-runtime docs if needed:

## Acceptance

- define the performance claim you are willing to make
- define the evidence needed to reject that claim
EOF
    ;;
  mechanization-plan)
    cat <<EOF
# Mechanization Plan

## Target Result

- State the theorem, translation, or safety result to mechanize.
$(language_notes)

## Formal Objects

- syntax
- typing judgment if any
- operational semantics
- target translation or machine

## Proof Skeleton

- substitution or weakening lemmas
- preservation or simulation lemma
- top-level theorem

## Source Anchors

- semantics source ids:
- translation or machine source ids:
- mechanization or artifact source ids:

## Artifact Plan

- toolchain version
- entrypoint file
- reproduction command

## Done Criteria

- clean build on a fresh environment
- one documented theorem or checked property
EOF
    ;;
  citation-memo)
    cat <<EOF
# Citation Memo

## Question

- State the exact question and the claim categories it touches.
$(language_notes)

## Claim Ledger

- Claim:
  - category: semantic | translation | implementation | ecosystem
  - source ids:
  - safe wording:
  - direct citation or inference:
  - what this source does not justify:

## Source Pack

- primary semantic source:
- primary translation or machine source:
- primary runtime or ecosystem source:
- live doc to browse if freshness matters:

## Output Shape

- one paragraph on agreement across sources
- one paragraph on the real difference
- one paragraph on open gaps or unresolved claims

## Sources

- list the exact papers, manuals, or docs to cite
EOF
    ;;
  witness-walkthrough)
    cat <<EOF
# Witness Walkthrough

## Distinction

- State the exact distinction to force.
$(language_notes)

## Minimal Witness

- give the smallest trustworthy term, program, or trace
- state the delimiter or prompt boundary
- name what continuation fragment is captured or resumed

## Observable Difference

- what happens in the first operator, runtime, or encoding?
- what happens in the second one?
- what user-visible consequence proves the distinction?

## Translation or Runtime Lens

- say whether CPS, subcontinuations, answer-type modification, or runtime linearity is the right explanatory tool

## Source Anchors

- primary semantic source ids:
- primary implementation or runtime source ids:
- one adjacent source that must not be overstretched:

## Failure Modes

- what shortcut explanation would get this witness wrong?
EOF
    ;;
  *) usage ;;
esac
