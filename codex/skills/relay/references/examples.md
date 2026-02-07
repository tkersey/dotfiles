# Examples

## Example Prompts That Should Trigger This Skill

- "Coordinate five subagents on this refactor and keep them from clobbering each other."
- "Set up a comms loop so agents ack messages and stay in one thread per ticket."
- "Recover a failed agent-mail delivery and keep the task moving."

## Macro-First Session Bootstrap

```text
scripts/relay.py start \
  --project /abs/repo \
  --program codex-cli \
  --model gpt-5 \
  --task "Implement auth split"
```

## Prepare and Execute a Ticket Thread

```text
scripts/relay.py prepare --project /abs/repo --thread bd-482 --program codex-cli --model gpt-5
scripts/relay.py reserve --project /abs/repo --agent BlueLake --path 'src/auth/**' --reason bd-482
scripts/relay.py send --project /abs/repo --sender BlueLake --to GreenStone --subject '[bd-482] start auth split' --body 'Taking parser + middleware.' --thread bd-482 --ack-required
```

## Contact Recovery Sequence

```text
scripts/relay.py link --project /abs/repo --requester BlueLake --target RedForest --auto-accept
scripts/relay.py send --project /abs/repo --sender BlueLake --to RedForest --subject '[bd-482] contract check' --body 'Need API signature confirm.' --thread bd-482
```
