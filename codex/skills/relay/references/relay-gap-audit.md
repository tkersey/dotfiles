# Relay Gap Audit

Scope:
- Relay abstraction contract in `relay/SKILL.md`
- Adapter implementation in `relay/scripts/relay.py`
- Upstream semantics from `mcp_agent_mail`

Method:
- Score current relay behavior against `relay-philosophy.md` invariants.
- Prioritize gaps by coordination risk and recovery cost.
- Propose minimal-incision fixes only.

## Scorecard

| Area | Status | Notes |
|---|---|---|
| Stable verb facade | Pass | Clear verb map and remap support. |
| Macro-first workflow | Pass | `start/prepare/reserve/link` mapped to macros. |
| Ack semantics | Pass | `ack` mapped to idempotent upstream ack behavior. |
| Consent-aware routing | Partial | Supported upstream; playbook verification step is invalid. |
| Thread continuity | Partial | Contract mentions reply-in-thread; adapter has no `reply` verb. |
| Reservation lifecycle | Fail | “Release” step currently re-enters reserve flow with `--auto-release`. |
| Deterministic recovery | Partial | Playbooks exist, but adapter does not emit typed next actions. |
| Endpoint/config coherence | Partial | Repo examples include both `/api/` and `/mcp/` endpoints. |

## Findings (Ordered By Severity)

1. High: No true release verb (reservation lifecycle violation)
- Evidence:
- `relay` workflow step 6 suggests `reserve --auto-release` for completion.
- `reserve` maps to `macro_file_reservation_cycle`, which reserves first and only then optionally releases.
- Why it matters:
- Task completion should be a pure release action; reserve+release adds unnecessary write churn and transient conflict surfaces.
- Minimal incision:
- Add `release` verb mapped to `release_file_reservations`.
- Add CLI command: `release --project --agent [--path <glob>] [--id <reservation-id>]`.
- Update workflow step 6 and examples to use `release`.

2. High: Thread continuity contract is underspecified in adapter
- Evidence:
- `Thread Contract` instructs reply-in-thread; adapter has no `reply` verb.
- `send --thread` is optional, making accidental unthreaded task updates likely.
- Why it matters:
- Loss of thread continuity degrades summarization, traceability, and routing heuristics.
- Minimal incision:
- Add `reply` verb mapped to `reply_message`.
- Add CLI: `reply --project --sender --message-id --body [--to/--cc/--bcc]`.
- Make `send --thread` required by default; add explicit escape hatch `--allow-unthreaded`.

3. Medium: CONTACT_REQUIRED playbook contains a false verification step
- Evidence:
- Playbook says verify link with `relay.py --dry-run link ...`.
- `--dry-run` only prints outbound JSON-RPC payload, it does not verify server state.
- Why it matters:
- Operators may believe contact is established when no link exists.
- Minimal incision:
- Replace verification step with state read:
- Option A: add `contacts` verb mapped to `list_contacts`.
- Option B: call backend `list_contacts` directly in playbook text.

4. Medium: Deterministic recovery is manual-only in adapter output
- Evidence:
- Adapter exits with raw JSON-RPC error payload; it does not normalize error type to next actions.
- Why it matters:
- Coordination loops are slower and more error-prone under pressure.
- Minimal incision:
- Parse known error types (`CONTACT_REQUIRED`, `CONTACT_BLOCKED`, `RECIPIENT_NOT_FOUND`, `FILE_RESERVATION_CONFLICT`) and print one-line executable remedy suggestions from playbooks.

5. Low: Endpoint examples can cause environment drift
- Evidence:
- Repo shows both `http://127.0.0.1:8765/api/` and `http://127.0.0.1:8765/mcp/` MCP URLs.
- Relay default is `/api/`.
- Why it matters:
- Misconfigured clients may fail preflight and appear as intermittent transport errors.
- Minimal incision:
- Document one canonical relay default (`/api/`) and add an explicit note that endpoint path is deployment-configurable.

## Minimal-Incision Patch Plan

Patch A: Add lifecycle-complete verbs
- Add `release` and `reply` to `DEFAULT_TOOL_MAP`.
- Extend parser/argument builder with `release` and `reply`.
- Keep existing verbs unchanged for compatibility.

Patch B: Fix playbook verification semantics
- Update `error-playbooks.md` CONTACT_REQUIRED step 2 to use contact state inspection, not `--dry-run`.
- Optionally add `contacts` relay verb (`list_contacts`) for first-class verification.

Patch C: Strengthen thread discipline
- Require `--thread` in `send` unless `--allow-unthreaded` is supplied.
- Update examples and prompt adapters to prefer `reply` for continuity.

Patch D: Improve recovery ergonomics
- Add lightweight error post-processor in `relay.py` that emits executable next-step commands keyed by error type.

## Acceptance Checks After Patches

- `relay.py send` without `--thread` exits with actionable guidance unless `--allow-unthreaded`.
- `relay.py reply` sends threaded replies and preserves original thread.
- `relay.py release` releases active claims without creating new claims.
- CONTACT_REQUIRED playbook includes a real state verification step.
- Mock tests cover new verbs and argument mapping.

