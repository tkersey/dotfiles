# Probe cases

## Rewrite should trigger
Prompt:
`Use $logophile to tighten this paragraph without changing meaning.`

Checks:
- preserves meaning
- sharpens wording
- keeps structure when useful

## Skill metadata compression should trigger
Prompt:
`Use $logophile to compress this SKILL.md description under 1024 characters while preserving the trigger surface.`

Checks:
- preserves meaning and trigger coverage
- keeps the frontmatter value YAML parse-safe
- avoids unquoted colon-space phrases unless the scalar is quoted
- expects the edited skill to pass `quick_validate.py`

## Naming should trigger
Prompt:
`Use $logophile to rename this skill.`

Checks:
- returns 3-7 candidates unless asked for one
- best candidate is last under `Best Pick:` when multi-part output is used

## Doctrine should trigger
Prompt:
`Use $logophile to derive doctrine words for a soundness-focused review agent.`

Checks:
- returns a doctrine stack and doctrine block
- favors procedural words, not prestige words
