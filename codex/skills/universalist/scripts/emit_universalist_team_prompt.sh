#!/usr/bin/env bash
set -euo pipefail
mode="${1:-design}"
case "$mode" in
  design)
    roster="universalist-world-cartographer, universalist-substrate-architect, universalist-categorical-architect, universalist-semanticist, universalist-resource-realist"
    ;;
  refactor)
    roster="universalist-world-cartographer, universalist-categorical-architect, universalist-semanticist"
    ;;
  audit)
    roster="universalist-world-cartographer, universalist-substrate-architect, universalist-resource-realist"
    ;;
  spatial)
    roster="universalist-world-cartographer, universalist-categorical-architect, universalist-semanticist, universalist-resource-realist"
    ;;
  convolution)
    roster="universalist-world-cartographer, universalist-categorical-architect, universalist-semanticist, universalist-resource-realist"
    ;;
  tambara|contextual-morphism|optic)
    roster="universalist-world-cartographer, universalist-categorical-architect, universalist-semanticist, universalist-resource-realist"
    ;;
  *) echo "unknown mode: $mode" >&2; exit 2 ;;
esac
cat <<OUT
Use \$universalist in explicit categorical-substrate team mode.

Spawn these custom read-only agents in parallel:
${roster}

Give each a bounded, non-overlapping question and require the Universalist specialist packet contract. Wait for every packet.

When locality is semantic, require points, patches, local/global identity, effective halos and labels, basis or explicit non-basis status, restriction, continuity, and resource laws; reject a plain dependency graph or context wrapper mislabeled as a comonadic space.

When description composition is semantic, require the index category/world, tensor/unit or promonoidal kernel, indexed description family, pointwise-vs-Day-vs-promonoidal-vs-substitution-vs-monadic selector, legal decomposition and quotient policy, representable/interpreter laws, effect-order guardrail, collision policy, and effective enumeration/normalization bound. Reject a nested loop, ordinary product, schema merge, numerical convolution, or static plan combinator mislabeled as Day convolution.

When contextual morphisms are semantic, require the ambient context category/world, tensor/unit or partial/dependent action, source and target endpoint actions, underlying profunctor/generalized capability, ordinary-vs-mixed-vs-dependent Tambara selector, frame operation, unit/associativity/naturality/context-coherence laws, residual/optic representation when used, free/cofree context basis when used, representability status, concrete realizer or obstruction, effect-order owner, and effective residual/framing resource bound. Reject a Reader parameter, Context wrapper, middleware stack, dependency-injection container, optic-shaped record, or equivariant Tambara functor mislabeled as a Pastro-Street/profunctor Tambara module.

Then synthesize one Effective Universal Architecture Certificate, send it to universalist-proof-auditor, revise or mark it obstructed, and select one witness seam. If implementation is requested, use only universalist-witness-implementer for that seam, then universalist-verifier. The root owns synthesis, write ordering, closure, and the final answer. Do not let child agents spawn more agents.
OUT
