# Formulas — copy-paste templates for artifacts and prompts

> Every artifact this skill produces has a canonical shape. Copy from here,
> fill the placeholders, commit. If the shape needs to change, change it
> here and propagate — don't fork per-project.

## Contents

1. [Candidate line — `duplication_map.md`](#candidate-line--duplication_mapmd)
2. [Ledger row](#ledger-row)
3. [Rejection log entry](#rejection-log-entry)
4. [Isomorphism-card fields](#isomorphism-card-fields)
5. [Commit message](#commit-message)
6. [PR title and body](#pr-title-and-body)
7. [Beads title & body](#beads-title--body)
8. [Pass-closeout summary](#pass-closeout-summary)
9. [Subagent prompt — extractor](#subagent-prompt--extractor)
10. [Subagent prompt — reviewer](#subagent-prompt--reviewer)

---

## Candidate line — `duplication_map.md`

```
- <ID> | <clone-type I/II/III/IV/V> | <N sites> | <est LOC saved> | <path:line, path:line, ...> | <one-line lever summary>
```

Example:

```
- ISO-014 | II | 3 | 42 | src/ingest/users.ts:18, src/ingest/accounts.ts:22, src/ingest/orgs.ts:31 | extract mapRows helper
```

## Ledger row

```
| <ID> | <type> | <N sites> | <lever> | <LOC saved> | <L/M/H risk> | <green/red tests> | <commit-sha> | <shipped/reverted/rejected> |
```

## Rejection log entry

Use the full block from [assets/rejection_log.md](../assets/rejection_log.md).

## Isomorphism-card fields

Use the full template from [assets/isomorphism_card.md](../assets/isomorphism_card.md).
Non-negotiable minimum: identity, sites, observable contract, hidden diffs, proof, commit plan.

## Commit message

```
refactor(<area>): <one-lever summary>

Candidate: ISO-<nnn>
Clone type: <I|II|III|IV|V>
Sites collapsed: <N>
LOC before/after: <before>/<after> (Δ <delta>)
Lever: <L-EXTRACT | L-PARAMETERIZE | L-DISPATCH | L-ELIMINATE | L-TYPE-SHRINK | L-MERGE-FILES | L-PIN-DEP>

Observable behavior: unchanged. Proof:
  - tests: <pass-count> → <pass-count> (identical set of failures, if any)
  - goldens: byte-identical (<list of golden-dirs>)
  - warnings: ≤ ceiling (<n>/<ceiling>)

Isomorphism card: refactor/artifacts/<run-id>/cards/ISO-<nnn>.md
```

## PR title and body

Title: `refactor(<area>): <one-lever summary>`

Body: use [assets/pr_description.md](../assets/pr_description.md).

## Beads title & body

Title:

```
ISO-<nnn> — <one-line description>
```

Body: the full isomorphism card. Link commits as they land with `br link`.

## Pass-closeout summary

At the end of a pass, emit this block and commit to `refactor/artifacts/<run-id>/CLOSEOUT.md`:

```markdown
# Refactor pass closeout — <run-id>

## Stats
- Collapses shipped:     N
- Collapses reverted:    N
- Candidates rejected:   N
- LOC before/after:      X / Y (Δ -Z)
- Test pass rate:        100% → 100%
- Warning ceiling:       before / after

## Shipped
<copy the latest N ledger rows where verdict=shipped>

## Reverted
<copy the REVERTED rows, with post-mortem one-liners>

## Rejections (new this pass)
<copy each rejection_log entry added this pass>

## Follow-ups
<list of beads filed during the pass that aren't yet done>

## Surprises & lessons
<freeform — 3–5 sentences max, things that would change how the next pass runs>
```

## Subagent prompt — extractor

```
You are the refactor-extractor subagent. The driver has selected ISO-<nnn>:
<paste from duplication_map.md>

Your single job:

1. Read the isomorphism card at refactor/artifacts/<run-id>/cards/ISO-<nnn>.md.
2. Read EVERY site listed in the card in full.
3. Propose a concrete Edit-tool plan (file, old_string, new_string) to collapse
   the sites with lever <L-*>.
4. Do NOT execute any Edits. Return the plan only.

Forbidden: sed, codemod, grep-replace, rewriting whole files, touching unrelated code.

If any site's observable contract diverges from the card, STOP and report.
```

## Subagent prompt — reviewer

```
You are the refactor-reviewer subagent. Review the attached diff.

Check, in order:

1. Does the diff match exactly the isomorphism card at
   refactor/artifacts/<run-id>/cards/ISO-<nnn>.md? Flag any extra changes.
2. Any new `any`, `unwrap`, `ignore`, bare `except:` in the diff?
3. Any new `_v2` / `_new` / `tmp_` in added filenames?
4. Any deleted tests or modified test assertions?
5. Any new feature flags / env-vars?
6. Any API surface growth?

Report:
- PASS — the diff satisfies the card and adds no collateral changes, OR
- FAIL — list each finding by file:line with a one-line justification.

Do NOT propose further changes. Your job is to verify, not to re-refactor.
```
