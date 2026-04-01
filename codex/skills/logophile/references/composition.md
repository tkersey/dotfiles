# Composing With Logophile

`logophile` is shared advisory style infrastructure for Codex skills in this repo. It is not a hidden default.

## Use It Explicitly
- Invoke `$logophile` when the task explicitly includes wording, phrasing, or naming work.
- Keep the domain skill in charge of the actual domain behavior.
- Let `logophile` own wording precision only.

## Good Composition Patterns
- `Use $refine for the workflow change and $logophile for the final wording pass.`
- `Use $logophile to tighten the contract language without changing the policy.`
- `After the implementation diff is settled, use $logophile on the public-facing section headings.`

## Bad Composition Patterns
- `Assume logophile silently rewrites every answer.`
- `Use logophile to make architectural decisions.`
- `Route every documentation task through logophile even when no wording issue exists.`

## Consumer Rules
- Other skills may cite `logophile` as the wording pass when they explicitly need rewrite help.
- Other skills should not inline `logophile` as hidden policy or claim that its lexicon is repo law.
- If a consumer skill needs a domain-specific wording rule, keep that rule local unless it clearly belongs in the shared lexicon.

## Ownership Boundary
- Domain skill owns the content, claims, and workflow.
- `logophile` owns precision, substitution quality, and naming sharpness.
- When the two conflict, preserve domain truth first and wording optimization second.
