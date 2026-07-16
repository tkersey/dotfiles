# PR Readiness Policy

Decide the GitHub operation separately from the desired final PR state.

```yaml
pr_decision:
  operation: create | update | update-and-promote | blocked
  final_state: ready | draft | preserve
  compatibility_mode: ready | draft | update-existing | promote-draft | blocked
  reason:
  draft_allowed_reason:
```

Default final state is `ready`.

Use `draft` only when:

- user explicitly requests draft;
- validation is incomplete, blocked, failing, or caveated;
- in-scope tasks remain blocked, deferred, or open;
- early visibility is explicitly intended;
- required context is missing and the user asks to publish anyway;
- repository policy requires draft and the source is direct.

Actuation input cannot publish a draft. A repository policy that requires draft
therefore blocks actuation shipping until the policy or lifecycle is resolved.

Compatibility projection:

| Condition | operation | final_state | compatibility_mode |
|---|---|---|---|
| No open PR; fully ready | `create` | `ready` | `ready` |
| No open PR; warranted draft | `create` | `draft` | `draft` |
| Open PR; preserve current state | `update` | `preserve` | `update-existing` |
| Open draft; fully ready | `update-and-promote` | `ready` | `promote-draft` |
| Invalid or ambiguous state | `blocked` | `preserve` | `blocked` |

If work is complete and validation passes, create or promote to a ready PR by
default. Do not pass `--draft` unless `final_state: draft` and
`draft_allowed_reason` is not `none`.
