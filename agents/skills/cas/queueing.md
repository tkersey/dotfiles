# Native queueing

For an authorized follow-up to an existing thread, select one route before sending.
Use `codex queue` when message delivery and optional loading express the operation
without changing the original request's effective settings. Use
[direct app-server](app-server.md#existing-thread-follow-up) when explicit
configuration control or observation through an existing persistent connection
is required. Neither route grants additional retry authority or review credit.

Use the selected installed Codex interface; Codex `0.166.0` provides:

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
On lost acknowledgement, inspect the exact thread and any known queued message
or turn before retrying. If acceptance cannot be resolved, hold the follow-up;
absence of a reply is not rejection. A route switch must not send the same
possibly accepted assignment again through `turn/start`.

This route does not replace native review or prepared-fork lifecycle requirements,
grant review credit, or authorize new work. Keep their existing routes when
those workflows are requested. For a completed review with missing inquiry, apply
the [review recovery guidance](reviews.md#recover-incomplete-review-inquiry) before
submitting the follow-up. See the [released implementation](https://github.com/openai/codex/blob/rust-v0.166.0/codex-rs/tui/src/session_queue_commands.rs).
