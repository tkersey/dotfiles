# Question Interface

Load this reference only after a candidate question passes the `$grill-me` ownership, materiality, dependency, and observation checks.

## Preflight

Ask only when every answer is `yes`:

```text
Is the answer unavailable from evidence?
Does the user own the decision?
Can different answers materially change the admissible downstream outcome?
Are all prerequisites settled?
Can conversation honestly settle it?
Is it one conceptual decision?
Has it not already been answered?
Is no equivalent question already pending?
Can the consequence of each live option be explained?
```

If an equivalent question is pending, do not send another. Otherwise research,
decide, default, defer to observation, or prune as appropriate.

## Local context

The user must be able to tell why the question follows and what it controls. Use the smallest natural-language bridge that supplies that information.

Default shape:

```text
Why this is next: <settled prerequisite or relevant evidence>; this decides <downstream consequence>.
```

Add a continuity sentence only when the relation to the previous answer is not already obvious. Do not emit a mandatory mini-report, lane matrix, hidden scores, or premature summary.

## Choose the supported question channel

Follow the host's current tool contract and mode restrictions. Tool availability
alone does not authorize using it for approvals or blocking decisions.

Use `request_user_input_async` when permitted to ask while independent authorized
work continues. Use `request_user_input` only for questions the current mode permits
it to carry. If a required answer cannot use either tool, ask one concise,
self-contained plain-text question. Do not turn a missing answer into approval.

Keep the skill's small question budget across deliveries, not just within one
call. The live schema is authoritative; do not transfer fields between tools.

### Synchronous questions

For `request_user_input`, use the live question fields: `id`, `header`, `question`,
and `options` containing `label`/`description` objects. Keep the conceptual id stable,
the header short, and the question atomic. State each option's consequence in its
description.

This Codex tool requires nonempty options; use two or three honest, mutually
exclusive choices. The interface supplies an Other/free-text escape alongside
those choices, so do not add a duplicate Other or placeholder option. That escape
does not make a free-text-only request with omitted or empty options valid.

### Asynchronous questions

For `request_user_input_async`, the `questions` entries use a `title` and optional
string `options`, not synchronous `id`, `header`, `question`, or option objects.
Keep conceptual ids internally. Make each title self-contained, including the
context needed to decide; put consequences in the title or concise option strings.
Omit `options` for a free-text-only question rather than fabricating choices. When
async is not permitted for that question, use the plain-text fallback.

The immediate `{"accepted":true}` response acknowledges delivery, not the user's
decision. Replies arrive later as new user messages. Keep the question pending in
the existing judgment graph until reconciled under the skill's answer lifecycle.
A preselected first option is not a submitted answer.

In either channel, put a recommended option first and suffix it with
` (Recommended)` only when evidence or locked priorities independently justify it.

## Fallback

Ask the necessary question naturally, with enough context to explain what its
answer controls. Do not expose tool availability, internal IDs, or a protocol
banner. Keep the conceptual ID internally if the decision must be re-asked.

## Answer handling

- Interpret actual user responses: selected labels and `user_note:` text when
  supplied by the synchronous tool, or later user messages for async questions.
  The async tool result itself is not an answer.
- Use question context or host-provided correlation to match delayed replies.
  When a reply cannot be matched unambiguously, clarify only the material
  ambiguity; do not guess or settle unrelated pending decisions.
- Strip ` (Recommended)` before interpreting the selected label.
- Mine notes for scope changes, dependencies, constraints, risks, and new decisions.
- A missing answer remains unresolved only when the question is still material.
- `I don't know` is a valid answer. Reclassify the decision as model-owned, observation-owned, safely defaultable, or explicitly nonblocking.
- When the user says “use your judgment,” make and own the model decision; do not record it as independently user-authored.
- When an answer introduces several decisions, split them in the graph before asking; keep visible questions atomic.

## Question quality

Prefer:

```text
Which compatibility posture should govern the public API?
```

over:

```text
Should we preserve compatibility, migrate consumers, update docs, add telemetry,
and decide the rollout window?
```

The first locks a prerequisite. Its consequences may create descendants for later rounds; they do not belong in the same question.
