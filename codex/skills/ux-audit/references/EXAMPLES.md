# UX Audit Examples

Real before/after examples from UX audits.

---

## Example 1: CLI Tool Audit (br - Beads Rust)

### Executive Summary

**br** is a local-first issue tracker CLI. Overall Score: **8/10**

**Critical Issues:** 0
**Important Issues:** 2
**Suggestions:** 5

---

### Heuristic Scores

| Heuristic | Score | Notes |
|-----------|-------|-------|
| 1. Visibility | 9/10 | Good progress indicators, clear status |
| 2. Real World | 8/10 | Familiar CLI conventions |
| 3. Control | 7/10 | Missing --dry-run on some commands |
| 4. Consistency | 9/10 | Standard flag patterns |
| 5. Error Prevention | 8/10 | Confirmation on destructive ops |
| 6. Recognition | 9/10 | Excellent --help at all levels |
| 7. Flexibility | 8/10 | Short and long flags, --robot mode |
| 8. Minimal | 9/10 | Clean default output |
| 9. Error Help | 7/10 | Some errors lack suggested fixes |
| 10. Documentation | 8/10 | Good --help, could use examples |

---

### Important Issues

#### 1. Missing --dry-run for Destructive Operations

**Heuristic:** #3 - User Control & Freedom
**Location:** `src/commands/close.rs`, `src/commands/delete.rs`
**Problem:** `br close --all` and `br delete` execute immediately
**Impact:** Users can't preview what will happen
**Fix:**
```rust
// Add --dry-run flag
#[arg(long, help = "Preview without executing")]
dry_run: bool,
```

#### 2. Generic Error Messages

**Heuristic:** #9 - Help Users with Errors
**Location:** `src/storage.rs:150`
**Problem:** "Database error" without specifics
**Impact:** Users don't know how to recover
**Fix:**
```rust
// Before
Err(anyhow!("Database error"))

// After
Err(anyhow!("Cannot write to database: {}. Check if {} is writable.", e, db_path))
```

---

### Suggestions

1. Add `--examples` flag to show usage examples in help
2. Add shell completion generation for zsh/bash/fish
3. Color-code status in table output (with --no-color option)
4. Add `br doctor` command to diagnose common issues
5. Show "Did you mean...?" for typo'd commands

---

## Example 2: Web Form Audit

### Before Audit

```html
<form>
  <input type="text" placeholder="Name">
  <input type="text" placeholder="Email">
  <input type="text" placeholder="Phone">
  <div onclick="submit()" style="background: green">SUBMIT</div>
</form>
```

### Issues Found

| Issue | Heuristic | Severity |
|-------|-----------|----------|
| No labels (placeholder only) | #6 Recognition | Critical |
| Email not validated | #5 Error Prevention | Important |
| Phone no format hint | #2 Real World | Important |
| Div instead of button | A11Y | Critical |
| No error states | #9 Error Help | Critical |
| No loading state | #1 Visibility | Important |

### After Audit

```html
<form>
  <div class="field">
    <label for="name">Full Name *</label>
    <input type="text" id="name" required aria-required="true">
    <span class="error" role="alert" hidden>Name is required</span>
  </div>

  <div class="field">
    <label for="email">Email Address *</label>
    <input type="email" id="email" required aria-required="true"
           aria-describedby="email-hint">
    <span id="email-hint" class="hint">We'll never share your email</span>
    <span class="error" role="alert" hidden>Please enter a valid email</span>
  </div>

  <div class="field">
    <label for="phone">Phone Number</label>
    <input type="tel" id="phone" placeholder="(555) 123-4567"
           pattern="[\d\s\-\(\)]+">
    <span class="hint">Format: (555) 123-4567</span>
  </div>

  <button type="submit" class="btn-primary" aria-busy="false">
    <span class="btn-text">Submit</span>
    <span class="btn-loading" hidden>Submitting...</span>
  </button>
</form>
```

---

## Example 3: Quick Scan Report

When you need a fast assessment (~10 min):

```markdown
# Quick UX Scan: [App Name]

## Traffic Light Assessment

| Area | Status | Notes |
|------|--------|-------|
| Navigation | 🟢 | Clear, consistent |
| Forms | 🟡 | Missing validation |
| Errors | 🔴 | Generic messages |
| A11Y | 🟡 | Keyboard mostly works |
| Mobile | 🟢 | Responsive |

## Top 3 Issues

1. **Error messages unhelpful** - "Error occurred" without context
2. **No loading states** - Forms submit with no feedback
3. **Low contrast on disabled buttons** - 2.5:1 ratio

## Quick Wins

- [ ] Add aria-busy to submit buttons
- [ ] Show specific validation errors
- [ ] Increase disabled button contrast

## Recommendation

Address error handling before launch. Other issues can wait.
```

---

## Audit Report Template

Copy this for full audits:

```markdown
# UX Audit Report: [Project Name]

## Executive Summary
[1-2 sentences on overall usability]

**Overall Score:** X/10
**Critical Issues:** N
**Important Issues:** N
**Suggestions:** N

---

## Critical Issues (Must Fix)

### 1. [Issue Title]
**Heuristic:** #N - [Name]
**Location:** `file:line` or screen/flow
**Problem:** [What's wrong]
**Impact:** [How it affects users]
**Fix:** [Specific solution with code/design]

---

## Important Issues (Should Fix)

### 1. [Issue Title]
**Heuristic:** #N - [Name]
**Location:** [Where]
**Problem:** [What]
**Fix:** [How]

---

## Suggestions (Nice to Have)

- [ ] [Suggestion 1]
- [ ] [Suggestion 2]

---

## Heuristic Scores

| Heuristic | Score | Notes |
|-----------|-------|-------|
| 1. Visibility | X/10 | |
| 2. Real World | X/10 | |
| 3. Control | X/10 | |
| 4. Consistency | X/10 | |
| 5. Error Prevention | X/10 | |
| 6. Recognition | X/10 | |
| 7. Flexibility | X/10 | |
| 8. Minimal Design | X/10 | |
| 9. Error Help | X/10 | |
| 10. Documentation | X/10 | |

---

## Accessibility Check

- [ ] Keyboard navigation: PASS/FAIL
- [ ] Color contrast: PASS/FAIL
- [ ] Screen reader: PASS/FAIL/N/A

---

## Recommendations (Priority Order)

1. [Highest impact fix]
2. [Second priority]
3. [Third priority]

---

*Audited: [Date]*
*By: [Agent/Human]*
```
