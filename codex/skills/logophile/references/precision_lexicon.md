# Precision lexicon

Use these as guarded phrase upgrades, not mandatory substitutions.

## Good upgrades
- `make better` -> `tighten`
- `handle malformed input` -> `reject malformed input`
- `do more checking` -> `add a direct validating check`
- `improve reliability` -> `bound failure behavior`
- `something is wrong` -> `the change is unsound` (only when the stronger claim is warranted)
- `works in more cases` -> `covers the previously partial path`
- `uses old state` -> `reads stale state`
- `hard to review` -> `increases incidental complexity`

## Guardrails
- only swap when the new phrase is strictly more exact
- preserve obligations, uncertainty, agency, and sequence
- do not force repo jargon when the local text does not support it
