# Example invocations

## Authority-gated review with custom agents

```md
Use $adversarial-reviewer in Authority-Gated v1 mode.
Review the current branch against origin/main. Spawn the custom read-only authority agents if available. Preserve candidate inventory, no-finding countercases, authority clearance, veto ledger, and Reviewer Gate. Do not implement.
```

## Fast review without handoff

```md
Use $adversarial-reviewer in Fast mode. Return candidate inventory, material findings, non-findings, authority matrix, change agenda, and Reviewer Gate. Block remediation handoff if authority coverage is incomplete.
```
