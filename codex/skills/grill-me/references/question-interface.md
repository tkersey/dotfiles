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
Can the consequence of each live option be explained?
```

Otherwise research, decide, default, defer to observation, or prune.

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

For `request_user_input`, send one to three questions.

Each question contains:

- `id`: stable `snake_case` conceptual identifier;
- `header`: short human-readable label, at most 12 characters;
- `question`: one atomic sentence;
- `options`: two or three mutually exclusive choices when the answer space can be represented honestly.

Each option description states its consequence or trade-off. Put a recommended option first and suffix it with ` (Recommended)` only when the recommendation is independently supported by evidence or locked priorities.

Do not add an `Other` option or a free-text placeholder; the interface supplies
free-text input. Use free-text input when the live choices cannot honestly fit
the tool's option schema.

## Fallback

Ask the necessary question naturally, with enough context to explain what its
answer controls. Do not expose tool availability, internal IDs, or a protocol
banner. Keep the conceptual ID internally if the decision must be re-asked.

## Answer handling

- Treat selected labels and `user_note:` text as user-provided evidence.
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
