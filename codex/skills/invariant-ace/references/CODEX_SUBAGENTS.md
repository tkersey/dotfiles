# Specialist Workers for Invariant Ace

Use the version-neutral worker model in `../../references/codex-specialist-worker-model.md`. Do not depend on one runtime's subagent invocation syntax or install path.

## Repository workers

| Role | Worker |
|---|---|
| concrete bad trace / reachability / falsifier | `inv-counterexample-authority` |
| state owner / scope / source of truth | `inv-owner-scope-authority` |
| transition set and preservation / induction closure | `inv-induction-authority` |
| enforcement boundary and why local/stronger/weaker cuts are wrong | `inv-boundary-authority` |
| generator / validator / projection / certificate / fixture / witness parity | `inv-witness-parity-authority` |
| proof signal tied to each predicate | `inv-verification-authority` |
| strongest no-invariant / no-enforce countercase | `inv-skeptic-authority` |

## Prompt shape

```text
Run $invariant-ace authority fanout using specialist workers when supported. Assign artifact_state_id, direction_state_id, candidate invariant IDs, relevant files, and exact scope. Require packet-native output with evidence refs. If a required worker is unavailable, emit same-schema root-equivalent packets or route to blocked. Root must synthesize an Authority Clearance Matrix and veto ledger; unresolved vetoes block enforce-now.
```

Workers are read-only. Root may downgrade freely but may not upgrade against unresolved veto.
