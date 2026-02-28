# Industry Guardrail Pattern Baseline

Date anchor: February 28, 2026.

Purpose: provide a provider-agnostic baseline synthesized from major vendor guardrail documentation so `$guards` can reason in shared control primitives instead of vendor APIs.

## Source Set (Primary Docs)

- OpenAI: Guardrails Python docs, Moderation API docs.
- AWS Bedrock: Guardrails overview, content filters, automated reasoning checks.
- Google: Vertex configurable safety filters, Model Armor overview.
- Azure: Azure AI Content Safety jailbreak detection and prompt shields, Azure OpenAI content filters.
- Anthropic: Guardrail strengthening guidance and Constitutional AI safety framing.
- Cohere: Safety modes documentation.

If freshness is required, re-check these sources before finalizing.

## Normalized Control Layers

Use this common taxonomy across providers:
1. Input controls
2. Context controls
3. Model controls
4. Tool pre-call controls
5. Tool post-call controls
6. Output controls
7. Human approval controls
8. Audit and traceability controls

## Cross-Provider Pattern Map

| layer | portable control pattern | common provider support signal |
| --- | --- | --- |
| Input | prompt and content risk classification, jailbreak detection | widely supported via safety/content policy surfaces |
| Context | retrieval/source trust checks, indirect prompt-injection filtering | partially explicit; often requires composition with app logic |
| Model | configurable harm thresholds, policy category filtering | widely supported with vendor-specific category models |
| Tool pre-call | schema validation, allowlists, least-privilege capability scoping | usually app-owned; some providers offer policy hooks |
| Tool post-call | argument/result inspection before side effects commit | primarily app-owned, with optional vendor moderation pass |
| Output | content filtering, redaction, safe completion transforms | widely supported across providers |
| Human approval | step-up approval for high-risk actions | mostly app-orchestration responsibility |
| Audit | decision logs, policy version traceability, replayability | partially supported; full audit chain is usually app-owned |

## Guardrail Requirements For Tool Misuse Resistance

For high-risk or critical scenarios, require all of these:
- Explicit tool capability allowlist.
- Strict argument schema validation before execution.
- Side-effect classifier to separate read-only vs mutating actions.
- Fail-closed default for mutating actions when policy confidence is low.
- Human approval gate for destructive, financial, credential, or regulated operations.
- Immutable audit event for allow/block/escalate decisions.

## Guardrail Requirements For Compliance-Grade Traceability

Minimum control set:
- Versioned policy object with change history.
- Deterministic decision record (`input class`, `policy version`, `decision`, `reason`).
- Replay path to reproduce allow/block outcomes.
- Segregation of duties for policy editing vs production override approval.
- Escalation SLA for unresolved high-risk decisions.

## Portability Hazards

Expect translation work when moving across providers:
- Different safety category taxonomies and threshold semantics.
- Different direct support for indirect prompt-injection defenses.
- Different logging/telemetry granularity for policy decisions.
- Different built-in vs application-owned responsibility split for tool-call guardrails.

Treat these as explicit migration risks in residual-risk sections.

## Assurance Profiles

Use these profiles as defaults:

| profile | intended context | mandatory properties |
| --- | --- | --- |
| `L1-baseline` | internal low-risk assistants | layered controls + logging + rollback path |
| `L2-production` | customer-facing or medium-risk automation | full control matrix + risk-tiered human gate + replayable decision trail |
| `L3-regulated` | high-stakes or regulated workflows | fail-closed high-risk posture + dual-control approvals + auditable policy lineage |

## Acceptance Heuristics

The output is not complete unless:
1. High-risk scenarios are fail-closed with explicit escalation.
2. Every major requirement maps to a validation check.
3. Residual risks include probability, impact, trigger, and owner.
4. Rollback triggers are concrete and monitorable.
5. Main plan text remains provider-agnostic.
