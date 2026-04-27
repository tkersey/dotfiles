Iteration: 3

# Move `$parse` Onto Raw `parse-arch collect`

## Round Delta
- Converted the `$grill-me` output into the full `$plan` contract with iteration proof, traceability, rollout, rollback, and signoff surfaces.
- Locked the campaign order: implement `parse-arch` local-build contract first, delete `.dotfiles` helper against that local proof, then complete release/tap closure.
- Added explicit stale-CLI contract checking so `$parse` fails closed when raw CLI output lacks the new stable fields.

## Summary
Objective: make `parse-arch` 0.2.0 own the full `$parse` collection contract so `codex/skills/parse/scripts/run_parse_collect.sh` can be deleted. Chosen path: add stable read-depth diagnostics directly to `parse-arch collect`, validate with local `zig-out/bin/parse-arch`, update `.dotfiles` to raw CLI usage, then publish and prove the Homebrew-installed binary. Done means no helper references remain, local and installed CLIs emit the same contract fields, and tap proof passes.

First execution wave is in `skills-zig`: implement the CLI JSON contract without broad architecture scoring retunes. Second wave is `.dotfiles`: delete the helper and update skill docs/prompts. Third wave is release propagation: publish `parse-arch-v0.2.0` and update `homebrew-tap`.

## Implementation Brief
1. step=implement_cli_contract; owner=skills-zig implementer; success_criteria=`parse-arch collect` always emits stable read-depth fields and focused runs report `focused`.
2. step=extend_eval_suite; owner=skills-zig implementer; success_criteria=eval cases assert verdict/classes/suggestions and fail on regression.
3. step=local_build_proof; owner=skills-zig implementer; success_criteria=build/test/eval plus `.dotfiles` and `skills-zig` smoke checks pass using `./zig-out/bin/parse-arch`.
4. step=delete_dotfiles_helper; owner=.dotfiles implementer; success_criteria=helper file removed, docs/prompts use raw CLI, quick_validate passes, no helper references remain.
5. step=release_parse_arch_020; owner=release implementer; success_criteria=`parse-arch-v0.2.0` assets published for Darwin arm64 and Linux x86_64.
6. step=update_homebrew_tap; owner=tap implementer; success_criteria=formula version/SHA updated and brew audit/test/upgrade plus installed field smoke pass.
