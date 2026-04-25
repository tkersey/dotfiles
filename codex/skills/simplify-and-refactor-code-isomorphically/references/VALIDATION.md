# Validation — runnable checks for the skill itself

> This page is for maintainers evolving this skill. It turns `/sw` and
> `operationalizing-expertise` guidance into a read-only release gate:
> frontmatter is triggerable, references are discoverable, operator cards are
> complete, the quote bank is auditable, and the marker-delimited kernel can
> be extracted by tooling.

## Contents

1. [Why this exists](#why-this-exists)
2. [Fast validation](#fast-validation)
3. [Individual gates](#individual-gates)
4. [What each gate proves](#what-each-gate-proves)
5. [Common failures](#common-failures)
6. [Release checklist](#release-checklist)

---

## Why this exists

The skill is intentionally large. Size is fine only if the entry point stays
triggerable and the deep material stays mechanically auditable. The validators
are read-only; they do not rewrite files and do not create artifacts outside
normal Python bytecode caches.

The contracts come from three sources:

- `/sw`: frontmatter starts at byte 0, description is short, first 50 lines
  carry the workflow, depth lives under `references/`.
- `/sc`: research-backed insights must be reflected in the skill, and
  progressive-disclosure links must remain intact.
- `/operationalizing-expertise`: corpus entries, triangulated kernel, operator
  cards, and validators are the methodology contract.

---

## Fast validation

Run this from the skill directory:

```bash
./scripts/validate_skill_contract.py
```

Expected:

```text
skill contract validation: PASS
```

This top-level gate calls the operator and corpus validators, checks script
syntax, verifies local files and section anchors across the skill's Markdown
surface, confirms every reference has a `## Contents` block, and catches stale
P1-P21 references after the catalog expanded to P1-P40.

`ai_slop_detector.sh` additionally requires `rg` (ripgrep). The scanner uses
language-aware filters such as `--type ts` and `--type rust`; a plain `grep`
fallback would silently miss most findings.

---

## Individual gates

```bash
./scripts/extract_kernel.sh > /tmp/refactor-kernel.md
./scripts/validate_operators.py
./scripts/validate_corpus.py
./scripts/validate_skill_contract.py
```

Syntax-only checks:

```bash
for s in scripts/*.sh; do bash -n "$s"; done
for p in scripts/*.py; do python3 -m py_compile "$p"; done
```

Skill-package validator, when available:

```bash
~/.claude/skills/sw/scripts/validate-skill.py /data/projects/je_private_skills_repo/.claude/skills/simplify-and-refactor-code-isomorphically/
```

---

## What each gate proves

| Gate | Proves | Does not prove |
|------|--------|----------------|
| `extract_kernel.sh` | `TRIANGULATED-KERNEL.md` has stable START/END markers and can be consumed by automation | the rules are correct |
| `validate_operators.py` | each operator card has definition, 3+ triggers, 2+ failure modes, and a prompt module | the prompt module is brilliant |
| `validate_corpus.py` | quote IDs have source, tags, verbatim text, derived rule, and usage fields | every quote is independently true |
| `validate_skill_contract.py` | package-level shape, links, anchors, script syntax, P1-P40 consistency | runtime behavior on arbitrary user repos |
| `SELF-TEST.md` scenarios | trigger behavior and model-class behavior | exhaustive coverage |

---

## Common failures

**Broken local link**

`validate_skill_contract.py` checks local links and Markdown section anchors
from `SKILL.md`, `SELF-TEST.md`, `CHANGELOG.md`, `references/*.md`,
`assets/*.md`, and `subagents/*.md`. It ignores fenced and inline code
examples so generic syntax such as `func F[T any]` does not become a fake
Markdown link, while still validating links whose labels are inline code such
as ``[`ledger_row.sh`](../scripts/ledger_row.sh)``. Anchor extraction also
ignores headings inside fenced examples so a template's `## Summary` cannot
mask a broken real section link, and it preserves generic/code-span text such
as `Box<dyn Trait>` and `parse<T: FromStr>` when computing GitHub-style
heading IDs. Headings that contain Markdown links are slugged from rendered
link text, not the target URL. Anchor extraction follows CommonMark's 0-3
leading-space rule for headings and fenced code blocks: `   ## Heading` is a
real heading, while `    ## Heading` is indented code. The validator contains
regression samples for these slug and parser rules. If a target was renamed,
update the link in place. Do not create a duplicate alias file.

**Missing operator prompt module**

Every operator must be directly usable by an agent. Add a concise `Prompt
module` block to the existing operator card; do not fork a second operator with
nearly the same name.

**Stale P1-P21 wording**

The pathology catalog now runs P1-P40. If a scanner or entry point says P1-P21,
it is stale and should be updated to P1-P40.

**Reference lacks `## Contents`**

Add a small contents list near the top. This keeps large reference files usable
for weaker models and for humans scanning in a terminal.

---

## Release checklist

- [ ] `SKILL.md` first 50 lines still state the One Rule, loop, pre-flight, and
      quick reference pointer.
- [ ] New deep content lives in `references/`, not in the entry point.
- [ ] New scripts are read-only unless their name and docs explicitly say they
      generate artifacts.
- [ ] Operator changes pass `validate_operators.py`.
- [ ] Corpus changes pass `validate_corpus.py`.
- [ ] Full package passes `validate_skill_contract.py`.
- [ ] `CHANGELOG.md` has an `[Unreleased]` entry describing the change.
