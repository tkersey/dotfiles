# $opt Session Output Template

Use this shape for parent-facing reports.

```text
$opt result:
- Target:
- Mode:
- Parent goal status:
- Evidence source:
- Subagent:
- Files inspected:
- Changes made:
- Outcome observation:
- Remaining risk:
- Suggested parent CAS status:
- Next recommended action:
```

## CAS status vocabulary

Use these terms for parent-side decision making:

- `continue`: useful progress, but success criteria are not yet proven.
- `complete_candidate`: all known requirements appear satisfied; parent should verify before marking complete.
- `blocked_candidate`: same concrete blocker has persisted and user/external state is required.

Do not let the subagent directly convert these suggestions into parent goal mutations.

## Evidence-source descriptor

```text
Evidence source:
- Kind: current-turn | shadow | tune | worktree | provided | mixed
- Locator: <session id/path, brief path, command output, file list, current conversation>
- Scope: <single turn, one watched session, recent history, explicit sessions, target package>
- Access method: <$shadow report, $tune brief, file read, command output, user text>
- Limitation: <what this source cannot prove>
```
