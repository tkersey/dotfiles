# $opt Routing Matrix

## Fast routing

| User intent | $opt mode | Companion | Edit default |
| --- | --- | --- | --- |
| "Is this skill well shaped?" | audit | skill-optimizer | no_edit |
| "Optimize this skill" | propose | skill-optimizer, maybe $tune | no_edit |
| "Tune from this session" | tune or shadow-diagnose | $shadow, $tune | no_edit |
| "Fix the skill now" | patch | skill-optimizer, maybe $refine | edit_allowed after gate |
| "Validate this skill edit" | validate | opt-sanity, target checks | no_edit |
| "Prevent that failure again" | regression | $tune + skill-optimizer | no_edit unless explicit |
| "Keep working until the skill is improved" | goal-loop | $cas + skill-optimizer | depends on explicit apply gate |

## Evidence routing

- Current user feedback: use current-turn evidence first; do not claim recurrence.
- Watched session id/path: use `$shadow` on exactly that session, then pass the report to `skill-optimizer`.
- Historical sessions: use `$tune` and its evidence-source model, usually via `$seq` when appropriate.
- Worktree diffs: inspect target skill files and validation output.
- Supplied brief: treat it as provided evidence and state what it cannot prove.

## Apply routing

The words below do not imply edit permission by themselves:

- optimize
- improve
- tune
- harden
- audit
- review
- diagnose
- make better

The words below usually imply possible edit permission if a target skill is identified:

- edit
- patch
- apply
- update the file
- change SKILL.md
- make the change
- implement the fix

Protected or self-targeted skill edits still require an apply gate and validation surface.
