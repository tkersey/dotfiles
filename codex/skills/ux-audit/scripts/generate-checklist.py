#!/usr/bin/env python3
"""Generate a UX audit checklist customized for project type.

Usage:
    ./generate-checklist.py web     # Web application checklist
    ./generate-checklist.py cli     # CLI tool checklist
    ./generate-checklist.py mobile  # Mobile app checklist
    ./generate-checklist.py api     # API/developer experience

Outputs markdown checklist to stdout.
"""

import sys
from textwrap import dedent

CHECKLISTS = {
    "web": dedent("""
        # UX Audit Checklist: Web Application

        ## Visibility of System Status
        - [ ] Loading indicators on async operations
        - [ ] Progress bars for multi-step processes
        - [ ] Success/error feedback on actions
        - [ ] Current page/section clearly indicated
        - [ ] Unsaved changes indicator

        ## Match with Real World
        - [ ] Language matches user's domain
        - [ ] No unexplained jargon or codes
        - [ ] Dates/numbers in local format
        - [ ] Icons are universally understood

        ## User Control & Freedom
        - [ ] Undo available for destructive actions
        - [ ] Cancel button on all modals
        - [ ] Browser back works correctly
        - [ ] Easy logout/exit path
        - [ ] Can close modals with Escape

        ## Consistency & Standards
        - [ ] Navigation in same place on all pages
        - [ ] Same terminology throughout
        - [ ] Standard icons (gear=settings, X=close)
        - [ ] Form validation consistent

        ## Error Prevention
        - [ ] Confirmation for destructive actions
        - [ ] Input constraints prevent invalid data
        - [ ] Disabled states for unavailable actions
        - [ ] Autosave or draft saving

        ## Recognition over Recall
        - [ ] Recently used items visible
        - [ ] Autocomplete on search/forms
        - [ ] Tooltips on icon-only buttons
        - [ ] Breadcrumbs for deep navigation

        ## Flexibility & Efficiency
        - [ ] Keyboard shortcuts for common actions
        - [ ] Search/filter capabilities
        - [ ] Bulk operations available
        - [ ] Customizable dashboard/views

        ## Aesthetic & Minimal Design
        - [ ] Clear visual hierarchy
        - [ ] No redundant information
        - [ ] Progressive disclosure (advanced options hidden)
        - [ ] Adequate whitespace

        ## Help Users with Errors
        - [ ] Errors in plain language
        - [ ] Errors suggest specific fixes
        - [ ] No stack traces to users
        - [ ] Inline validation feedback

        ## Help & Documentation
        - [ ] Contextual help available
        - [ ] Searchable documentation
        - [ ] Keyboard shortcuts reference
        - [ ] Onboarding for new users

        ## Accessibility (A11Y)
        - [ ] Keyboard navigation works
        - [ ] Color contrast meets WCAG AA (4.5:1)
        - [ ] Not color-only indicators
        - [ ] Form inputs have labels
        - [ ] Images have alt text
        - [ ] Focus indicator visible
    """).strip(),

    "cli": dedent("""
        # UX Audit Checklist: CLI Tool

        ## Visibility of System Status
        - [ ] Progress bars for long operations
        - [ ] Spinners for async work
        - [ ] Verbose mode available (-v)
        - [ ] Clear success/failure messages
        - [ ] Exit codes are meaningful

        ## Match with Real World
        - [ ] --help uses familiar language
        - [ ] Standard flag conventions (-v, -h, -f)
        - [ ] Output format matches domain norms
        - [ ] Timestamps in readable format

        ## User Control & Freedom
        - [ ] Ctrl+C works to cancel
        - [ ] --dry-run for preview
        - [ ] Confirmation before destructive ops
        - [ ] --force to bypass confirmations
        - [ ] Undo or recovery possible

        ## Consistency & Standards
        - [ ] Short (-v) and long (--verbose) flags
        - [ ] Consistent subcommand structure
        - [ ] Standard exit codes (0=success)
        - [ ] Errors to stderr, output to stdout

        ## Error Prevention
        - [ ] Input validation before processing
        - [ ] Sanity checks on dangerous operations
        - [ ] Clear prompts with defaults shown
        - [ ] Type confirmation for irreversible actions

        ## Recognition over Recall
        - [ ] --help at every subcommand level
        - [ ] Tab completion available
        - [ ] Example usage in help
        - [ ] Suggest similar commands on typos

        ## Flexibility & Efficiency
        - [ ] Config file support
        - [ ] Environment variables for settings
        - [ ] Piping support (stdin/stdout)
        - [ ] --robot/--json for scripting
        - [ ] Quiet mode (-q)

        ## Aesthetic & Minimal Design
        - [ ] Clean default output
        - [ ] Verbose details optional
        - [ ] Consistent table/list formatting
        - [ ] Color optional (--no-color)

        ## Help Users with Errors
        - [ ] Specific error messages
        - [ ] Suggested fixes in errors
        - [ ] No stack traces (unless --debug)
        - [ ] "Did you mean...?" for typos

        ## Help & Documentation
        - [ ] Comprehensive --help
        - [ ] Man page available
        - [ ] Usage examples included
        - [ ] Common workflows documented

        ## Accessibility
        - [ ] Works without color
        - [ ] Screen reader parseable output
        - [ ] No ASCII art required for function
        - [ ] Configurable output width
    """).strip(),

    "mobile": dedent("""
        # UX Audit Checklist: Mobile App

        ## Visibility of System Status
        - [ ] Loading states clear
        - [ ] Pull-to-refresh feedback
        - [ ] Sync status visible
        - [ ] Network state indicated
        - [ ] Progress for uploads/downloads

        ## Match with Real World
        - [ ] Native platform conventions
        - [ ] Gestures match platform norms
        - [ ] Local date/number formats
        - [ ] Appropriate icons

        ## User Control & Freedom
        - [ ] Swipe to go back works
        - [ ] Undo for destructive actions
        - [ ] Easy to close/dismiss
        - [ ] Cancel mid-operation

        ## Consistency & Standards
        - [ ] Platform design guidelines followed
        - [ ] Tab bar consistent
        - [ ] Navigation patterns standard
        - [ ] Same gestures throughout

        ## Error Prevention
        - [ ] Confirmation for deletes
        - [ ] Form validation inline
        - [ ] Disabled states clear
        - [ ] Smart defaults

        ## Recognition over Recall
        - [ ] Recent items accessible
        - [ ] Search with suggestions
        - [ ] Labels on bottom nav
        - [ ] Onboarding for features

        ## Flexibility & Efficiency
        - [ ] Quick actions available
        - [ ] Shortcuts for power users
        - [ ] Bulk selection mode
        - [ ] Customizable home screen

        ## Aesthetic & Minimal Design
        - [ ] Touch targets 44pt minimum
        - [ ] Clear visual hierarchy
        - [ ] No clutter
        - [ ] Appropriate for screen size

        ## Help Users with Errors
        - [ ] Clear error messages
        - [ ] Retry options
        - [ ] Graceful offline handling
        - [ ] Helpful empty states

        ## Accessibility
        - [ ] VoiceOver/TalkBack works
        - [ ] Dynamic type supported
        - [ ] Color contrast sufficient
        - [ ] Reduce motion respected
    """).strip(),

    "api": dedent("""
        # UX Audit Checklist: API / Developer Experience

        ## Visibility of System Status
        - [ ] Request IDs in responses
        - [ ] Rate limit info in headers
        - [ ] Deprecation warnings
        - [ ] Status endpoint available

        ## Match with Real World
        - [ ] RESTful conventions OR clear docs
        - [ ] Standard HTTP status codes
        - [ ] ISO date formats
        - [ ] Consistent naming conventions

        ## User Control & Freedom
        - [ ] Idempotent operations where possible
        - [ ] Pagination with offset/cursor
        - [ ] Filtering/sorting options
        - [ ] Partial updates (PATCH)

        ## Consistency & Standards
        - [ ] Consistent response format
        - [ ] Consistent error format
        - [ ] Versioning strategy clear
        - [ ] Authentication consistent

        ## Error Prevention
        - [ ] Input validation with clear rules
        - [ ] Type checking/schemas
        - [ ] Sandbox environment available
        - [ ] Dry-run options for mutations

        ## Recognition over Recall
        - [ ] OpenAPI/Swagger spec
        - [ ] Interactive docs (try it)
        - [ ] Code examples in multiple languages
        - [ ] Postman/Insomnia collections

        ## Flexibility & Efficiency
        - [ ] Sparse fieldsets (fields param)
        - [ ] Batch operations
        - [ ] Webhooks for events
        - [ ] GraphQL or similar for flexibility

        ## Aesthetic & Minimal Design
        - [ ] Minimal required fields
        - [ ] Sane defaults
        - [ ] Progressive complexity
        - [ ] Clean response structure

        ## Help Users with Errors
        - [ ] Structured error responses
        - [ ] Error codes documented
        - [ ] Suggested fixes in errors
        - [ ] Validation errors itemized

        ## Documentation
        - [ ] Quick start guide
        - [ ] Authentication docs clear
        - [ ] All endpoints documented
        - [ ] Changelog maintained
    """).strip(),
}


def main():
    if len(sys.argv) < 2:
        print("Usage: generate-checklist.py <type>")
        print(f"Types: {', '.join(CHECKLISTS.keys())}")
        sys.exit(1)

    project_type = sys.argv[1].lower()

    if project_type not in CHECKLISTS:
        print(f"Unknown type: {project_type}")
        print(f"Available: {', '.join(CHECKLISTS.keys())}")
        sys.exit(1)

    print(CHECKLISTS[project_type])


if __name__ == "__main__":
    main()
