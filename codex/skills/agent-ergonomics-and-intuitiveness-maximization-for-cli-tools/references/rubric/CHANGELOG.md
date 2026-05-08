# SCORING-RUBRIC.md CHANGELOG

Every rubric edit MUST land here with a new version + summary. Scores written
under earlier versions are not directly comparable to scores written under
later versions; use `scripts/migrate-scores.sh` to translate.

## Versioning policy

`rubric_version` follows semver:

- **PATCH** (1.0.0 → 1.0.1): Editorial-only. No anchor change. No score migration needed.
- **MINOR** (1.0.1 → 1.1.0): Anchor wording tweaked or new examples; existing scores remain valid but should be re-validated when convenient.
- **MAJOR** (1.1.0 → 2.0.0): Anchor levels reassigned, dim added/removed, weights changed. ALL prior scores must be migrated or invalidated.

When in doubt: prefer MINOR for prose edits, MAJOR for any change that would change scorer behavior on the same surface.

## Score-migration contract

Every MAJOR bump must be accompanied by:

1. A `scripts/migrate-scores.sh` runner that handles the (vN → vN+1) transformation.
2. A documented migration rationale in this CHANGELOG.
3. A test fixture in `references/scoring-fixtures/migration-cases-v<N>-to-v<N+1>.jsonl` showing 5+ surfaces before/after.

If the migration is mechanical (e.g., "all `agent_ergonomics` ≥ 750 are bumped to ≥ 800 because anchor 750 was tightened"), document the formula. If it requires re-scoring, flag with `requires_rescoring: true` and document the cost.

## Versions

### 1.0.0 (2026-05-07)

- **Status:** initial versioned release.
- **Scope:** assigns explicit version to the rubric as it existed at end-of-Round-L.
- **Migration:** none required (no prior versioned data).
- **Affected dims:** all 11.
- **Notes:** Frontmatter added at top of SCORING-RUBRIC.md. Migration script registered. validate-artifacts-strict.sh now warns when scores reference an unknown rubric_version.

### Pre-1.0 (history)

The rubric existed unversioned through rounds A-L. Scores from those passes are flagged with `rubric_version: "pre-1.0"` and treated as advisory; do not include them in calibration corpora.

## How to bump

1. Edit `SCORING-RUBRIC.md`. Update the frontmatter:
   ```
   rubric_version: 1.1.0
   last_changed_at: 2026-MM-DD
   last_changed_summary: "tightened agent_ergonomics 750 anchor — now requires --json AND error-pedagogy hint."
   ```
2. Add a new section to this CHANGELOG with the same date and summary.
3. If MAJOR: write the migration in `scripts/migrate-scores.sh` and add fixtures.
4. Run `scripts/rubric-fitness.sh` against an existing corpus to verify the new rubric produces sensible scores.
5. Commit `SCORING-RUBRIC.md`, `CHANGELOG.md`, and any migration assets together.

## Anti-patterns

- **Don't bump the version without a CHANGELOG entry.** Future scorers will see the new version with no idea what changed.
- **Don't re-use a version number.** Even if the prior commit was a typo fix, bump to the next PATCH.
- **Don't break MAJOR without migration.** Old scores in the field would become uninterpretable.
