# CRASH-RECOVERY-AND-RESUMABILITY — Long-running ops, partial failures, mid-state recovery

Modern AI agents pause and resume across sessions. A coding agent may start an operation, hit a rate limit, sleep for hours, and continue. A CLI invocation that's interrupted mid-state must be **recoverable** — without manual cleanup, without data loss, without the agent needing to know the tool's internal state machine.

This file gives the patterns.

---

## The agent's resume model

Agents resume after:

| Cause | Frequency |
|-------|-----------|
| Rate limit hit | Hourly |
| Manual approval needed | Daily |
| Network outage | Occasional |
| OS reboot | Weekly+ |
| Token expiry | Daily |
| Multi-day workflow | Per-project |

A canonical resume sequence:

1. Agent picks up in a new session (or after pause)
2. Agent must determine: "what state was I in?"
3. Agent invokes `<tool> status --json` (or equivalent introspection)
4. Tool reports state; agent decides next action
5. Agent resumes via `<tool> resume` or `<tool> continue`

CLIs that don't support this leave agents stuck.

---

## The three resume patterns

### Pattern R-1: Stateless verb (default)

Most verbs should be **stateless** — same input → same effect, every time.

- `<tool> list` is naturally stateless (read-only)
- `<tool> add foo` should be idempotent (re-running with same input is no-op or warning)
- `<tool> delete X-001` should detect "already deleted" and exit 0

Stateless verbs don't need resume logic. They just work.

### Pattern R-2: Stateful long-running verb with explicit resume

For verbs that take minutes/hours and have intermediate state:

```bash
$ <tool> sync --output=run.log
[progress streaming...]
[interrupted]

$ <tool> sync --resume run.log
[picks up where it left off]
```

OR (more elegant):

```bash
$ <tool> sync --run-id=$(uuidgen)
[interrupted]

$ <tool> sync --resume --run-id=<id>
```

Tool stores intermediate state in a known location (e.g. `$XDG_STATE_HOME/<tool>/runs/<id>/`).

### Pattern R-3: Stateful daemon with checkpoint

For daemon-style state (long-running indexes, builds):

- Tool checkpoints periodically to disk
- On startup, tool detects existing state and offers `--resume`
- `<tool> doctor --json` reports interrupted runs

---

## Idempotency tokens

For mutating verbs that go over network (e.g. POST to API):

```bash
$ <tool> create-resource --idempotency-key=$(echo "create-foo-$DATE" | sha256sum)
```

If the call is retried with the same idempotency-key, the tool returns the existing resource (instead of creating duplicate).

Capabilities surface:

```jsonc
"create_resource": {
  "supports_idempotency_key": true,
  "idempotency_key_lifetime": 3600
}
```

---

## State files (where to put them)

Use **XDG state dirs** for resumable state:

| Type | Location |
|------|----------|
| Resumable run state | `$XDG_STATE_HOME/<tool>/runs/<id>/` |
| Checkpoints | `$XDG_STATE_HOME/<tool>/checkpoints/` |
| Crash dumps | `/tmp/<tool>-crash-<pid>.jsonl` (or `$XDG_RUNTIME_DIR`) |
| Lock files | `$XDG_RUNTIME_DIR/<tool>-<resource>.lock` |
| Cache | `$XDG_CACHE_HOME/<tool>/` |
| Config | `$XDG_CONFIG_HOME/<tool>/` |

Document in capabilities:

```jsonc
"state_dirs": {
  "runs":     "$XDG_STATE_HOME/mytool/runs",
  "cache":    "$XDG_CACHE_HOME/mytool",
  "config":   "$XDG_CONFIG_HOME/mytool"
}
```

---

## The doctor verb (resume-aware)

`<tool> doctor --json` should report interrupted state:

```jsonc
{
  "ok": false,
  "data": {
    "components": {
      "runs": {
        "state": "degraded",
        "details": "1 interrupted run found",
        "interrupted_runs": [
          {"id": "run-abc123", "started": "2026-05-06T10:00:00Z", "phase": "fetching", "resumable": true}
        ]
      }
    },
    "recommended_action": {
      "command": "mytool sync --resume --run-id=run-abc123",
      "rationale": "interrupted run is resumable"
    }
  }
}
```

The agent reads this, finds the interrupted run, resumes.

---

## Transactional mutations

For verbs that change multiple things together, use transactions:

```bash
$ <tool> import file.json --json
{"ok": true, "data": {"imported": 50, "failed": 0, "transaction_id": "txn-abc"}}

$ <tool> import file.json --json --on-error=rollback
[fails midway]
{"ok": false, "data": {"imported": 0, "failed_at": 25, "transaction_id": "txn-abc", "rolled_back": true}, "errors": [...]}
```

`--on-error` modes:
- `rollback`: undo previous successful imports if any fail
- `continue`: log failures, complete what's possible
- `abort` (default): stop at first error; don't roll back; partial state remains

The agent can branch on `data.rolled_back`.

---

## Heartbeats for long ops

If an operation takes > 30s, emit periodic heartbeats to stderr:

```bash
$ <tool> long-op
[2026-05-06T10:00:00Z heartbeat] mytool long-op — running 30s — phase: fetching (12% complete)
[2026-05-06T10:00:30Z heartbeat] mytool long-op — running 60s — phase: processing (45% complete)
[2026-05-06T10:01:00Z heartbeat] mytool long-op — running 90s — phase: writing (87% complete)
```

Heartbeat format is grep-friendly. Agents can monitor stderr for "still alive" + progress.

In JSON mode:

```bash
$ <tool> long-op --json
{"event": "heartbeat", "phase": "fetching", "elapsed_s": 30, "progress": 0.12}
{"event": "heartbeat", "phase": "processing", "elapsed_s": 60, "progress": 0.45}
{"event": "complete", "elapsed_s": 95, "imported": 50}
```

NDJSON; agent reads line-by-line; stops on `complete` event.

---

## Crash dumps (revisited)

When the tool crashes (panic, segfault, uncaught exception), it should:

1. Write a structured crash dump to `/tmp/<tool>-crash-<pid>.jsonl`
2. Print a one-line summary to stderr
3. Print "report:" pointer to the crash file
4. Exit with crash exit code (usually `139` for SIGSEGV, `134` for abort, or custom)

```jsonl
{"event":"panic","ts_iso":"2026-05-06T12:34:56Z","message":"...","file":"src/sync.rs","line":42}
{"event":"thread_main_backtrace","frames":[...]}
{"event":"env","tool_version":"0.4.1","rust_version":"1.74"}
{"event":"recoverable","run_id":"run-abc123","resume_command":"mytool sync --resume --run-id=run-abc123"}
```

Agent reads the file, decides whether to resume or report.

---

## Locks and TTLs

For locks (advisory, per Operator 🛂):

```bash
$ <tool> reindex
error: lock /var/run/mytool.lock held by PID 12345 (started 2 minutes ago, ttl 1800s)
  remaining: 28 minutes
  options:
    wait:    mytool reindex --wait=300  (waits up to 5 min)
    force:   mytool reindex --force-unlock --reason='PID 12345 confirmed dead'  (DANGEROUS)
exit 4 (transient-failure; retry safe after wait)
```

TTL on locks ensures crashed processes don't leave permanent locks. Force-unlock is gated behind explicit `--reason` (audit trail).

---

## Multi-step workflows

For verbs that compose into multi-step workflows:

```bash
$ <tool> workflow start phase-1 --run-id=run-abc
{"phase": "phase-1", "complete": true, "next": "phase-2"}

$ <tool> workflow continue --run-id=run-abc
{"phase": "phase-2", "complete": true, "next": "phase-3"}

$ <tool> workflow continue --run-id=run-abc
{"phase": "phase-3", "complete": true, "next": null}
```

Or single command with `--auto-continue`:

```bash
$ <tool> workflow run --auto-continue --run-id=run-abc
[runs all phases; checkpoints after each]
```

Recoverable mid-workflow:

```bash
$ <tool> workflow continue --run-id=run-abc
# picks up at the failed phase; doesn't redo completed phases
```

---

## Recovery from corrupt state

If state files become corrupt (disk full mid-write, agent killed mid-write), the tool should:

1. Detect corruption on next read (checksum mismatch)
2. Quarantine the corrupt file (rename to `.corrupt-<ts>`)
3. Exit with helpful error:

```
error: state file at $XDG_STATE_HOME/mytool/runs/run-abc/state.json is corrupt
  quarantined to: state.json.corrupt-20260506T123456
  suggestions:
    repair:        mytool repair --run-id=run-abc
    discard:       mytool discard --run-id=run-abc --yes
    inspect:       mytool inspect-corrupt /path/to/quarantined
exit 3 (tool-environment-error)
```

NEVER silently delete corrupt state. Quarantine + diagnose.

---

## Atomic file writes

For all file-write paths in the tool, use atomic-write:

```rust
// Rust: write to tempfile, fsync, rename
let tmp = path.with_extension("tmp");
std::fs::write(&tmp, &data)?;
std::fs::File::open(&tmp)?.sync_all()?;
std::fs::rename(&tmp, &path)?;
```

This prevents half-written files. Critical for resumable state.

---

## Capabilities mention

```jsonc
"resumability": {
  "supports_resume":          true,
  "supports_idempotency_key": true,
  "supports_transactions":    true,
  "state_dir":                "$XDG_STATE_HOME/mytool/runs",
  "lock_ttl_seconds":         1800,
  "heartbeat_interval_s":     30,
  "checkpoint_interval_s":    60
}
```

Agents can introspect resumability before launching long ops.

---

## Regression tests for resumability

```bash
# audit/regression_tests/RES-001__interrupt_and_resume.test.sh
set -euo pipefail
TOOL="${TOOL_BIN}"
RUN_ID=$(uuidgen)

# Start an op in background
$TOOL sync --run-id=$RUN_ID &
PID=$!
sleep 2

# Interrupt
kill -TERM $PID
wait $PID || true

# Verify state file exists
[ -f "$XDG_STATE_HOME/mytool/runs/$RUN_ID/state.json" ] || {
  echo "FAIL: no state file written" >&2; exit 1; }

# Verify doctor reports the interrupted run
$TOOL doctor --json | jq -e ".data.components.runs.interrupted_runs[] | select(.id == \"$RUN_ID\")" > /dev/null || {
  echo "FAIL: doctor doesn't report interrupted run" >&2; exit 1; }

# Resume
$TOOL sync --resume --run-id=$RUN_ID

# Verify it completed
$TOOL doctor --json | jq -e ".data.components.runs.interrupted_runs == []" > /dev/null || {
  echo "FAIL: run still flagged as interrupted" >&2; exit 1; }

echo OK
```

---

## Per-archetype resumability emphasis

| Archetype | Resumability needs |
|-----------|---------------------|
| Search tool | Low (queries are fast; just re-run) |
| Package manager | High (installs are slow + transactional) |
| Build tool | High (incremental builds are inherently resumable) |
| Test runner | Medium (re-running failed tests is a resume pattern) |
| SCM tool | High (commits, rebases, merges all transactional) |
| Daemon CLI | High (the daemon IS long-running state) |
| Migration tool | Critical (transactional + rollback essential) |

---

## Anti-patterns

- **Silent re-do**: Re-running a long op without `--resume` re-does everything. Should detect and prompt.
- **Half-written state**: No atomic-write means crashes leave state corrupt.
- **Locks without TTL**: Crashed processes leave permanent locks; tool can't recover.
- **No idempotency key for network calls**: Retries duplicate side effects.
- **No heartbeats for long ops**: Agents time out and abort.
- **No way to inspect state**: Agent doesn't know what to resume.

---

## Related

- `OBSERVABILITY-AND-TELEMETRY-SURFACES.md` — heartbeats and trace files
- `JSON-SCHEMA-PATTERNS.md` — NDJSON for streaming events
- `methodology/AGENT-API-DESIGN-PRINCIPLES.md` § "Agent-driven workflow" — the design intent
- Operator 🔬 (Single-Step-Atomicity), 🧷 (Idempotency-Pin) — applicable here
