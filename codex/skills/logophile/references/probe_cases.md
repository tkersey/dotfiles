# Logophile Probe Cases

Use these probes to validate substitution-first behavior, output shape, and meaning safety.

## P01: fast output stays text-only
- `case_id`: `fast_text_only`
- `mode`: `fast`
- `input`: `In order to proceed, we need to verify access to staging.`
- `must_keep`: `proceed`, `verify`, `staging`
- `expected_behavior`: return only rewritten text such as `To proceed, verify access to staging.`
- `forbidden_behavior`: `Mode: Logophile`, motto text, commentary, recap, or any wrapper around the rewrite

## P02: generic survivor must upgrade
- `case_id`: `generic_survivor_upgrade`
- `mode`: `fast`
- `input`: `We should iterate on improvements to the skill.`
- `must_keep`: `skill`
- `expected_behavior`: replace `iterate on improvements` with a sharper phrase such as `find accretive changes`, `tighten the contract`, or another context-fit substitute
- `forbidden_behavior`: leaving `iterate` and `improvements` unchanged

## P03: precision can beat brevity
- `case_id`: `precision_beats_brevity`
- `mode`: `fast`
- `input`: `We need to make the error path better.`
- `must_keep`: `error path`
- `expected_behavior`: choose a more exact phrase such as `harden the error path` even if the result is not shorter
- `forbidden_behavior`: generic outputs like `make the error path nicer`

## P04: handle must become an action
- `case_id`: `handle_specific_action`
- `mode`: `annotated`
- `input`: `We need to handle malformed inputs better.`
- `must_keep`: `malformed inputs`
- `expected_behavior`: rewrite with a concrete action such as `reject`, `validate`, or `normalize`; `Edits:` must mention the substitution
- `forbidden_behavior`: preserving `handle`

## P05: context override beats lexicon default
- `case_id`: `context_override`
- `mode`: `fast`
- `input`: `Choose the final wording for user-facing setup copy so it reads plainly.`
- `must_keep`: `final wording`, `user-facing`, `plainly`
- `expected_behavior`: keep the rewrite plain and precise; do not force a higher-register repo term just because it is in the lexicon
- `forbidden_behavior`: introducing `accretive`, `fail-closed`, or other specialized repo terms that break the local register

## P06: uncertainty must survive
- `case_id`: `uncertainty_preserved`
- `mode`: `annotated`
- `input`: `We think the issue is probably due to cache configuration.`
- `must_keep`: uncertainty
- `expected_behavior`: compress the hedge to something like `The issue is likely due to cache configuration.` and note that certainty did not increase
- `forbidden_behavior`: `The issue is due to cache configuration.`

## P07: naming mode stays separate
- `case_id`: `naming_mode`
- `mode`: `naming`
- `input`: `Things to Do Before Release`
- `must_keep`: release intent
- `expected_behavior`: return candidate names only
- `forbidden_behavior`: rewrite audit text, commentary about substitutions, or generic prose paragraphs
