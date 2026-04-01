# Example Sessions

## Example 1: dcg (Destructive Command Guard)

### Phase 2 Output (30→5)

**Top 5 Ideas Generated:**

1. **Pattern Testing Tool** - CLI subcommand to test patterns against sample commands without running them
2. **Natural Language Explanations** - Explain WHY a command was blocked in plain English
3. **Command Rewriting Suggestions** - Suggest safer alternatives when blocking
4. **Automatic Allowlist Suggestions** - Learn from repeated blocks and suggest allowlist entries
5. **Context-Aware Allowlisting** - Allow commands only in specific directories or git branches

### Phase 3 Expansion (Next 5)

6. **Temporary/Expiring Allowlist Entries** - Time-limited exceptions
7. **Interactive Learning Mode** - Ask before blocking to learn preferences
8. **Git Branch Awareness** - Different rules for main vs feature branches
9. **Agent-Specific Profiles** - Different rules for different AI agents
10. **Graduated Response System** - Warn before blocking, block after N warnings

### Phase 5 Bead Creation

```bash
# Epic for top idea
br create "Epic: Pattern Testing Tool" -p 1 -t epic --body "
## Background
Users need to verify their patterns match what they expect without running real commands.
Currently, the only way to test is trial and error with actual dangerous commands.

## Goals
- Interactive pattern testing via CLI
- Show what a pattern would match
- Explain WHY a pattern matches or doesn't

## Success Criteria
- User can test any pattern against any command
- Output clearly shows match/no-match with explanation
"

# Subtasks
br create "Design CLI interface for 'dcg test'" -p 1 -t task
br create "Implement pattern-to-command matching logic" -p 2 -t task
br create "Add verbose output mode with match details" -p 2 -t task
br create "Unit tests for pattern testing" -p 2 -t task
br create "E2E tests for pattern testing CLI" -p 2 -t task

# Dependencies
br dep add bd-impl bd-design
br dep add bd-verbose bd-impl
br dep add bd-unit-tests bd-impl
br dep add bd-e2e-tests bd-impl
```

---

## Example 2: wezterm-automata

### Phase 6 Refinement (Pass 3)

**Issues Found:**
- Bead "Implement IPC layer" was too vague
- Missing test tasks for 3 features
- Cycle detected between "Config loader" and "State manager"

**Fixes Applied:**
```bash
# Break down vague bead
br update bd-ipc --body "
## Specific Implementation
1. Use Unix domain sockets for local IPC
2. JSON-RPC 2.0 protocol
3. Async message handling via tokio

## Interface
- send_command(cmd) -> Result<Response>
- subscribe_events(filter) -> Stream<Event>
"

# Add missing test tasks
br create "Unit tests for IPC layer" -p 2 -t task
br dep add bd-ipc-tests bd-ipc

# Fix cycle by introducing shared dependency
br dep remove bd-state bd-config
br create "Core types module" -p 1 -t task
br dep add bd-config bd-core-types
br dep add bd-state bd-core-types
```

---

## Anti-Pattern: What NOT To Do

### Bad: Vague Bead
```bash
# DON'T
br create "Improve performance" -p 2 -t task
```

### Good: Specific Bead
```bash
# DO
br create "Optimize pattern matching with Aho-Corasick" -p 2 -t task --body "
## Background
Current O(n*m) pattern matching is slow for 100+ patterns.

## Approach
1. Use aho-corasick crate for multi-pattern matching
2. Build automaton once at startup
3. Expected: O(n) matching regardless of pattern count

## Success Criteria
- 10x speedup for 100+ patterns
- No regression for <10 patterns
"
```
