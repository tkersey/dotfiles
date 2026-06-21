#!/usr/bin/env bash
set -euo pipefail
kind="${1:-canonical-boundary-artifact}"
language="${2:-agnostic}"
case "$kind" in
  free-syntax|initial-algebra)
    cat <<OUT
# Canonical artifact plan: free syntax (${language})

## Signal
Syntax, execution, logging, explanation, or validation are tangled.

## Artifact
- data Syntax / Program / Command
- interpreter(s)
- smart constructors if needed

## First seam
- one command / AST node / workflow step:

## Proof signal
old evaluator and new interpreter match on fixtures.

## Negative witness
invalid syntax or missing interpreter case fails.
OUT
    ;;
  coherent-observation|observations|yoneda)
    cat <<OUT
# Canonical artifact plan: coherent observations (${language})

## Signal
Duplicated projections, selectors, old client views, reports, or policy checks.

## Artifact
- data Observation
- runObservation
- validateCoherence

## First seam
- one observation / report / projection:

## Proof signal
overlapping observations commute; representation change preserves observations.
OUT
    ;;
  transported-semantics|transport|lan)
    cat <<OUT
# Canonical artifact plan: transported semantics (${language})

## Signal
Old/source semantics must move to a new target surface.

## Artifact
- data TransportPath
- transport / lower / interpretPath

## First seam
- one source behavior and one target path:

## Proof signal
identity or embedding path preserves behavior.
OUT
    ;;
  lifted-implementation|lift|kan-lift)
    cat <<OUT
# Canonical artifact plan: lifted implementation (${language})

## Signal
Public behavior is known before internals.

## Artifact
- data PublicCase
- data Realizer
- realize : PublicCase -> Realizer
- project : Realizer -> PublicBehavior

## Projection P : B -> C
- concrete code path:

## First seam
- one public case:

## Proof signal
project(realize(case)) == required(case)
OUT
    ;;
  free-builder|free-builder-behind-projection|freyd-aft|aft)
    cat <<OUT
# Canonical artifact plan: free builder behind projection (${language})

## Signal
Public behavior should have a canonical implementation-side builder through P : B -> C.

## Artifact
- data RequiredBehavior
- data ImplementationTemplate
- free : RequiredBehavior -> ImplementationTemplate
- project : ImplementationTemplate -> PublicBehavior

## Freyd/AFT diagnostic
- P in code:
- B constraint-combining structure:
- P preserves constraints? yes/no/evidence:
- bounded templates:

## Proof signal
project(free(required(case))) satisfies required(case)
OUT
    ;;
  obstruction|obstruction-report)
    cat <<OUT
# Canonical artifact plan: obstruction report (${language})

## Signal
A free/lifted implementation is desired but P loses evidence or B lacks structure.

## Artifact
- data Obstruction = MissingEvidence | MissingCapability | InconsistentRequirement | UnboundedTemplates
- explainObstruction : RequiredBehavior -> Obstruction

## First seam
- one public case that cannot be realized:

## Proof signal
obstruction names the missing evidence/template/constraint and reproduces the failure.
OUT
    ;;
  residual-obligations|obligation|rift)
    cat <<OUT
# Canonical artifact plan: residual obligations (${language})

## Signal
Public behavior implies internal checks, fields, events, resources, or capabilities.

## Artifact
- data Requirement
- data Obligation
- deriveObligations
- satisfy

## First seam
- one public requirement:

## Proof signal
missing obligation fails; satisfying obligations passes projection.
OUT
    ;;
  behavioral-coalgebra|coalgebra|protocol|state-machine)
    cat <<OUT
# Canonical artifact plan: behavioral coalgebra (${language})

## Signal
Stateful or ongoing behavior is duplicated, informal, or observed over time.

## Artifact
- data State
- data Input
- data Observation
- step : State × Input -> State
- observe : State -> ObservationResult

## First seam
- one transition:
- one observation:

## Proof signal
trace(step, observe, initial, inputs) == expectedTrace
invalid transition is rejected
states claimed equivalent produce equivalent observations
OUT
    ;;
  effect-handler|effects|algebraic-effects)
    cat <<OUT
# Canonical artifact plan: effect signature and handlers (${language})

## Signal
Operations need multiple handlers: test, production, audit, explanation, simulation, retry, or scheduling.

## Artifact
- data Operation
- data Program = Pure | Perform(Operation, continuation)
- handleTest
- handleProd
- handleAudit or handleExplain

## First seam
- one operation:
- one test handler:
- one production projection:

## Proof signal
test handler and production projection agree on declared observations
every operation has a handler case
OUT
    ;;
  freyd-category|premonoidal|effect-order)
    cat <<OUT
# Canonical artifact plan: Freyd effect boundary (${language})

## Signal
Pure values and effectful computations share types, but order/parallelism/centrality is implicit.

## Artifact
- Pure category C
- Effectful premonoidal category K
- pure embedding J : C -> K
- central operation registry / proof surface

## First seam
- one pure transformation:
- one order-sensitive effect pair:

## Proof signal
J preserves identity/composition; claimed reorderings agree observationally; noncommuting witness stays ordered.
OUT
    ;;
  operad|operadic|component-wiring)
    cat <<OUT
# Canonical artifact plan: colored operad / composition grammar (${language})

## Signal
Typed components assemble hierarchically, but legal wiring is hidden in an accidental call graph.

## Artifact
- colors / port types
- primitive operations
- substitution rules
- semantic algebras

## First seam
- one composite subsystem:
- one forbidden wiring:

## Proof signal
interpret(substitute(f,g1,...,gn)) == compose(interpret(f),interpret(g1),...,interpret(gn))
OUT
    ;;
  explicit-ir|defunctionalization|ir)
    cat <<OUT
# Canonical artifact plan: explicit IR (${language})

## Signal
Callbacks, closures, handlers, continuations, predicates, or mappers cross an architecture boundary.

## Artifact
- data BoundaryCase
- applyBoundaryCase / interpret / project

## First seam
- one callback/handler/predicate:

## Proof signal
apply(encodedCase, x) == oldCallback(x)
OUT
    ;;
  dense-probe|semantic-compression|codensity-presentation)
    cat <<OUT
# Dense Probe Presentation Plan (${language})

## Boundary

Worlds:
Boundary:
Target semantic artifact:

## Why not algebraic/free syntax

Generators/equations attempted:
Why insufficient or too large:

## Probe world

Probes:
Probe morphisms/refinements:
Coverage/density claim:
Dualizing observation object:
Reconstruction operation:
Domain-specific theorem/assumption:

## Implementation

Probe IR:
runProbe:
reconstruct:
validateProbeCoherence:

## Laws

Probe coherence:
Reconstruction law:
Missing-probe falsifier:
OUT
    ;;
  *)
    cat <<OUT
# Canonical artifact plan: ${kind} (${language})

## Signal

## Artifact

## Boundary

## First seam

## Proof signal

## Falsifier
OUT
    ;;
esac
