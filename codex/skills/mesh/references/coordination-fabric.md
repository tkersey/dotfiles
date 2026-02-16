# Coordination Fabric

This document defines a **coordination substrate** for scaling orchestration beyond a single in-process swarm.
It is intentionally tool-agnostic: you can implement it with an HTTP tool service, a local SQLite service, or
any other durable message/lease store.

## Why

Hub-and-spoke swarms (workers only talk to an orchestrator) break down at scale:

- **Slow convergence**: important contradictions are discovered late (synthesis), causing retries.
- **High correlation**: workers see the same prompt and make the same mistake.
- **No self-coordination**: parallel sessions/instances can't safely claim work or avoid conflicts.

The coordination fabric adds three primitives:

1) **Task list** (what to do)
2) **Mailbox** (who said what; durable threads)
3) **Leases** (who intends to touch which files)

The goal is not "agents chatting". The goal is *low-overhead, durable, typed coordination*.

## Primitives

### 1) Task list

Source of truth is your task system (recommended: `$st`).

Fabric requirements:
- stable `task_id`
- `status`: `pending|in_progress|blocked|completed`
- `scope`: paths/globs (exclusive locks)
- `validation`: commands that prove completion

### 2) Mailbox

Mailbox is an append-only store of typed messages.

Message fields (minimum viable):
- `thread_id`: typically the `task_id`
- `from`: agent identity
- `to`: one identity or `broadcast`
- `type`: `claim|lease|proposal|critique|question|decision|blocker|proof|status`
- `body`: markdown/text
- `ts`: timestamp

Rules:
- Prefer short messages; put the full diff/proof output elsewhere and link it.
- Treat mailbox history as a **durable memory** and a **debug log** (good for `$seq` mining).

### 3) Leases

Leases are advisory reservations for file paths/globs.

Lease fields (minimum viable):
- `owner`: agent identity
- `scope`: list of paths/globs (exclusive by default)
- `mode`: `exclusive|shared`
- `ttl_seconds`
- `reason`: usually `task_id`

Rules:
- Leases are *advisory* but must be honored by schedulers.
- Expired leases are treated as not held.

## Protocol (Recommended)

These steps are the "happy path" for multi-agent execution:

1) **Register identity**
   - Each agent has a stable name (not "worker-3").

2) **Claim task**
   - Post `type=claim` to `thread_id=task_id`.
   - Scheduler updates task to `in_progress`.

3) **Acquire leases**
   - Post `type=lease` announcing scope + TTL.
   - Refuse or re-scope if there is a conflicting active exclusive lease.

4) **Work + communicate**
   - Post `proposal/critique/question/blocker/decision` messages to the task thread.
   - Prefer disproof: ask peers to falsify assumptions.

5) **Prove**
   - Post `type=proof` with the exact validation command(s) + pass/fail + key line.
   - Scheduler only marks `completed` after proof.

6) **Release leases**
   - Release early and explicitly; don't rely only on TTL.

## Quality gates (Hook-style)

Fabric enables cheap, enforceable gates:

- **No silent completion**: a task cannot transition to `completed` without a `proof` message.
- **No unscoped work**: a task cannot be claimed without a non-broad `scope` lease.
- **No orphan agents**: agents must periodically post a heartbeat or their leases expire.

Implement these gates either in the fabric service or in the orchestrator.

## Mesh integration

`$mesh` can remain the orchestrator, but when the fabric exists:

- Use mailbox threads as the artifact bus (instead of only in-prompt artifacts).
- Use leases to enable safe `parallel_tasks>1` and multi-instance work.
- Treat the orchestrator as the **integrator**:
  - only it applies patches, runs validation, and mutates `$st`.
  - worker instances/agents are read-only or diff-producing.

## Multi-instance ($cas) integration

To scale beyond per-instance `[agents].max_threads`:

- Run N instances (one per teammate).
- All instances connect to the same fabric.
- Exactly one instance is the integrator (patch/validation/git).
- All other instances:
  - read, propose, critique, synthesize diffs
  - publish results to mailbox threads
  - never touch `$st` or apply patches directly

This turns "more instances" into *real* parallelism without chaos.
