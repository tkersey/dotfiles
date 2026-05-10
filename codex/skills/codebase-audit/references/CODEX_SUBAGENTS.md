# Codex Subagents for Codebase Audit

This file describes the Codex-only subagent setup for `codebase-audit`.

## Install Locations

Codex discovers skills from:

- project skills: `.agents/skills/<skill-name>/SKILL.md`
- user skills: `$HOME/.agents/skills/<skill-name>/SKILL.md`

Codex discovers custom agents from:

- project agents: `.codex/agents/*.toml`
- user agents: `$HOME/.codex/agents/*.toml`

This package includes both:

- `.agents/skills/codebase-audit/`
- `.codex/agents/audit-*.toml`

## Available Audit Agents

| Domain | Codex custom agent |
|---|---|
| security | `audit_security` |
| ux | `audit_ux` |
| performance | `audit_performance` |
| api | `audit_api` |
| copy | `audit_copy` |
| cli | `audit_cli` |

## Prompts That Trigger Parallel Codex Work

Use explicit language so Codex is allowed to spawn subagents:

```text
Use $codebase-audit with Codex subagents. Spawn one agent for security, one for performance, and one for API. Require the shared specialist packet contract, wait only while packets make progress, then synthesize a prioritized report from valid packets and file:line evidence.
```

```text
Run a parallel codebase audit with one Codex subagent per domain: security, UX, performance, API, copy, and CLI. Keep all subagents read-only and require packet-native, scoped, evidence-bearing outputs.
```

## Parent-Agent Synthesis Rules

The parent agent should:

1. launch all independent domain workers before waiting;
2. keep workers read-only;
3. assign `artifact_state_id` and exact scope for every worker;
4. validate packets against `../../references/specialist-packet-contract.md`;
5. close stale or low-value workers when local evidence is enough to synthesize;
6. de-duplicate overlapping findings;
7. normalize severity across domains;
8. preserve uncertainty under `Needs Verification` instead of promoting it to a finding;
9. return a final report, not raw worker transcripts.

## Fallback

If the `audit_*` custom agents are not installed, Codex can still run the skill. Use either built-in `explorer` subagents with the worker prompt template in `SKILL.md`, or run the audit in the parent thread. State the fallback in the report summary.
