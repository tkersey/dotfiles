# Probe Cases

Use these probes to test substitution quality, output shape, and implicit trigger behavior.

## Rewrite should trigger
Prompt: `Tighten this paragraph without changing meaning.`
Checks:
- preserves meaning and obligations
- sharpens wording before deleting text
- keeps code, identifiers, paths, URLs, and numbers intact

## Human-facing copy should trigger implicitly
Prompt: `Write a concise PR reply explaining that we accepted comments 2 and 4 but rejected 5.`
Checks:
- uses paste-ready human-facing language
- preserves the adjudication result
- does not invent technical evidence

## Naming should trigger
Prompt: `Rename this skill.`
Checks:
- returns 3-7 candidates unless asked for one
- best candidate appears first and again as `Best Pick:` in multi-part output
- avoids vague names like `manager`, `helper`, and `util`

## Doctrine should trigger
Prompt: `Find doctrine words for a soundness-focused review agent.`
Checks:
- returns a doctrine stack and doctrine block
- favors procedural words, not prestige words
- includes type-theoretic pressure when relevant

## Should not trigger implicitly
Prompt: `Fix the failing auth tests and update the implementation.`
Checks:
- this belongs to implementation skills unless a wording surface is requested

Prompt: `Review this patch for regressions and invariants.`
Checks:
- this belongs to review skills unless wording or doctrine output is requested

Prompt: `Update this TOML config field.`
Checks:
- does not rewrite machine-consumed syntax for style
