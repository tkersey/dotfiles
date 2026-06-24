# Universalist Subagent Orchestration

## Gate

Universalist custom agents are spawned only when the user explicitly requests subagents, parallel agents, team mode, or the categorical-substrate team.

## Root responsibilities

The root owns requirement interpretation, artifact state, roster selection, prompts, packet validation, synthesis, architecture choice, write ordering, conflict resolution, final certificate, root proof, and closure.

## Default topology

```text
explicit team request
-> select 1-2 route-changing read-only specialists by default
-> root synthesizes one candidate certificate and strongest countercase
-> proof auditor only when unresolved soundness remains
-> root selects one witness seam
-> one bounded writer implements it
-> one independent verifier checks it
-> root integrates, proves, and stops
```

Use 3-4 read-only specialists when several independent architecture dimensions remain material. Use 5-8 only for a high-risk whole-system certificate where those dimensions cannot be closed locally.

## Roster

- `universalist-world-cartographer` — worlds, boundaries, primitives, observations, and evidence.
- `universalist-substrate-architect` — effective presentation, recursion/partiality, and concrete primitives.
- `universalist-categorical-architect` — canonical construction and boundary artifact.
- `universalist-semanticist` — syntax/semantics, effects, state, observations, and equivalence.
- `universalist-resource-realist` — time, space, latency, concurrency, failure, security, and deployment.
- `universalist-proof-auditor` — effectivity, soundness, adequacy, laws, and falsifiers.
- `universalist-witness-implementer` — exactly one root-selected witness seam.
- `universalist-verifier` — independent final witness and certificate verification.

Select only roles whose unresolved dimension can change the certificate, witness seam, proof, or risk disposition.

## Invariants

- Specialists return `specialist-packet-v2`.
- Read-only roles never edit.
- Only one writer may own the selected seam.
- Children do not spawn children.
- Specialist packets are evidence, not truth.
- Any material edit makes pre-edit packets stale unless their claim is artifact-independent and the root explicitly revalidates it.
- The verifier does not repair the witness.

## Stop rule

Close specialists and continue locally when their uncertainty is resolved, the packet is stale or low-value, or waiting no longer produces progress. Do not wait indefinitely for a broad swarm.
