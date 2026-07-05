# Goal Scheme Modes

Use modes to customize behavior without multiplying skills.

## Persistence modes

| Mode | Use when | State owner |
|---|---|---|
| `update_plan` | The plan is user-visible and session-local. | Native Codex plan UI. |
| `goal-artifacts` | A material `/goal` needs attempts, evidence, and memo rows. | `.goal/*` files if publishable for the repo. |
| `blocked` | Durable graph coordination, fencing, claims, worktrees, or serialized integration are required but unsupported. | Explicit blocked receipt. |

## Implementation modes

| Mode | Behavior |
|---|---|
| `proof-only` | Run/inspect proof and respond; do not edit unless proof fails. |
| `minimal-fix` | Make the smallest owner-correct repair. |
| `refactor-kernel` | Replace repeated local patches with one owner/boundary/abstraction fix. |
| `branch-race` | Compare isolated strategies under the same verifier. |

## Review modes

| Mode | Behavior |
|---|---|
| `adjudicate-only` | Classify review findings; no mutation. |
| `proof-only` | Treat review as a request for evidence. |
| `minimal-fix` | Fix accepted liabilities locally. |
| `refactor-kernel` | Collapse same-family comments into one abstraction or boundary correction. |
| `blocked-external-coordination` | Stop when durable, fenced review remediation lacks a supported controller. |

## Default selection

1. Start in `update_plan + minimal-fix`.
2. Switch to `proof-only` when the claim is likely already satisfied.
3. Switch to `refactor-kernel` when findings or failures share an owner boundary.
4. Switch to `branch-race` when two plausible fixes cannot be ranked cheaply.
5. Switch to `blocked` for durable coordination, resource claims, or legacy controller continuity that cannot be represented locally.
