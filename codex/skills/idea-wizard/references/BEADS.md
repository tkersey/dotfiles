# Bead Creation Details

## Structure of a Good Bead

```bash
br create "Epic: Feature Name" -p 1 -t epic --body "
## Background
[Why this feature matters]

## Goals
- [Goal 1]
- [Goal 2]

## Non-Goals
- [What we're explicitly NOT doing]

## Considerations
[Technical constraints, user expectations, etc.]
"
```

## Subtask Pattern

```bash
# Create epic first
br create "Epic: Pattern Testing Tool" -p 1 -t epic

# Create tasks under epic
br create "Design CLI interface for pattern tester" -p 1 -t task
br create "Implement pattern compilation logic" -p 2 -t task
br create "Add test coverage for pattern tester" -p 2 -t task

# Add dependencies
br dep add bd-task1 bd-epic1    # task depends on epic existing
br dep add bd-task3 bd-task2    # tests depend on implementation
```

## Self-Documenting Comments

Every bead comment should answer:
1. **What** - What specifically needs to be done?
2. **Why** - Why is this important?
3. **How** - Key implementation approach
4. **Risks** - What could go wrong?
5. **Success criteria** - How do we know it's done?

## Test Tasks

Every feature should have companion test beads:

```bash
br create "Unit tests for pattern tester" -p 2 -t task --body "
## Coverage Requirements
- Test pattern compilation
- Test error handling for invalid patterns
- Test edge cases (empty, unicode, etc.)

## Logging
- Log test inputs and outputs
- Log timing for performance tracking
"

br create "E2E tests for pattern tester" -p 2 -t task --body "
## Scenarios
- Happy path: valid pattern matches
- Error path: invalid pattern rejected
- Integration: works with existing allowlist

## Logging
- Full command and response capture
- Timing and resource usage
"
```

## Dependency Best Practices

```bash
# Check for cycles IMMEDIATELY after adding deps
bv --robot-insights | jq '.Cycles'

# Visualize dependency tree
br dep tree bd-123

# View what's blocked
br blocked --json
```

## Priority Scale

| Priority | Meaning | Use For |
|----------|---------|---------|
| 0 | Critical | Blocking issues, security |
| 1 | High | Core features, user-facing |
| 2 | Medium | Enhancements, refactors |
| 3 | Low | Nice-to-haves |
| 4 | Backlog | Future consideration |
