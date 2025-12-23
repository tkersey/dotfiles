# Agentic-Flow CLI

## Conventions
- Use `npx agentic-flow` for one-off runs.
- Use `agentic-flow` if the CLI is installed globally.

## Initialize Swarm
```bash
npx agentic-flow hooks swarm-init --topology mesh --max-agents 5
```

## Spawn Agents
```bash
npx agentic-flow hooks agent-spawn --type coder
npx agentic-flow hooks agent-spawn --type tester
npx agentic-flow hooks agent-spawn --type reviewer
```

## Orchestrate Tasks
```bash
npx agentic-flow hooks task-orchestrate \
  --task "Build REST API with tests" \
  --mode parallel \
  --timeout 300000
```

## Coordination Hooks
```bash
npx agentic-flow hooks pre-task --description "Build API"
npx agentic-flow hooks post-task --task-id "task-123"
npx agentic-flow hooks session-restore --session-id "swarm-001"
```

## Notes
- Topology values: `mesh`, `hierarchical`, `adaptive`.
- Mode values: `parallel`, `pipeline`, `auto` (or `adaptive` depending on CLI version).
- Prefer explicit `--timeout` for every orchestration command.
