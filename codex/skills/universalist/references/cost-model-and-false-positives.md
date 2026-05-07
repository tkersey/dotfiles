# Cost model and false positives

A universal construction is useful only when its maintenance cost is lower than the repeated obligation it eliminates.

## Cost dimensions

| Cost | What to inspect |
|---|---|
| Edit cost | How many files change for one new case or rule? |
| Lookup cost | How many files must an agent read before understanding the behavior? |
| Boundary cost | Does the new model require adapters at API, JSON, DB, queue, or external client surfaces? |
| Runtime cost | Is the invariant compile-time, parse-time, or runtime-only? |
| Test cost | What proof must be added or updated? |
| Concept cost | Does the repo/team language support the construction idiomatically? |
| Reduction opportunity | Which old checks, flags, adapters, or wrappers become deletable after the lift? |

## Positive signals

Climbing is likely worthwhile when:

- the same check appears in multiple layers;
- invalid states are currently representable and already guarded against;
- branch expansion is accelerating;
- one missing case could cause data loss, security issues, billing errors, or public contract drift;
- a small constructor/decoder seam can isolate the stronger shape;
- proof is fast and local.

## False positives

| Looks like | But may only need | Check before lifting |
|---|---|---|
| repeated validation | a shared helper | Is the predicate stable and domain-significant? |
| booleans/status fields | clearer names | Are impossible combinations actually possible? |
| branchy policy | a lookup table | Are behaviors independent and supplied from outside? |
| syntax + execution | one direct function | Are there multiple interpreters: eval, explain, render, log, persist? |
| agreement check | local assertion | Is agreement checked in several places or across trust boundaries? |
| local UI flow | reducer/state machine | Are invalid transitions common or consequential? |

## Reduction preflight summary

Before a lift, answer:

```md
What tax does this construction add?
What repeated obligation does it delete?
Could a lower primitive solve this?
Does it improve agent-editability?
What proof signal detects a wrong lift?
```

If the answers are weak, do not universalize. Use `reduce`, hold, or split.
