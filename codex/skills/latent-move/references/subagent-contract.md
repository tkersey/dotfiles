# Read-Only Subagent Contract

## Location and format

Reusable Codex custom subagents for this workflow are project-scoped TOML files under `.codex/agents/*.toml`. Do not place custom subagent definitions under `codex/skills/latent-move/agents/`; that skill-local directory is reserved for skill metadata such as `openai.yaml`.

Each custom agent file must define `name`, `description`, and `developer_instructions`, and should set `sandbox_mode = "read-only"` for Latent Move's evidence-gathering agents.

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

Rules:

- No user-facing preamble.
- No instruction acknowledgements.
- No transport wrappers.
- No outer JSON envelope.
- No markdown essay before or after the packet.
- `routing_call:` is required and must be one line.
- `ledger_updates:` may use concise ledger-shaped lines.
- Malformed packets are not evidence.

## Transport degradation

Treat specialist transport as unreliable unless the packet contract is satisfied.

If specialist output contains transport wrappers, instruction acknowledgements, outer JSON envelopes, or multiple packet bodies:

- mark it `transport-invalid`
- normalize it into the Specialist Briefing Ledger
- do not relay raw malformed output to the user
- continue locally
- retry at most one narrowly scoped specialist only if the missing signal is material

After one malformed specialist result for the current artifact state, do not rerun the broad swarm for that same artifact state.

## Read-only permissions

Subagents must not edit files, apply patches, create commits, run formatters, run migrations, install dependencies, start services, mutate project state, perform write-heavy implementation, or claim final decisions.

Subagents may read files, inspect docs, search the repository, summarize evidence, identify relevant tests or commands, propose proof checks, and update ledgers in packet form.

If a useful check might mutate state, the subagent should describe the check instead of running it.

## Subagent selection

Use `state_cartographer` when project state is broad or unclear.

Use `latent_frame_scout` when the request may be underframed.

Use `constraint_miner` when product, compatibility, API, operational, or time constraints could change the ranking.

Use `proof_surface_mapper` when proof quality is a decision factor.

Use `candidate_red_team` when a nominee looks flashy, broad, high-risk, or close to the runner-up.

Use `brief_auditor` when the final brief will be handed to an executor or human.

Use the smallest swarm that can reduce real uncertainty.
