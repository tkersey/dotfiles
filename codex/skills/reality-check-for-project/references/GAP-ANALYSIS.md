# Gap Analysis Methodology

## The Core Question

For each goal in the Vision Checklist: **What is the gap between what the docs promise and what the code actually delivers?**

## Step-by-Step Process

### 1. Build the Vision Checklist

Extract every concrete, testable goal from:
- `README.md` — what the project claims to do
- Plan/spec documents — the detailed breakdown of features
- `docs/` folder — design documents, architecture notes
- Bead epics — high-level goals that beads are grouped under

Each goal must be **concrete and testable**. Convert vague statements:

```
BAD:  "High performance" → not testable
GOOD: "Parses 10K lines/sec on commodity hardware" → testable
GOOD: "Handles all ES2024 syntax" → testable against test262 suite
```

### 2. Map Goals to Code

For each vision goal, find the implementing code:

```bash
# Find relevant source files
rg -l "function_name\|ClassName\|module_name" --type rust --type ts --type py .

# Check test coverage for that area
rg -l "test.*function_name\|function_name.*test" --type rust --type ts .

# Check if it's a stub (leverage mock-code-finder patterns)
ast-grep run -l Rust -p 'fn $NAME($$$) { todo!() }' --json 2>/dev/null
```

### 3. Categorize Each Gap

| Status | Definition | Evidence Required |
|--------|-----------|-------------------|
| `WORKING` | Code exists, tests pass, e2e verified | Test output, demo run |
| `PARTIAL` | Some features work, others missing | List what works vs what doesn't |
| `STUB` | Placeholder/mock/todo only | Code snippet showing the stub |
| `UNPROVEN` | Code exists, no/insufficient tests | Show missing test coverage |
| `NOT_STARTED` | Zero code for this goal | grep showing no relevant code |
| `REGRESSED` | Was working, now broken | Failing test output or git bisect |
| `NO_BEAD` | Vision goal not tracked by any bead | Cross-reference with `br list` |
| `WRONG_APPROACH` | Implemented but architecturally flawed | Explain the design issue |

### 4. Severity Classification

**Critical gaps** (vision is undeliverable without these):
- Core value proposition not implemented
- Fundamental architecture prevents goal achievement
- Key integration missing entirely

**Major gaps** (vision is significantly degraded):
- Feature exists but can't handle real-world input
- Performance far below stated targets
- No end-to-end test proving the happy path works

**Minor gaps** (polish/completeness):
- Edge cases not handled
- Error messages could be better
- Documentation promises features that work but aren't well-tested

### 5. The Bead Coverage Cross-Check

This is the most dangerous gap type: goals the vision promises that have NO bead tracking them at all.

```bash
# Get all open bead titles and descriptions
br list --status=open --json 2>/dev/null | jq -r '.[].title' > /tmp/bead_titles.txt

# For each vision goal, search for relevant beads
# If no bead mentions goal X, it's a NO_BEAD gap
grep -i "goal_keyword" /tmp/bead_titles.txt || echo "NO BEAD COVERAGE!"
```

**Why this matters:** If all open beads were completed, these goals would STILL not be delivered. This is the gap between "bead completion percentage" and "vision delivery percentage."

## Output Format

### Summary Table

```markdown
## Reality Check Summary: [Project Name]

**Date:** YYYY-MM-DD
**Beads:** X open / Y closed / Z in-progress (N% complete)
**Vision delivery:** M of N goals fully working (P%)

### Vision Goal Status

| # | Goal | Status | Severity | Bead Coverage | Evidence |
|---|------|--------|----------|---------------|----------|
| 1 | [Goal from vision] | WORKING | - | beads-42,43 | Tests pass, demo verified |
| 2 | [Goal from vision] | PARTIAL | Major | beads-55 | 3/7 sub-features work |
| 3 | [Goal from vision] | NOT_STARTED | Critical | NO BEAD | No code found |
| 4 | [Goal from vision] | UNPROVEN | Major | beads-60 | Code exists, 0 tests |
| 5 | [Goal from vision] | STUB | Critical | beads-71 | `todo!()` at src/foo.rs:42 |
```

### Detailed Gap Report (one per gap)

```markdown
### Gap #3: [Goal Name] — NOT_STARTED (Critical)

**Vision promise:** "[Exact quote from README/plan doc]"
**Source:** README.md L42-45

**Current reality:** No code exists for this goal. Searched for:
- `rg -l "keyword" .` → 0 results
- No relevant bead found in `br list --status=open`

**Why it matters:** This is part of the core value proposition. Without it,
the project cannot [specific consequence].

**What's needed:**
- [Specific implementation requirement]
- [Specific test requirement]
- [Dependencies on other gaps]

**Bead coverage:** NONE — must create new beads for this goal.
```

## Common Failure Modes

| Failure | How to Detect | Example |
|---------|---------------|---------|
| **Optimism bias** | Agent reports PARTIAL when it's really STUB | Check: does it produce correct output for ANY real input? |
| **Test theater** | Tests pass but don't test real behavior | Check: are tests trivial? Do they use real data? |
| **Bead completion illusion** | 72% beads done but 0% of vision delivered | Cross-check: which vision goals have ALL their beads closed? |
| **Architecture gravity** | Code exists but architecture prevents the goal | Ask: can this design EVER achieve the stated performance? |
| **Scope creep masking** | New beads added faster than old ones close | Check: are NEW goals being tracked that weren't in original vision? |

## Integration with bv

```bash
# Check overall project health
bv --robot-triage | jq '.project_health'

# Find critical-path beads (blocking the most downstream work)
bv --robot-triage | jq '.blockers_to_clear'

# Check for cycles that prevent progress
bv --robot-insights | jq '.Cycles'

# Forecast completion
bv --robot-forecast all | jq '.forecast.summary'
```
