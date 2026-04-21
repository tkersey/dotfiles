# Read-only subagent contract

Subagents are optional evidence lenses. They never replace the companion-skill chain.

## Allowed project-scoped subagents

- `state_cartographer`
- `latent_evidence_scout`
- `constraint_miner`
- `proof_surface_mapper`
- `candidate_red_team`
- `brief_auditor`

## Packet contract

Ask each specialist to return exactly one packet:

```text
<LATENT_MOVE_PACKET role="..." artifact_state_label="..." status="ok|blocked|transport-invalid">
scope: ...
top_signals: ...
unresolved_signals: ...
ledger_updates: ...
agreement_pressure: ...
routing_call: ...
</LATENT_MOVE_PACKET>
```

No preamble, no instruction acknowledgement, no JSON envelope, no markdown essay.
Malformed packets are not evidence.

## Read-only rule

Subagents must not edit files, apply patches, create commits, run formatters, run migrations, install dependencies, start services, mutate project state, or claim final decisions.
