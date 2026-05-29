# Codex subagents for invariant-ace

## Install locations

Codex discovers custom agents from:

- project agents: `codex/agents/*.toml` in this dotfiles layout, symlinked to `$HOME/.codex/agents`
- user agents: `$HOME/.codex/agents/*.toml`

This package includes:

- `codex/agents/inv-counterexample-authority.toml`
- `codex/agents/inv-owner-scope-authority.toml`
- `codex/agents/inv-induction-authority.toml`
- `codex/agents/inv-boundary-authority.toml`
- `codex/agents/inv-witness-parity-authority.toml`
- `codex/agents/inv-verification-authority.toml`
- `codex/agents/inv-skeptic-authority.toml`

## Spawn guidance

Use all seven agents when an invariant can become implementation work, proof closure, or review-adjudication authority. For exploratory sketches, root-equivalent packets are acceptable only when implementation handoff remains `no`.

Prompt shape:

```text
Run $invariant-ace authority fanout. Spawn inv-counterexample-authority, inv-owner-scope-authority, inv-induction-authority, inv-boundary-authority, inv-witness-parity-authority, inv-verification-authority, and inv-skeptic-authority. Assign artifact_state_id, candidate invariant IDs, relevant files, direction state, and exact scope. Require packet-native output with evidence refs. Root must synthesize an Authority Clearance Matrix and veto ledger; unresolved vetoes block enforce-now.
```

## Parent synthesis rules

1. Launch independent lanes before waiting.
2. Keep workers read-only.
3. Reject wrong-state/wrong-scope/generic packets.
4. Preserve vetoes in `Authority Veto Ledger`.
5. Root may downgrade freely but may not upgrade against unresolved veto.
6. Final output must pass `tools/invariant_ace_gate.py` before implementation handoff.
