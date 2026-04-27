# Example Audit Reports

## Security Audit Excerpt

```markdown
# Security Audit Report: Example Project

## Summary
- **Scope:** `src/routes`, `src/db`
- **Mode:** standard; single-agent
- **Total Findings:** 4
- **Critical:** 1 | **High:** 2 | **Medium:** 1 | **Low:** 0

## Critical Findings

### 1. SQL Injection in Search Endpoint
- **Location:** `src/search.rs:42`
- **Severity:** Critical
- **Issue:** User input is concatenated into a SQL predicate.
- **Root Cause:** Query construction uses string formatting instead of bound parameters.
- **Impact:** An attacker can alter the query and read or modify data outside the intended search.
- **Recommended Fix:** Replace string construction with prepared statements and bound parameters.
- **Verification:** Add a test with a quote/control payload and confirm it is treated as data.
```

## CLI Audit Excerpt

```markdown
# CLI Audit Report: Example Tool

## Summary
- **Scope:** `src/cli`
- **Mode:** quick; Codex subagent `audit_cli`
- **Total Findings:** 3
- **Critical:** 0 | **High:** 1 | **Medium:** 1 | **Low:** 1

## High Findings

### 1. Successful Command Exits With Failure Code
- **Location:** `src/cli/main.rs:118`
- **Severity:** High
- **Issue:** The command prints successful output but exits with code 1.
- **Root Cause:** Success and failure paths share the same error-return branch.
- **Impact:** CI scripts and shell automation treat successful work as failed.
- **Recommended Fix:** Return `ExitCode::SUCCESS` on the success path and reserve non-zero codes for errors.
- **Verification:** Run `tool valid-command; echo $?` and assert `0`.
```

## Multi-Domain Synthesis Excerpt

```markdown
# Multi-Domain Audit Report: Example Service

## Summary
- **Scope:** whole repo
- **Mode:** standard; Codex subagents `audit_security`, `audit_performance`, `audit_api`
- **Total Findings:** 7
- **Critical:** 0 | **High:** 3 | **Medium:** 3 | **Low:** 1

## Security

### 1. Missing Ownership Check on Project Read
- **Location:** `src/routes/projects.ts:88`
- **Severity:** High
- **Issue:** The route verifies authentication but not project ownership.
- **Root Cause:** The query filters by project id only.
- **Recommended Fix:** Include `ownerId` or membership in the query predicate.

## Performance

### 2. Serial Await in Hot List Handler
- **Location:** `src/routes/feed.ts:134`
- **Severity:** High
- **Issue:** The handler awaits one enrichment call per row.
- **Root Cause:** Row enrichment is performed inside a loop instead of batching.
- **Recommended Fix:** Fetch enrichment data with one batch query keyed by ids.
```
