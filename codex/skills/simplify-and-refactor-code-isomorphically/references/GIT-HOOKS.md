# Git hooks — native pre-commit/pre-push as a belt-and-suspenders layer

> Claude Code hooks ([HOOKS.md](HOOKS.md)) catch violations at the tool
> boundary (PreToolUse). Git hooks catch them at the repo boundary (git
> commit / git push). Both layers are worth having: agents bypass one,
> the other still fires.

## Contents

1. [When to use git hooks (vs cc-hooks)](#when-to-use-git-hooks-vs-cc-hooks)
2. [pre-commit script](#pre-commit-script)
3. [commit-msg script](#commit-msg-script)
4. [pre-push script](#pre-push-script)
5. [Installing (husky / lefthook / native)](#installing-husky--lefthook--native)
6. [Bypassing — the rules](#bypassing--the-rules)
7. [Interaction with CI](#interaction-with-ci)

---

## When to use git hooks (vs cc-hooks)

| Check                          | cc-hook | git-hook | CI |
|--------------------------------|:-------:|:--------:|:--:|
| Block `sed -i` in tool call    |   ✅    |    —     | —  |
| Block `_v2.*` filename in write|   ✅    |    ✅    | ✅ |
| UBS on staged diff             |    —    |    ✅    | ✅ |
| Warning ceiling check          |   ✅    |    ✅    | ✅ |
| Golden-diff verify             |    —    |    —     | ✅ |
| Forbid `unwrap()` growth       |    —    |    ✅    | ✅ |
| Validate commit message format |    —    |    ✅    | ✅ |

Git hooks are most valuable for team settings where humans and agents
share the repo — the agent might bypass cc-hooks (different env), but
everyone commits through git.

## pre-commit script

`.git/hooks/pre-commit` (mode 0755):

```bash
#!/usr/bin/env bash
# Skill-enforced pre-commit. See git-hooks.md.
set -euo pipefail

SKILL="./.claude/skills/simplify-and-refactor-code-isomorphically"

# 1. Forbidden filenames in staged tree
staged=$(git diff --cached --name-only --diff-filter=A)
if echo "$staged" | grep -E '(_v2|_new|_improved|tmp_|_backup)\.(rs|ts|tsx|py|go|c|cpp|h|hpp)$' >/dev/null; then
  echo "pre-commit: staged file uses _v2/_new/tmp_/_backup naming — refactor skill forbids this pattern."
  echo "           merge the file back to its canonical name or rename."
  exit 1
fi

# 2. Forbidden substrings added in the diff
added=$(git diff --cached -U0 | grep -E '^\+' | grep -v '^\+\+\+')

if echo "$added" | grep -E ':\s*any\b|<any>|\bas any\b' >/dev/null; then
  echo "pre-commit: new 'any' added in TS diff. Use a narrower type."
  exit 1
fi

if echo "$added" | grep -E '\.unwrap\(\)|\.expect\(' >/dev/null; then
  echo "pre-commit: new .unwrap()/.expect() added in Rust diff."
  echo "           use ? or match, or ceiling-relax with justification."
  exit 1
fi

if echo "$added" | grep -E '^\+\s*except\s*:\s*$|^\+\s*except Exception\s*:\s*pass$' >/dev/null; then
  echo "pre-commit: bare/pass-swallowing except added in Python diff."
  exit 1
fi

if echo "$added" | grep -E '^\+\s*//\s*@ts-ignore|^\+\s*//\s*@ts-expect-error' >/dev/null; then
  echo "pre-commit: ts-ignore added."
  exit 1
fi

# 3. Warning ceiling
if [[ -x "$SKILL/scripts/lint_ceiling.sh" ]]; then
  "$SKILL/scripts/lint_ceiling.sh" check || {
    echo "pre-commit: warning ceiling exceeded."
    exit 1
  }
fi

# 4. UBS on the staged diff if installed
if command -v ubs >/dev/null; then
  ubs --staged --robot-json > /tmp/ubs_precommit.json 2>&1 || true
  crit=$(jq '.critical // 0' /tmp/ubs_precommit.json 2>/dev/null || echo 0)
  if [[ "$crit" -gt 0 ]]; then
    echo "pre-commit: UBS found $crit critical issues. See /tmp/ubs_precommit.json."
    exit 1
  fi
fi

exit 0
```

## commit-msg script

`.git/hooks/commit-msg` (mode 0755):

```bash
#!/usr/bin/env bash
# Enforce refactor commit-message format (see FORMULAS.md).
set -euo pipefail

MSG_FILE="$1"
first_line=$(head -1 "$MSG_FILE")

# Only enforce on refactor commits
if [[ ! "$first_line" =~ ^refactor\( ]]; then
  exit 0
fi

# Format: refactor(<area>): <summary>
if [[ ! "$first_line" =~ ^refactor\([a-z0-9_-]+\):\ .{5,80}$ ]]; then
  echo "commit-msg: refactor commits must match: refactor(<area>): <summary 5-80 chars>"
  echo "            got: $first_line"
  exit 1
fi

# Body should contain Candidate: ISO-<nnn> if it's a skill-produced commit
if ! grep -E '^Candidate: ISO-[0-9]+' "$MSG_FILE" >/dev/null; then
  echo "commit-msg: WARNING — no 'Candidate: ISO-<nnn>' line in body."
  echo "            if this commit is from the refactor skill, add it."
  # warn only, don't block
fi

exit 0
```

## pre-push script

`.git/hooks/pre-push` (mode 0755):

```bash
#!/usr/bin/env bash
# Verify isomorphism before push.
set -euo pipefail

SKILL="./.claude/skills/simplify-and-refactor-code-isomorphically"
RUN_ID_FILE="refactor/artifacts/.current-run-id"

# If no active run, nothing to verify
if [[ ! -f "$RUN_ID_FILE" ]]; then
  exit 0
fi

RUN_ID=$(cat "$RUN_ID_FILE")

if [[ -x "$SKILL/scripts/verify_isomorphism.sh" ]]; then
  "$SKILL/scripts/verify_isomorphism.sh" "$RUN_ID" || {
    echo "pre-push: isomorphism verification failed for run $RUN_ID."
    echo "          revert the offending commit or run the card audit again."
    exit 1
  }
fi

exit 0
```

Note: `refactor/artifacts/.current-run-id` is a convention — the skill's
`session_setup.sh` can write it so later hooks know which run to verify.

## Installing (husky / lefthook / native)

### Native

```bash
# From repo root
cp .claude/skills/simplify-and-refactor-code-isomorphically/assets/hooks/* .git/hooks/
chmod +x .git/hooks/{pre-commit,commit-msg,pre-push}
```

### Husky (JS/TS projects)

```json
// package.json
{
  "husky": {
    "hooks": {
      "pre-commit": "./.claude/skills/simplify-and-refactor-code-isomorphically/assets/hooks/pre-commit",
      "commit-msg": "./.claude/skills/simplify-and-refactor-code-isomorphically/assets/hooks/commit-msg HUSKY_GIT_PARAMS",
      "pre-push": "./.claude/skills/simplify-and-refactor-code-isomorphically/assets/hooks/pre-push"
    }
  }
}
```

### Lefthook (polyglot)

```yaml
# lefthook.yml
pre-commit:
  commands:
    skill-checks:
      run: ./.claude/skills/simplify-and-refactor-code-isomorphically/assets/hooks/pre-commit

commit-msg:
  commands:
    format:
      run: ./.claude/skills/simplify-and-refactor-code-isomorphically/assets/hooks/commit-msg {1}

pre-push:
  commands:
    isomorphism:
      run: ./.claude/skills/simplify-and-refactor-code-isomorphically/assets/hooks/pre-push
```

## Bypassing — the rules

`git commit --no-verify` exists. Someone WILL use it. Rules:

- **Agents:** never pass `--no-verify`. If a hook blocks, that's signal,
  not noise. Fix the underlying issue.
- **Humans:** `--no-verify` is allowed only for genuine hook bugs, and
  the commit body must say `NO-VERIFY-REASON: <explanation>`. PR
  reviewers must scrutinize any `--no-verify` commit.
- **Pre-push force:** `git push --force` is blocked by dcg in safer
  setups. Never force-push `main` or a release branch.

If a hook is legitimately wrong, fix the hook in a separate commit,
don't bypass it.

## Interaction with CI

CI is the ultimate enforcer — it runs on a clean VM that agents cannot
subvert. See [CI-CD-INTEGRATION.md](CI-CD-INTEGRATION.md) for the full CI
setup that mirrors these hooks, so even a `--no-verify` commit fails in
CI before it can merge.

Hooks catch issues early (cheaper to fix locally). CI is the safety net.
Don't rely on one without the other.
