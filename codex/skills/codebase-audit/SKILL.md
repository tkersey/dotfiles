---
name: codebase-audit
description: "Run evidence-backed Codex-native audits for security, UX/accessibility, performance, API design, copy, or CLI quality. Use for code audits, issue finding, quality assessment, pre-launch review, or explicit parallel domain audits. Report only unless fixes are explicitly requested."
---
# Codebase Audit

## Mission

Audit one repository scope through one or more named domain lenses and report
only source-verified findings.

Domains:

```text
security | ux | performance | api | copy | cli
```

## Common single-agent path

1. Bind domain, scope, depth, and current artifact state.
2. Inspect only enough guidance, manifests, entry points, tests, and dependency
   surfaces to classify the project.
3. Load the selected domain checklist.
4. Use targeted search to find candidates.
5. Read surrounding source and verify root cause before reporting.
6. Assign severity by plausible impact and exploitability, not code size.
7. Cite the smallest available path, line, symbol, command, or configuration.
8. Separate verified findings from `Needs Verification`.
9. Include important positive signals.
10. Stop without editing, creating issues, or installing scanners unless the
    user explicitly authorizes that work.

A grep hit is not a finding.

## Conditional disclosure

Load [references/CHECKLISTS.md](references/CHECKLISTS.md) only for the selected
domain or domains.

Load [references/TOOLS.md](references/TOOLS.md) only when choosing audit commands
beyond the repository's existing safe tools.

Load [references/EXAMPLES.md](references/EXAMPLES.md) only when the requested
report shape is ambiguous.

The complete pre-split contract is preserved byte-for-byte in
[FULL_CONTRACT.md](FULL_CONTRACT.md). Do not load it for an ordinary
single-domain audit. Load it only for explicit parallel subagents, multi-domain
deep synthesis, exact worker packet validation, or an unported edge route. Its
frontmatter is archived source, not a second skill definition.

## Parallel route

Use subagents only when the user explicitly asks for parallel agents,
subagents, or one agent per domain. The parent owns scope, artifact binding,
packet validation, severity normalization, deduplication, and final synthesis.
Workers remain read-only and receive only their domain checklist and packet
contract.

## Finding standard

Every accepted finding includes:

```text
title
severity
location
issue and root cause
impact
specific remedy
verification
```

Do not inflate severity or report speculative risks as defects.
