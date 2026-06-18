# st graph intake

Source: .step/proposed-plan.md

## Intent

- intent-001 | requirement | covered
  Text: Create a new `accts` Codex skill with `SKILL.md`, `agents/openai.yaml`, a reusable Python CLI script, and tests.
  Source: .step/proposed-plan.md#implementation

- intent-002 | requirement | covered
  Text: Manage Codex account metadata in TOML while keeping token-bearing `auth.json` copies only in an owner-readable vault.
  Source: .step/proposed-plan.md#locked-decisions

- intent-003 | requirement | covered
  Text: Implement safe account backup, status detection, and activation against `$CODEX_HOME/auth.json`.
  Source: .step/proposed-plan.md#implementation

- intent-004 | requirement | covered
  Text: Implement next-turn account switching through queued state and Codex Stop/SessionStart hook entrypoints without replacing existing hooks.
  Source: .step/proposed-plan.md#locked-decisions

- intent-005 | requirement | covered
  Text: Implement weekly reset rotation using `$cas` account status as the reset authority and a turn-use ledger as actual-use proof.
  Source: .step/proposed-plan.md#locked-decisions

- intent-006 | test-expectation | covered
  Text: Validate the skill with CLI/unit/temp-home/hook/CAS smoke checks, quick_validate, prompt-input smoke, diff check, and st projection checks.
  Source: .step/proposed-plan.md#validation

- intent-007 | requirement | covered
  Text: Ship the validated work in a ready PR, then land it with review-thread/check proof and guarded squash merge.
  Source: .step/proposed-plan.md#implementation

## Items

### st-990 | feature | high

Step: Scaffold `accts` skill surfaces

Covers:
- intent-001

Depends:
- none

Locations:
- codex/skills/accts/SKILL.md
- codex/skills/accts/agents/openai.yaml
- codex/skills/accts/scripts/accts.py
- codex/skills/accts/tests

Acceptance:
- `codex/skills/accts` exists with required skill files and no README/INSTALL/CHANGELOG-style extra docs.
- `agents/openai.yaml` exists and contains a default prompt mentioning `$accts`.

Validation:
- test -f codex/skills/accts/SKILL.md && test -f codex/skills/accts/agents/openai.yaml && test -f codex/skills/accts/scripts/accts.py

Proof:
- proof-990 | scaffold | test -f codex/skills/accts/SKILL.md && test -f codex/skills/accts/agents/openai.yaml && test -f codex/skills/accts/scripts/accts.py

Contract:
Background:
The user wants a new Codex-only account manager skill named `accts`, not a mutation of the borrowed `caam` skill.

Objective:
Create the skill skeleton and reusable CLI location.

Implementation Approach:
Use skill-creator/init conventions, then replace template content with real `accts` guidance and code.

Risks:
- Creating unnecessary docs or stale placeholder files.
- Misaligned frontmatter name/folder.

### st-991 | feature | high

Step: Implement config, state, vault, backup, status, and activation primitives

Covers:
- intent-002
- intent-003

Depends:
- st-990

Locations:
- codex/skills/accts/scripts/accts.py
- codex/skills/accts/tests

Acceptance:
- TOML metadata parses and token-looking TOML keys are rejected.
- Vault writes are atomic, file mode is `0600`, and runtime state stores only non-secret hashes/labels/timestamps.
- `backup`, `ls`, `status`, and `activate` work against temp `$CODEX_HOME`.

Validation:
- python3 -m unittest discover -s codex/skills/accts/tests -p 'test_*.py'

Proof:
- proof-991 | unit | python3 -m unittest discover -s codex/skills/accts/tests -p 'test_*.py'

Contract:
Background:
`auth.json` contains OAuth material and must not be represented in normal TOML config or stdout.

Objective:
Build the safe local account/vault core before adding hooks or reset orchestration.

Implementation Approach:
Use Python stdlib (`argparse`, `tomllib`, `json`, `hashlib`, lock files, `os.replace`) and temp-file atomic writes.

Risks:
- Token leakage through fixtures, error output, or state.
- Corrupting current auth without backup.

### st-992 | feature | high

Step: Implement queued next-turn hook switching

Covers:
- intent-004

Depends:
- st-991

Locations:
- codex/skills/accts/scripts/accts.py
- codex/skills/accts/tests

Acceptance:
- `queue`, `hook print`, `hook install`, `hook uninstall`, `hook stop`, and `hook session-start` are implemented.
- Hook install/uninstall preserves unrelated existing `hooks.json` entries.
- Stop/SessionStart hook commands apply pending switches exactly once and return valid Codex hook JSON.

Validation:
- python3 -m unittest discover -s codex/skills/accts/tests -p 'test_*.py'

Proof:
- proof-992 | unit | python3 -m unittest discover -s codex/skills/accts/tests -p 'test_*.py'

Contract:
Background:
The user wants an account selected by CLI to be used after the next possible Codex turn.

Objective:
Make queued switching reliable at the Codex hook boundary without promising mid-response auth reload.

Implementation Approach:
Merge tagged `accts` Stop/SessionStart hook entries into existing JSON; hook handlers read pending state, activate atomically, and mark the pending entry consumed.

Risks:
- Breaking existing `$st` or other hooks.
- Hook trust not yet granted after install.

### st-993 | feature | high

Step: Implement CAS-backed reset-cycle rotation and turn-use ledger

Covers:
- intent-005

Depends:
- st-992

Locations:
- codex/skills/accts/scripts/accts.py
- codex/skills/accts/tests

Acceptance:
- `reset-cycle status`, `reset-cycle start`, and `reset-cycle advance` parse CAS account status.
- Adapter prefers `cas account status --json --usage --hooks off`, falls back to `$SKILLS_ZIG_REPO/zig-out/bin/cas_account`.
- Missing weekly secondary fields fail closed.
- Fixture tests prove all enabled accounts are queued/touched once per weekly cycle using turn-use ledger rows.

Validation:
- python3 -m unittest discover -s codex/skills/accts/tests -p 'test_*.py'
- /Users/tk/workspace/tk/skills-zig/zig-out/bin/cas_account status --cwd /Users/tk/.dotfiles --json --usage --hooks off

Proof:
- proof-993 | unit | python3 -m unittest discover -s codex/skills/accts/tests -p 'test_*.py'
- proof-993b | cas-smoke | /Users/tk/workspace/tk/skills-zig/zig-out/bin/cas_account status --cwd /Users/tk/.dotfiles --json --usage --hooks off

Contract:
Background:
CAS status is the source for reset timing, but status observation alone is not proof that an account has been used in a real Codex turn.

Objective:
Rotate through accounts after weekly reset and prove per-account turn usage.

Implementation Approach:
Store a reset-cycle key from CAS weekly secondary window fields and a `turn_use_ledger` row when Stop hook completes a turn for an account.

Risks:
- Treating CAS status read as usage proof.
- Homebrew `cas` lacking the `account` subcommand in the current environment.

### st-994 | feature | medium

Step: Author `accts` skill instructions and UI metadata

Covers:
- intent-001
- intent-006

Depends:
- st-993

Locations:
- codex/skills/accts/SKILL.md
- codex/skills/accts/agents/openai.yaml

Acceptance:
- `SKILL.md` is procedural, concise, under 500 lines, and documents safety, commands, hook workflow, reset-cycle workflow, and validation.
- `agents/openai.yaml` is generated or verified consistent with the skill.

Validation:
- uv run --with pyyaml -- python3 codex/skills/.system/skill-creator/scripts/quick_validate.py codex/skills/accts

Proof:
- proof-994 | skill-validation | uv run --with pyyaml -- python3 codex/skills/.system/skill-creator/scripts/quick_validate.py codex/skills/accts

Contract:
Background:
Skills should be lean trigger/workflow artifacts with reusable scripts, not broad documentation packages.

Objective:
Make `$accts` usable by future Codex sessions without excessive context.

Implementation Approach:
Keep detailed CLI behavior in the script/help/tests and put only operational guidance in `SKILL.md`.

Risks:
- Trigger text too vague for account-management use.
- Overlong skill body or stale UI metadata.

### st-995 | feature | high

Step: Run full validation and fixed-point closure checks

Covers:
- intent-006

Depends:
- st-994

Locations:
- codex/skills/accts
- .step

Acceptance:
- CLI help, unit tests, temp-home dry run, quick_validate, live redacted CAS status smoke, `codex debug prompt-input`, `git diff --check`, `st doctor`, and `st assert-projection` pass.
- Root-equivalent fixed-point review finds no duplicate truth owners, token-leak paths, hook-preservation gaps, or unretired scaffolds.

Validation:
- python3 codex/skills/accts/scripts/accts.py --help
- python3 -m unittest discover -s codex/skills/accts/tests -p 'test_*.py'
- CODEX_HOME="$(mktemp -d)" ACCTS_HOME="$(mktemp -d)" python3 codex/skills/accts/scripts/accts.py init --dry-run
- uv run --with pyyaml -- python3 codex/skills/.system/skill-creator/scripts/quick_validate.py codex/skills/accts
- /Users/tk/workspace/tk/skills-zig/zig-out/bin/cas_account status --cwd /Users/tk/.dotfiles --json --usage --hooks off
- codex debug prompt-input
- git diff --check
- st doctor --file .step/st-plan.jsonl
- st assert-projection --file .step/st-plan.jsonl

Proof:
- proof-995 | validation-bundle | full validation bundle

Contract:
Background:
Actuating requires current proof before shipping.

Objective:
Prove the branch is ready for PR publication.

Implementation Approach:
Run narrow functional tests first, then repo/skill validation, then runtime and st projection checks.

Risks:
- Treating scaffold checks as integration proof.
- Missing hook/CAS proof.

### st-996 | feature | high

Step: Ship ready PR with validation proof

Covers:
- intent-007

Depends:
- st-995

Locations:
- GitHub PR

Acceptance:
- Branch is pushed.
- Ready PR exists with concise summary, scope, proof, and readiness.

Validation:
- gh pr view --json url,state,isDraft,headRefOid

Proof:
- proof-996 | ship | gh pr view --json url,state,isDraft,headRefOid

Contract:
Background:
The user asked for `$actuating`, which includes proof-backed PR publication when validation passes.

Objective:
Publish the validated branch as a ready PR.

Implementation Approach:
Use `gh pr create` or `gh pr edit` according to existing-PR state, defaulting to ready after validation.

Risks:
- Duplicate PR.
- PR body overclaims proof.

### st-997 | feature | high

Step: Land PR with guarded merge and cleanup

Covers:
- intent-007

Depends:
- st-996

Locations:
- GitHub PR
- local git branch state

Acceptance:
- Complete review-thread sweep has zero unresolved threads.
- Checks are green or explicitly absent/non-required with mergeStateStatus clean.
- Squash merge uses `--match-head-commit`.
- Local checkout is back on updated `main` and feature branch cleanup is verified.

Validation:
- gh pr view --json state,mergedAt,headRefOid,mergeStateStatus,statusCheckRollup
- gh api graphql reviewThreads sweep
- git status --short --branch

Proof:
- proof-997 | land | PR merged state, review-thread sweep, guarded merge output, and local cleanup status

Contract:
Background:
The user asked for `$land` in the same objective.

Objective:
Merge the PR only after fresh review/check proof on the exact head.

Implementation Approach:
Use GitHub CLI, refetch review threads immediately before merge, and pass `--match-head-commit <headRefOid>`.

Risks:
- Stale review sweep after final push.
- Active requested changes or unresolved review threads.
