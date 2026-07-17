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
  *) echo "unknown mode: $mode" >&2; exit 2 ;;
esac
cat <<OUT
Use \$universalist in explicit categorical-substrate team mode.

Spawn these custom read-only agents in parallel:
${roster}

Give each a bounded, non-overlapping question and require the Universalist specialist packet contract. Wait for every packet. When locality is semantic, require points, patches, local/global identity, effective halos and labels, basis or explicit non-basis status, restriction, continuity, and resource laws; reject a plain dependency graph or context wrapper mislabeled as a comonadic space. Then synthesize one Effective Universal Architecture Certificate, send it to universalist-proof-auditor, revise or mark it obstructed, and select one witness seam. If implementation is requested, use only universalist-witness-implementer for that seam, then universalist-verifier. The root owns synthesis, write ordering, closure, and the final answer. Do not let child agents spawn more agents.
OUT