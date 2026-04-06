# Vision Extraction

## Where to Find the Vision

Projects document their vision across multiple locations. Check all of these:

### Primary Sources (authoritative)

1. **README.md** — The public-facing promise. Contains the "elevator pitch" goals.
2. **Plan documents** — Names vary:
   - `PLAN.md`, `PLAN_TO_CREATE_*.md`
   - `docs/DESIGN.md`, `docs/ARCHITECTURE.md`
   - `docs/SPEC.md`, `docs/SPECIFICATION.md`
   - `ROADMAP.md`

```bash
# Find all plan/spec docs
find . -maxdepth 3 -name "*.md" | xargs grep -li "goal\|vision\|objective\|purpose\|deliver" 2>/dev/null | head -20
ls docs/ 2>/dev/null
```

3. **Bead epics** — High-level groupings that reveal strategic goals:

```bash
br list --type=epic --json 2>/dev/null | jq -r '.[].title'
```

### Secondary Sources (context)

4. **AGENTS.md** — Workflow rules that hint at project priorities
5. **CHANGELOG.md** — What's been delivered so far
6. **GitHub repo description** — One-line vision statement
7. **Git commit messages** — What the project has been focused on recently

```bash
git log --oneline -30  # Recent trajectory
```

## Converting Vision to Testable Goals

The vision as written is usually a mix of:
- Concrete claims ("parses 10K lines/sec")
- Vague aspirations ("high performance")
- Feature lists ("supports ES2024")
- Comparative claims ("faster than V8")

Convert ALL of these into **concrete, testable goals**:

| Vision Text | Testable Goal |
|-------------|---------------|
| "High performance" | Parses N lines/sec (benchmark against stated targets or competitors) |
| "Supports ES2024" | Passes X% of test262 ES2024 tests |
| "Easy to use" | Has CLI with documented flags, returns 0 on success, useful error messages |
| "Production ready" | Has CI, test suite, no panics on malformed input, graceful error handling |
| "Better than X" | Outperforms X on benchmark Y by stated margin |
| "Complete implementation" | All methods from spec have non-stub implementations with tests |

### For Projects Without Explicit Metrics

When the README doesn't state specific targets, infer reasonable ones:
- **Performance:** "Should be competitive with similar tools" → benchmark against 2-3 alternatives
- **Correctness:** "Should handle all standard cases" → find or create a conformance test suite
- **Robustness:** "Should be reliable" → no panics on fuzz input, graceful error on bad input

## Handling Evolving Visions

Large projects often have vision documents that were written early and haven't been updated. The beads may have diverged from the original plan. When this happens:

1. **Treat the code + beads as the actual vision** (they reflect what's actually being built)
2. **But flag the divergence** — "README promises X, but beads suggest the project pivoted to Y"
3. **Ask the user** if the original vision or the evolved direction is correct

## Output: The Vision Checklist

```markdown
## Vision Checklist: [Project Name]

### Source Documents
- README.md (last updated: [date from git])
- [Other plan docs found]

### Goals (extracted and testable)

| # | Goal | Source | Testable Criterion | Priority |
|---|------|--------|-------------------|----------|
| 1 | [Goal] | README L42 | [How to verify] | Core |
| 2 | [Goal] | PLAN.md sec3 | [How to verify] | Core |
| 3 | [Goal] | README L88 | [How to verify] | Important |
| 4 | [Goal] | docs/DESIGN.md | [How to verify] | Nice-to-have |

### Priority Key
- **Core:** Project has no value without this
- **Important:** Significantly degrades value if missing
- **Nice-to-have:** Polish, completeness, competitive edge
```
