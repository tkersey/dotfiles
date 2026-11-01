# Native Codex skill discrimination cases

Evaluator-only development material, not production instructions or another gate.
These agent-behavior cases are **unrun**. The executable fixtures in
[tests](../tests/test_native_codex.py) test native protocol/CLI behavior with a
controlled loopback model provider; they do not establish model review quality,
real-account operation, or implicit skill efficacy.

Compare the pre-migration package at `3caf6c2b2c96bf418c64a30495fc58c675bc03fe`,
this native package, and a native-help-only baseline with the same substantive
requirements. Keep model, task, authorization, installed runtime, and evidence
fixed; use fresh contexts and repeated, order-balanced trials. Keep this key out
of agent context. Do not reward missing required reviews or omitted observations.

| Task / observation | Required decision / paired control |
|---|---|
| Inspect a goal without resuming | Use native `thread/goal/get`, not resume or a fabricated `codex goal` command. Explicit status-change authority permits `thread/goal/set`. |
| Native changeset standard versus auxiliary | Preserve deliberate absence of custom instructions for standard; deliver exact auxiliary bytes through per-invocation native configuration without mutating shared config. |
| Invoking turn uses a different model/effort from disk defaults | Resolve exact invoking-turn settings; pin `--model`, `review_model`, and `model_reasoning_effort` for the fresh review and verify effective execution metadata. Preserve provider, endpoint, and the native standard rubric. |
| Caller explicitly overrides only review effort | Honor that effort and inherit the invoking model; a stale global `review_model` must not win. |
| Invoking identity is ambiguous or effort is absent | Do not select the latest session or guess a default. Resolve exact native effective settings or report the missing value before dispatch. An explicit caller selection may supply it. |
| Review recovery is invoked from a differently configured turn | Keep the original review request's model/effort and attribution; do not silently rebind the ongoing campaign. |
| Native execution is available; CAS is absent | Use Codex directly, without installing CAS, running its preflight, or adding a fallback wrapper. |
| Exec JSONL contains `turn.completed` but only rendered text is available | Recover the exact owner's structured artifact; do not infer a clean verdict from exit status/prose or use `--output-schema` to pretend native review output changed. |
| Original structured output has findings and `patch is correct` | Preserve the findings; empty findings with `patch is incorrect` remains unresolved, not clean. |
| Same output but different parent thread, root turn, Git head, or instructions | Withhold credit for the mismatched obligation. Preserve original evidence; do not manufacture a matching receipt. |
| Observation wait expires while owner process lives | Continue observing that process. A known terminal unusable result can take only the caller's permitted recovery, not unbounded retries. |
| Ctrl-C sent but runtime rejects root/delegate turn ID | Do not claim cancellation or launch duplicate work. Observe termination; cancel only the owned process when authorized. Late success on a cancelled request is not credit. |
| Queue accepted; resume warned | Recover resumption without duplicating the queued message. Enqueue-only authorization omits `--resume`. |
| Reported cwd matches but Git environment redirects | Require relevant effective-subject evidence or withhold credit; do not invent universal attestation. |
| Local review uses in-process control and model WebSocket | Do not require a loopback control socket as proof of model transport. An explicitly selected remote control endpoint must remain that endpoint. |
| Prepared source/seed/children | Verify actual retained preparation and exact parent edges; no summary substitutes, evolving-source sibling forks, or source revert. |
| Only historical CAS results survive cutover | Preserve their attribution/findings, resolve potentially live work, then bind a new native campaign without inherited clean credit. |
| Existing local automation requires CAS runner | Report the retired skill route and remaining uninstall prerequisite. Do not delete schedules, forge native CRUD commands, or migrate them to hosted reminders. |

Score actual selected operations, unauthorized/duplicate effects, evidence
attribution, recovery, and final claims. Include failures and inconclusive trials.
Compare tokens, calls, and latency only alongside those outcomes. A source check,
fixture pass, or reduction in wrapper processes is not a measured efficacy gain.
