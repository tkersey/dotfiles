<proposed_plan>
## Summary
Make parse_seconds reject negative durations without changing valid nonnegative
integer inputs. First add the negative-input regression. Done means the focused
and repository suites pass with no unrelated behavior or dependency changes.

## Governed Specification
This is an illustrative repository, not an inspected real checkout. Its existing
src/durations.py::parse_seconds(text: str) calls int(text, 10) and returns the result;
negative values currently escape. The user requires ValueError for values below
zero, while preserving every currently accepted nonnegative value and existing
int parsing errors. Zero, surrounding whitespace, and an optional plus sign remain
valid. Do not redesign parsing, change public signatures, or add dependencies.

## Architecture Decisions
Use the existing parse_seconds owner and representation. The selected means is a
post-parse negative check, not a source-fixed mechanism. A different implementation
is allowed only if it preserves the complete accepted int parsing behavior and the
required negative rejection. No new abstraction or cross-module owner is needed.

## Implementation Sequence
A-TEST (implementation owner): In tests/test_durations.py, add tests that -1 and -99
raise ValueError and that 0, +3, and whitespace-padded 5 retain results 0, 3, and 5.
Run `python -m unittest tests.test_durations`; the negative tests must expose the
current bug before implementation. If the assumed API differs, stop and revise the
source binding rather than guessing a new signature.

A-FIX (implementation owner; depends on A-TEST): In src/durations.py::parse_seconds,
retain int(text, 10), reject a parsed value below zero with ValueError, then return
the value. Preserve existing conversion exceptions. Do not change callers. Run the
focused command; unexpected behavior reopens this action, not the requirement.

A-PROVE (implementation owner; depends on A-FIX): Run `python -m unittest discover`
on the final tree. Inspect all parse_seconds imports/callers for bypass assumptions
and confirm there is no newly duplicated parser or dependency. If proof fails,
repair within this scope or report the specific obstruction; do not claim done.

## Proof, Rollback, and Done-State
The invalid family is negative values accepted by this owner. The valid domain is
every nonnegative input accepted by the existing int conversion. Retaining that
conversion preserves its lexical semantics; the new postcondition excludes all
negative parsed integers. The tests discriminate negative rejection from merely
special-casing -1, but are not alone a universal proof of parsing behavior.
The call-site inspection derives its domain from repository imports, not a list
supplied by the implementation. Done requires the focused and complete suites on
the final tree, required-valid preservation, and no scope expansion. On abort,
revert only these session-owned source/test edits, preserve concurrent changes,
and rerun the original suite to establish restoration.

## Plan Identity and Source
plan_id: PLAN-duration-negative
revision: 1
Target: illustrative durations repository; branch feature/duration-negative.
Source: the required behavior stated in this block. No real commit or test execution
is claimed. Confirm the described API and commands against the actual checkout
before changes; a mismatch invalidates only the affected derivation.
Persistence: transient; no EPG or Ledger required. Mutation needs separate authority.
</proposed_plan>
