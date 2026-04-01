# Nielsen's 10 Usability Heuristics - Deep Dive

Detailed explanations and examples for each heuristic.

---

## 1. Visibility of System Status

**Principle:** Keep users informed about what's happening through appropriate feedback within reasonable time.

### What to Look For
- Loading indicators for async operations
- Progress bars for long tasks
- Success/error confirmations
- Current state visible (logged in? which page? unsaved changes?)

### Good Examples
```
✓ Spinner + "Saving..." while form submits
✓ "3 of 10 files uploaded" with progress bar
✓ "Connected as john@example.com" in header
✓ Toast: "Changes saved" that auto-dismisses
```

### Bad Examples
```
✗ Form submit with no feedback (user clicks again)
✗ Background sync with no indicator
✗ No indication of unsaved work
✗ "Loading..." for 30 seconds with no progress
```

### CLI Application
```bash
# Good
Processing: [=====>    ] 50% (5/10 files)

# Bad
(no output for 30 seconds)
```

---

## 2. Match Between System and Real World

**Principle:** Use language, concepts, and conventions familiar to users.

### What to Look For
- Jargon-free labels
- Familiar metaphors (folder, trash, cart)
- Domain-appropriate terminology
- Logical ordering (alphabetical, chronological, priority)

### Good Examples
```
✓ "Shopping Cart" not "Purchase Queue"
✓ "Delete" not "Expunge Record"
✓ Calendar uses days/weeks, not "time units"
✓ Medical app uses "Blood Pressure" not "Arterial Pressure Reading"
```

### Bad Examples
```
✗ "Initiate Transaction" instead of "Buy"
✗ Technical IDs shown to users (UUID-4e5f-...)
✗ Error: "ECONNREFUSED" instead of "Can't connect to server"
✗ "Epoch timestamp" instead of "Created: Jan 15, 2024"
```

---

## 3. User Control and Freedom

**Principle:** Users make mistakes. Provide clear exits and undo.

### What to Look For
- Undo/redo available
- Cancel button on modals
- Back navigation works
- "Are you sure?" for destructive actions
- Easy logout/exit

### Good Examples
```
✓ Ctrl+Z undoes last action
✓ "Undo" toast after delete with timer
✓ Modal has X close button AND "Cancel"
✓ Browser back works correctly
```

### Bad Examples
```
✗ No way to cancel mid-operation
✗ Accidental delete is permanent
✗ Modal can only be closed by completing action
✗ Wizard with no back button
```

### CLI Application
```bash
# Good
$ rm important.txt
Delete important.txt? [y/N]: n
Aborted.

# Bad
$ rm important.txt
(file deleted, no confirmation, no undo)
```

---

## 4. Consistency and Standards

**Principle:** Follow platform conventions. Same action = same result.

### What to Look For
- Consistent navigation placement
- Standard icons (gear=settings, X=close)
- Same terminology throughout
- Keyboard shortcuts follow conventions

### Good Examples
```
✓ "Save" is always Ctrl+S
✓ Search is always in top-right
✓ Red means danger/delete everywhere
✓ Links are blue and underlined
```

### Bad Examples
```
✗ "Submit" on one page, "Send" on another
✗ Sometimes Enter submits, sometimes it doesn't
✗ Settings icon is gear on desktop, hamburger on mobile
✗ Different date formats on different pages
```

### CLI Application
```bash
# Good - follows conventions
-v, --verbose    # common pattern
-h, --help       # expected
-f, --force      # standard meaning

# Bad - breaks conventions
-q for help      # should be -h
--verbose/-V     # V is usually version
```

---

## 5. Error Prevention

**Principle:** Prevent errors before they happen.

### What to Look For
- Constraints that prevent invalid input
- Confirmation for destructive actions
- Clear affordances (disabled buttons, grayed options)
- Smart defaults

### Good Examples
```
✓ Date picker prevents invalid dates
✓ "Delete All" requires typing "DELETE" to confirm
✓ Disabled "Submit" until form is valid
✓ Auto-save prevents data loss
```

### Bad Examples
```
✗ Free text for dates (user types "13/45/2024")
✗ Delete button right next to Edit
✗ No validation until submit
✗ "Send to All" with one click
```

---

## 6. Recognition Rather Than Recall

**Principle:** Minimize memory load. Make options visible.

### What to Look For
- Recently used items visible
- Autocomplete/suggestions
- Clear labels on icons
- Context-sensitive help

### Good Examples
```
✓ Recent files list
✓ Command palette with search
✓ Tooltips on icon buttons
✓ "Did you mean...?" for typos
```

### Bad Examples
```
✗ Icon-only toolbar with no tooltips
✗ Must remember exact command syntax
✗ Hidden features in unlabeled menus
✗ "Enter code from email" (user must switch context)
```

### CLI Application
```bash
# Good
$ git
usage: git <command> [<args>]
Common commands: add, commit, push, pull, status...

# Bad
$ mytool
(no output, must consult docs)
```

---

## 7. Flexibility and Efficiency of Use

**Principle:** Accelerators for experts, simplicity for novices.

### What to Look For
- Keyboard shortcuts
- Command palette
- Customizable workflows
- Bulk operations
- Power user modes

### Good Examples
```
✓ Ctrl+K command palette
✓ Right-click context menus
✓ Batch select with Shift+Click
✓ Configurable hotkeys
```

### Bad Examples
```
✗ Only mouse-driven interface
✗ No bulk operations (edit one at a time)
✗ Experts must click through same wizard every time
✗ No way to save frequent workflows
```

---

## 8. Aesthetic and Minimalist Design

**Principle:** Remove the unnecessary. Every element should serve a purpose.

### What to Look For
- No redundant information
- Clean visual hierarchy
- Progressive disclosure
- Whitespace used effectively

### Good Examples
```
✓ "Advanced options" collapsed by default
✓ Dashboard shows key metrics, details on drill-down
✓ Error shows message, stack trace in expandable
✓ Mobile shows essential, desktop shows more
```

### Bad Examples
```
✗ Every field visible even if rarely used
✗ Wall of text with no hierarchy
✗ Five CTAs competing for attention
✗ Settings page with 50 options visible
```

### CLI Application
```bash
# Good (default clean, verbose optional)
$ br list
TKT-1  Fix login bug        open
TKT-2  Add dark mode        closed

$ br list --verbose
# Shows timestamps, assignees, etc.

# Bad (verbose by default)
$ br list
ID: TKT-1 | Title: Fix login bug | Status: open | Created: 2024-01-15T10:30:00Z | Updated: ...
```

---

## 9. Help Users Recognize, Diagnose, and Recover from Errors

**Principle:** Error messages should be human-readable and suggest solutions.

### What to Look For
- Plain language error messages
- Specific problem identification
- Suggested fixes
- No stack traces to end users

### Good Examples
```
✓ "Email address isn't valid. Example: name@example.com"
✓ "File too large (50MB). Maximum size is 10MB."
✓ "Can't connect to server. Check your internet connection."
✓ "Password must include a number" (specific, actionable)
```

### Bad Examples
```
✗ "Error 500"
✗ "Invalid input"
✗ "Something went wrong"
✗ Stack trace shown to user
✗ "Null pointer exception at line 234"
```

### CLI Application
```bash
# Good
$ br create
error: Missing required argument: title
usage: br create <title> [--description "..."]

# Bad
$ br create
Error: NoneType has no attribute 'title'
```

---

## 10. Help and Documentation

**Principle:** Provide help that is searchable, task-focused, and concise.

### What to Look For
- Contextual help (? icons, tooltips)
- Searchable documentation
- Task-oriented guides
- Keyboard shortcut reference

### Good Examples
```
✓ "?" icon next to complex fields
✓ Ctrl+? shows keyboard shortcuts
✓ Onboarding tour for new users
✓ "Learn more" links to relevant docs
```

### Bad Examples
```
✗ No documentation
✗ Docs exist but not searchable
✗ Help is PDF manual, not integrated
✗ "RTFM" attitude
```

### CLI Application
```bash
# Good
$ br --help
$ br create --help  # Subcommand-specific help
$ br help create    # Alternative syntax

# Bad
$ br
(no help, must find docs)
```

---

## Severity Ratings

When reporting issues, rate severity:

| Level | Meaning | Action |
|-------|---------|--------|
| **4 - Critical** | Prevents task completion | Must fix before launch |
| **3 - Major** | Significant difficulty | Fix soon |
| **2 - Minor** | Annoyance, workaround exists | Fix when possible |
| **1 - Cosmetic** | Polish issue | Nice to fix |
| **0 - Not a problem** | Audit found no issues | Document why |
