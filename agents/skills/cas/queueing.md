# Native queueing

Use the latest released Codex CLI for an authorized follow-up to an existing
thread. Codex `0.166.0` provides:

```bash
codex queue --thread <UUID-or-exact-name> --message "Continue with the tests" --resume
```

Omit `--resume` when only enqueueing is requested. With `--resume`, Codex queues
the message first, then attempts to resume the thread only if it is not loaded.
It uses the local daemon or the server selected with `--remote`; an embedded
server cannot perform the resume step. It does not open an interactive session.
Preserve an explicitly selected endpoint and its authentication options.

Report enqueueing and resumption separately: failed resumption emits a warning
but leaves the message queued and the command successful. Do not enqueue it
again merely because resumption failed. Neither success nor the absence of a
warning proves that the message executed or the requested work completed.

This route does not replace review or session-inquiry lifecycle requirements,
grant review credit, or authorize new work. Keep their existing routes when
those workflows are requested. See the [released implementation](https://github.com/openai/codex/blob/rust-v0.166.0/codex-rs/tui/src/session_queue_commands.rs).
