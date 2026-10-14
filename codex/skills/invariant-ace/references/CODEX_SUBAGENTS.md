# Specialist Workers for Invariant Ace

Resolve the named specialist roles from the current runtime's available agents.
Use its supported invocation syntax and pass the exact subject, relevant evidence,
and assigned authority question. Do not depend on a fixed install path. Dispatch
only dimensions selected by the entry's evidence-dependent escalation conditions
or explicitly required by the caller. Direct root evidence does not substitute
for independently required clearance when a worker is unavailable.

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
Run the selected $invariant-ace independent lanes using available specialist workers. Reuse qualifying independent packets before dispatch. Supply the material unestablished premise or unresolved evidence that requires each remaining lane, artifact_state_id, direction_state_id, candidate invariant IDs, relevant files, and exact scope. Require packet-native output with evidence refs. If an independently required worker is unavailable, keep its affected result unresolved; do not claim root-equivalent evidence is independent. Root assesses the other substantive questions directly and synthesizes the clearances and vetoes. Unresolved vetoes block enforce-now.
```

Workers are read-only. Root may downgrade freely but may not upgrade against unresolved veto.
