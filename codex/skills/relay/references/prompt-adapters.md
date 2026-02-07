# Prompt Adapters

Use these adapters when the user asks for subagent coordination in natural language.

## "Be excellent to each other"

Interpret as:
- keep communication respectful and explicit,
- preserve one shared `thread_id` per task,
- require acknowledgements for coordination-critical messages,
- avoid stepping on files through reservations.

Execution pattern:
1. `scripts/relay.py start`
2. `scripts/relay.py prepare`
3. `scripts/relay.py reserve`
4. `scripts/relay.py send --ack-required --thread <task-id>`
5. `scripts/relay.py poll` + `scripts/relay.py ack`

## "Use this with my subagents"

Interpret as:
- bootstrap each agent identity in the same `project_key`,
- give each agent bounded file scopes,
- route every update through the shared task thread.

Execution pattern:
1. Register/bootstrap all active agents.
2. Reserve narrow path scopes per agent.
3. Send kickoff messages with explicit ownership and expected handoff.
4. Poll inbox after each local edit chunk.

## "Keep everyone synchronized"

Interpret as:
- no side-channel state,
- all decisions posted in-thread,
- ACK loop for critical instructions.

Execution pattern:
1. `scripts/relay.py send --ack-required`
2. `scripts/relay.py poll`
3. escalate via `scripts/relay.py link` and error playbooks if missing ACK or blocked routing.
