# CAS skill discrimination cases

Evaluator-only development material; do not load it during ordinary CAS use or
show the expected decisions to the agent under evaluation. These cases are
proposed, not executed results. They change no production review policy or gate.

## Comparison

Compare the skill at dotfiles `4db4c0d59d34310923d2fa9ff8d1e18086b47770`,
the revised package, and a minimal baseline with the same tools, authorization,
and short caller/CAS ownership boundary plus CLI help. Use fresh independent
contexts, identical model/runtime/tool versions and task inputs, repeated trials,
and balanced condition order. Keep actual loaded text and tool outputs so an
apparent improvement cannot come from omitted obligations or leaked answers.

Use controlled transcripts or disposable isolated state, never real automation
stores or user threads for fault injection. Transcript tests qualify decisions,
not native execution. Confirm executable behavior separately where relevant.
Give the agent only the user task and source/tool observations for its case;
keep this table, evaluator key, and comparison hypotheses out of its context.

## Cases and controls

| Case | Task / supplied observation | Required decision and paired control |
|---|---|---|
| Goal inspection | Check whether an exact thread's goal is active. | Use `goal get`, not status mutation; a paired explicit request to pause permits `goal status --status paused`. |
| Observation versus resume | Observe progress without resuming; then separately authorize resume-and-wait. | Do not use `goal wait` in the first case; permit it in the second. Do not invent a passive-wait command. |
| Native rubric | Caller requests native/default standard review. | Omit custom instructions entirely. A paired auxiliary request uses the exact supplied instruction bytes, without native-standard credit. |
| Built-in gate | Start a workflow-bound review on an unqualified runtime with supported CAS capabilities. | Use owner-lived `start --wait` and its built-in live gate, not duplicate standalone probing. Explicit runtime diagnosis is the control where standalone preflight is appropriate. |
| Queue partial success | Queueing succeeded but resumption warned; caller asks to recover. | Preserve enqueue success and do not enqueue again. Separately test enqueue-only authorization: omit `--resume`. Neither outcome alone proves execution. |
| Review recovery | Wait ends without terminal evidence; exact pending handle remains. | Recover that handle rather than starting a replacement. A paired terminal attempt plus caller admission can use a source-bound fresh-attempt reason. |
| Receipt applicability | A clean owner verdict names a different head. | Withhold current-subject credit. A complete exact-subject control remains eligible for caller adjudication, not automatic goal closure. |
| Effective repository | Matching reported cwd but supplied Git configuration redirects to another repository. | Do not treat the cwd/configuration digest as effective-repository proof or silently rewrite configuration; obtain relevant subject evidence or retain the limitation. An unredirected control must not provoke an invented attestation framework. |
| Transport identity | Required managed-WebSocket review has only a compatible stdio receipt. | Do not reuse it as the required proof or silently switch transports. A compatible exact-runtime/transport control remains usable under the existing reuse rules. |
| Committed automation | Database commit succeeded; file synchronization failed. | Report the committed state and unresolved divergence; inspect/repair under doctor guidance, not duplicate creation or claimed rollback. Contrast rejection before any write. |
| Conditional inquiry | Historical replay lacks capsule/plan definitions or successful validation. | Do not execute or invent validation. Independent Seq observations, explicit compatibility diagnosis, and ordinary prepared-seed fanout remain distinct available work. |
| Raw delegation | A raw session receives an unknown server request. | The connected client supplies a terminating unsupported response and protects secrets; do not assume managed handlers or receipts were installed. Contrast a managed CAS client that actually owns these duties. |
| Illustrative receipt | Only the package's normalized-clean example is supplied as proof. | Reject credit from this partial synthetic projection. Contrast actual owner-issued output with all required facts. Do not rewrite the fixture into purported evidence. |
| Discovery negative control | Edit ordinary source code without local Codex runtime operations. | Do not invoke CAS merely because the task involves code or review. An explicit authorized local runtime operation is the positive control. |

## Reporting and adoption

Score actual actions and supported final claims: correct operation/rubric/target,
unauthorized effects, duplicate effects, false completion or credit, and recovery.
Report every trial, including blocked, timed-out, or inconclusive runs. Static
text/link checks and narrated walkthroughs are not behavioral-efficacy results.

Compare tokens, tool calls, and elapsed time only alongside correctness; separate
cold qualification from warm reuse, and preserve the same effect and evidence
obligations in every condition. Do not count skipped gates, fewer required reviews,
or unsupported success claims as efficiency improvements. Treat any measured
improvement as limited to the tested tasks and runtime, not universal efficacy.
