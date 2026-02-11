---
name: logophile
description: "Editing mode for clarity and semantic density. Trigger cues/keywords: `$logophile`, tighten wording, rewrite for brevity, sharpen prompts/docs/specs/emails, compress verbose text, improve naming/title/label options, and keep intent/tone while making copy faster to scan."
---

# Logophile

## Intent
Maximize semantic density: fewer tokens, same meaning.

## Use when
- User asks to tighten/clarify/compress.
- Text is verbose/repetitive or slow to scan (<30s).
- Names/titles/labels/headings feel weak.

## Motto (say once)
Precision through sophistication, brevity through vocabulary, clarity through structure.

## Output (default: fast)
- fast: revised text only (no preamble, no recap).
- annotated: revised text + `Edits:` (lexical; structural).
- delta: only if asked or reduction > 40% (words/chars).

## Loop (Distill -> Densify -> Shape -> Verify)
- Distill: 1-sentence intent; must-keep tokens (numbers/keywords/quotes/code).
- Densify: delete filler/hedges; verbify nouns; precision ladder (axis -> exact verb/property); reuse terms.
- Shape: lead with action; keep sentences atomic; parallelize lists; punctuation > scaffolding.
- Verify: intent/obligations/risks/scope unchanged; required tokens + format preserved.

## Guardrails
- Don't change intent.
- Don't compress away obligations, risks, or scope.
- Don't "upgrade" vocabulary if it changes meaning or increases tokens without adding precision.
- Don't add meta-text ("here's", "I think", "note that") unless requested.

## Constraints (ask only if blocked)
Fields: must_keep; must_not_change; tone; length_target; format; keywords_include; keywords_avoid.
Defaults: must_keep=all facts/numbers/quotes/code; tone=original; format=preserve; length_target=min safe.

## Elevation (precision ladder)
- Step: vague word -> axis (what changes?) -> exact verb/property -> object.
- Axis: correctness | speed | cost | reliability | security | UX | scope | consistency.
- Swaps (only if true): improve->simplify/stabilize/accelerate/harden; handle->parse/validate/normalize/route/retry/throttle; robust->bounded/idempotent/deterministic/fail-closed.
- Term-of-art rule: use 1 domain term if it replaces >=3 tokens and fits audience; else keep phrase.

## High-ROI compressions
- in order to -> to; due to the fact that -> because; is able to -> can.
- there is/are -> concrete subject + verb.
- nominalization -> verb (conduct an analysis -> analyze).
- delete: throat-clearing, apologies, self-reference, empty intensifiers.
- token-aware: prefer short, common words; digits + contractions if tone allows.
