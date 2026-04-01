---
name: ux-audit
description: >-
  Systematic UX evaluation using Nielsen heuristics and accessibility checks.
  Use when reviewing UI, "is this usable", improving user experience, or pre-launch.
---

<!-- TOC: Core | Prompt | Quick Check | Heuristics | CLI | Output | Anti-Patterns | References -->

# UX Audit

> **Core Insight:** Users don't read manuals. If it's not obvious, it's broken.

## THE EXACT PROMPT

```
Conduct a UX audit of this [application/CLI/interface]:

1. Nielsen's 10 Usability Heuristics
2. Accessibility basics (keyboard, contrast, screen reader)
3. User flow analysis (happy path + error paths)
4. Cognitive load assessment

Produce prioritized report:
- Critical (blocking)
- Important (degraded experience)
- Suggestions (polish)

Include file:line references and concrete fixes.
```

---

## Quick Check (5 min)

```markdown
| Area | Status | Notes |
|------|--------|-------|
| Navigation | 🟢/🟡/🔴 | |
| Forms | 🟢/🟡/🔴 | |
| Errors | 🟢/🟡/🔴 | |
| Accessibility | 🟢/🟡/🔴 | |
| Mobile/Responsive | 🟢/🟡/🔴 | |
```

---

## Nielsen's 10 Heuristics (Quick Reference)

| # | Heuristic | Key Question |
|---|-----------|--------------|
| 1 | **Visibility** | Does user know what's happening? |
| 2 | **Real World** | Familiar language & concepts? |
| 3 | **Control** | Can user undo/escape? |
| 4 | **Consistency** | Same action = same result? |
| 5 | **Error Prevention** | Prevents mistakes before they happen? |
| 6 | **Recognition** | Options visible vs. memorized? |
| 7 | **Flexibility** | Shortcuts for experts? |
| 8 | **Minimal** | Visual clutter removed? |
| 9 | **Error Help** | Error messages helpful? |
| 10 | **Documentation** | Help available when needed? |

Deep dive: [HEURISTICS.md](references/HEURISTICS.md)

---

## CLI-Specific Heuristics

| Heuristic | CLI Application |
|-----------|-----------------|
| Visibility | `--verbose`, progress bars, spinners |
| Real world | Standard flags (`--help`, `--version`) |
| Control | Ctrl+C works, `--dry-run` available |
| Consistency | `-v` short, `--verbose` long |
| Error prevention | Confirmation prompts, `--force` |
| Recognition | `--help` shows all options |
| Flexibility | Short + long flags, piping |
| Minimal | Clean default, verbose optional |
| Error help | Actionable messages, suggested fixes |
| Documentation | `--help`, man pages, examples |

Generate checklist: `./scripts/generate-checklist.py cli`

---

## Accessibility Quick Check

### The Big 4
- [ ] **Keyboard:** All interactive elements reachable via Tab?
- [ ] **Contrast:** Text 4.5:1 ratio minimum?
- [ ] **Not color-only:** Icons/patterns, not just color?
- [ ] **Screen reader:** Labels, alt text, ARIA?

Deep dive: [A11Y.md](references/A11Y.md)

---

## Output Template

```markdown
# UX Audit: [Project]

## Summary
**Score:** X/10 | **Critical:** N | **Important:** N | **Suggestions:** N

## Critical Issues (Must Fix)
### 1. [Title]
**Heuristic:** #N - [Name]
**Location:** `file:line`
**Problem:** [What's wrong]
**Fix:** [Specific solution]

## Important Issues (Should Fix)
[Same format]

## Suggestions
- [ ] [Item]

## Heuristic Scores
| Heuristic | Score |
|-----------|-------|
| 1. Visibility | X/10 |
...
```

Full template: [EXAMPLES.md](references/EXAMPLES.md)

---

## Audit Depth

| Type | Time | When |
|------|------|------|
| **Quick Scan** | 5-10 min | PR review, spot check |
| **Standard** | 30-60 min | Pre-release, feature review |
| **Deep Audit** | 2+ hr | Major redesign, compliance |

---

## Anti-Patterns

| Don't | Do |
|-------|-----|
| "It's intuitive" | Test with fresh eyes |
| Ignore error paths | Audit happy AND error flows |
| Skip accessibility | Check the Big 4 minimum |
| Vague issues | Specific `file:line` + fix |
| All issues equal | Prioritize by impact |

---

## Integration

### With Hooks

Auto-run a11y check after UI edits:

```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Edit",
      "hooks": [{
        "type": "command",
        "command": "if echo \"$TOOL_INPUT_PATH\" | grep -qE '\\.(tsx|jsx|html)$'; then npx axe \"$TOOL_INPUT_PATH\" 2>/dev/null || true; fi"
      }]
    }]
  }
}
```

### With Other Skills

| Combine with... | For... |
|-----------------|--------|
| multi-model-triangulation | Multiple UX perspectives |
| multi-pass-bug-hunting | Include UX issues in sweeps |
| ui-polish | After fixing critical UX issues |

---

## References

| Topic | File |
|-------|------|
| Full heuristic details | [HEURISTICS.md](references/HEURISTICS.md) |
| Accessibility deep dive | [A11Y.md](references/A11Y.md) |
| Example audits | [EXAMPLES.md](references/EXAMPLES.md) |

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/generate-checklist.py` | Generate project-specific checklist |

```bash
./scripts/generate-checklist.py web    # Web app
./scripts/generate-checklist.py cli    # CLI tool
./scripts/generate-checklist.py mobile # Mobile app
./scripts/generate-checklist.py api    # API/DX
```
