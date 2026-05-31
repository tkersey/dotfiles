# Integration Notes

## Implicit invocation posture
`logophile` is allowed to trigger implicitly for human-facing language surfaces. It is not allowed to rewrite operational decisions or machine-consumed artifacts.

## AGENTS.md interaction
`AGENTS.md` owns repo-level response wrappers such as `Echo:`. `logophile` owns the generated artifact text. Keep wrappers outside artifacts.

## Trigger boundary
Good implicit trigger: the requested output is wording, naming, doctrine, PR copy, commit/PR text, docs, user-facing explanation, or final human-readable language.

Bad implicit trigger: ordinary coding, code review, verification, planning, or tool execution where no wording/naming/doctrine output is requested.
