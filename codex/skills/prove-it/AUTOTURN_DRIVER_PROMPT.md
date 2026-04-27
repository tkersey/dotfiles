# Auto Gauntlet driver prompt

Use this prompt with a thread automation, MCP `codex-reply`, CLI `codex exec resume`, or any host process that can continue the same conversation.

```text
Continue prove-it from the checkpoint. Execute exactly the next uncompleted numbered round only. Stop only if the Terminality Check is terminal.
```

Driver loop policy:

1. Submit the prompt to the same conversation/thread.
2. Stop if the latest reply contains any of:
   - `Status: COMPLETE`
   - `Action: STOP`
   - `Terminal verdict: PROVEN`
   - `Terminal verdict: DISPROVEN`
   - `Terminal verdict: ROUND_10_COMPLETE`
   - `Terminal verdict: USER_STOPPED`
3. Otherwise, submit the same prompt again.
4. Never ask the model to run more than one numbered round per reply.
