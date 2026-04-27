---
name: codebase-audit
description: Codex-native domain codebase auditing for security, UX/accessibility, performance, API design, copy, and CLI quality. Use when auditing code, assessing quality, finding issues, pre-launch review, or running an explicit parallel Codex subagent audit.
---

# Codebase Audit — Codex Native

## Purpose

Audit a local codebase through a named domain lens and return an evidence-backed report. The audit is report-only unless the user explicitly asks for fixes.

Domains:

- `security`
- `ux`
- `performance`
- `api`
- `copy`
- `cli`

## Codex Compatibility Rules

This skill is written for Codex only.

- Do not use Claude Code `Task`, `Agent`, `subagent_type`, or tool-call syntax.
- Do not assume a Claude-style agents directory inside the skill can create workers.
- Codex custom agents are separate TOML files under `.codex/agents/` or `~/.codex/agents/`.
- Codex subagents are expensive and should be used only when the user explicitly asks for parallel work, subagents, one agent per domain, or a multi-agent audit.
- When subagents are used, workers must stay read-only and return concise findings; the parent agent owns severity normalization, de-duplication, and final synthesis.

## Inputs

Resolve these from the user prompt and repository context:

- `domain`: one of the domains above, or a list for a multi-domain sweep.
- `scope`: whole repo by default, or user-provided files/directories/features.
- `depth`: `quick`, `standard`, or `deep`. Default: `standard`.
- `subagents`: true only when the user explicitly asks for Codex subagents or parallel agents.

If the domain is missing, choose the most likely domain from the prompt. For generic "audit this codebase" requests, use `security`, `performance`, and `api` for backend/service repos; use `security`, `ux`, and `performance` for frontend/product repos; use `security`, `cli`, and `performance` for CLI/tooling repos.

## Workflow

### 1. Establish repo context

Inspect only enough to classify the project and identify audit surfaces:

- repo layout, manifests, framework/runtime, package manager/build system
- `AGENTS.md`, README, docs, route/command entry points, tests
- dependency manifests and lockfiles when relevant
- target files or feature paths named by the user

Prefer `rg`, manifest reads, and targeted file inspection over broad exhaustive reads.

### 2. Load the relevant domain checklist

Use `references/CHECKLISTS.md` for domain-specific checks, `references/TOOLS.md` for commands, and `references/EXAMPLES.md` for report shape.

For a single-domain audit, go deep on that domain. For a multi-domain sweep, keep findings domain-separated and avoid spending the whole pass on one domain.

### 3. Find candidate issues

Use fast static discovery first:

- code search for known risky constructs
- dependency/config review
- tests and examples to understand intended behavior
- framework conventions and entry points

Then verify each candidate by reading the surrounding source. Do not report a finding unless you can explain the root cause and cite a concrete location. Prefer exact `file:line` citations. If a line number is unavailable after reasonable effort, cite the smallest path/symbol scope and say so.

### 4. Validate severity

Assign severity by user impact and exploitability:

| Severity | Criteria | Examples |
|---|---|---|
| Critical | Directly exploitable now, data loss, privilege escalation, production outage risk | SQL injection, auth bypass, destructive command path |
| High | Serious impact but needs conditions, scale, or uncommon access | missing CSRF on sensitive action, N+1 on hot path, broken pagination on core endpoint |
| Medium | Real issue with bounded blast radius | missing validation, confusing flow, vague error that blocks recovery |
| Low | Polish, best practice, maintainability, minor UX/copy/API friction | inconsistent naming, missing helper text, noisy CLI output |

Do not inflate severity. Do not count speculative risks as findings; list them under "Needs Verification" instead.

### 5. Report

Return this shape for each domain:

```markdown
# [Domain] Audit Report: [Project or Scope]

## Summary
- **Scope:** [repo/files/features inspected]
- **Mode:** [quick/standard/deep; single-agent or Codex subagents]
- **Total Findings:** N
- **Critical:** X | **High:** Y | **Medium:** Z | **Low:** W

## Critical Findings

### 1. [Finding title]
- **Location:** `path/to/file.ext:line`
- **Severity:** Critical
- **Issue:** [what is wrong]
- **Root Cause:** [why the code allows it]
- **Impact:** [user/security/performance/API/UX impact]
- **Recommended Fix:** [specific change]
- **Verification:** [test, command, repro, or manual check]

## High Findings
[Same format]

## Medium Findings
[Same format, terser]

## Low Findings
[Same format, terser]

## Needs Verification
- [Only plausible risks that need runtime access, credentials, production data, or user confirmation]

## Positive Signals
- [Important things the code is already doing correctly]
```

For quick multi-domain sweeps, return top 3 findings per domain and keep the total under 100 lines unless the user asks for more.

## Codex Subagent Workflow

Use this section only when the user explicitly asks for Codex subagents, parallel agents, or one agent per domain.

1. Split work by independent audit domain or disjoint repo scope.
2. Spawn one Codex custom agent per requested domain when the matching agent is installed:
   - `security` → `audit_security`
   - `ux` → `audit_ux`
   - `performance` → `audit_performance`
   - `api` → `audit_api`
   - `copy` → `audit_copy`
   - `cli` → `audit_cli`
3. Give every worker the same scope, depth, output schema, and instruction to avoid file edits.
4. Wait for all requested workers before final synthesis.
5. Merge results by domain, de-duplicate overlapping findings, normalize severity, and keep disagreements visible in `Needs Verification`.
6. If the custom agents are not installed, use Codex built-in `explorer` agents with the same domain-specific instructions, or run locally and state which fallback was used.

### Worker Prompt Template

Use this template when spawning a Codex subagent:

```text
Run a read-only [DOMAIN] audit for [SCOPE] using the codebase-audit checklist.
Depth: [quick|standard|deep].
Do not edit files.
Return findings only when backed by concrete source evidence.
For each finding include title, severity, location, issue, root cause, impact, recommended fix, and verification.
Also return Needs Verification and Positive Signals.
Keep output concise; the parent agent will synthesize the final report.
```

## Anti-Patterns

- Do not say "code is bad" without a concrete path, cause, and fix.
- Do not mix domains in one undifferentiated list.
- Do not report grep hits that were not manually verified.
- Do not edit files while running an audit unless the user asks for remediation.
- Do not create issues/tasks unless the user asks.
- Do not use external scanners that require installation, network access, or approvals unless the user asks or the command is already available and safe under the current sandbox.

## References

- `references/CHECKLISTS.md` — domain checklists and grep patterns
- `references/TOOLS.md` — tool suggestions by domain
- `references/EXAMPLES.md` — report examples
- `references/CODEX_SUBAGENTS.md` — Codex-only subagent prompts and install notes
