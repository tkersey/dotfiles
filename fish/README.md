# Native Fish prompt

A single-line replacement for the effective saved Tide setup, using Fish's
`fish_prompt`, `fish_right_prompt`, `fish_git_prompt`, `prompt_pwd`, and builtins.
No Tide, Starship, prompt framework, or new runtime dependency is required.
The existing `config.fish`, other plugins, installation script, and Ghostty
configuration are unchanged. Use Fish 4.x; CI records its tested version.

## Migrate: uninstall Tide before merging

`links.conf` symlinks this entire directory to `~/.config/fish`, so Fisher's
uninstall edits the checkout too. **Uninstall before merging or checking out the
native prompt**: Tide owns the old `fish_prompt.fish` and `fish_mode_prompt.fish`
paths and could delete their replacements if removed afterward.

Start in the dotfiles checkout on `main`, with unrelated tracked edits committed
or safely stashed. Make a private backup outside the repository, following the
Fish-directory symlink rather than copying just the link:

```fish
set backup "$HOME/.local/state/fish-before-native-"(date +%Y%m%d-%H%M%S)"-$fish_pid"
mkdir -p -m 700 "$backup"
cp -RL "$__fish_config_dir/." "$backup/"
fisher list > "$backup/plugins-before.txt"
fisher remove ilancosman/tide@v6
```

If you already removed Tide, skip that uninstall command. If the installed spec
is different, use the exact Tide entry from `fisher list`; do not install another
plugin manager. Confirm `fisher list` no longer includes Tide.

Fisher has now removed Tide's registration and universal settings. Before
pulling the merged PR, save its tracked file removals in a local stash. Use a
plain shell for this short interval so restored old files are not loaded by a
new Fish session:

```fish
sh
```

Run the following in that `sh`, still in the dotfiles checkout:

```sh
git stash push -m 'Tide uninstall before native prompt' -- fish
```

**Now merge the PR on GitHub**, then update the local checkout:

```sh
git pull --ff-only
exit
```

Back in Fish, start a fresh shell (or open a new Ghostty tab):

```fish
exec fish
```

Do **not** blindly pop the uninstall stash: it includes deletions of paths that
now contain the native prompt. Keep it until you have verified the migration;
recover any genuinely unrelated edits selectively. `git stash` does not restore
ignored `fish_variables`, so Fisher's uninstall registration remains removed.
The brief restoration of tracked files is not a Fisher reinstall.

The tracked manifest contained only Tide, so this change leaves `fish_plugins`
empty rather than inventing a new plugin list. Preserve any other locally
installed plugins by regenerating that manifest from the actual Fisher state
in the fresh Fish session:

```fish
fisher list > "$__fish_config_dir/fish_plugins"
```

Review that manifest before any later `fisher update`. Other plugin files are
preserved by the PR. Do not rerun `install` or copy the downloaded package over
this checkout; the existing symlink already makes the new files live.

## Appearance and behavior

The baseline was the repository's saved Tide-variable snapshot, not a read of
your currently running shell. Its effective left items were `os pwd git
character`; effective right items were `status cmd_duration context jobs node
python java ruby go kubectl aws time`.

- One line, no frame, extra blank line, or transient collapse. Apple and
  directory/home/lock glyphs retain the saved code points.
- Blue directories (`0087AF`), bold cyan project anchors (`00AFFF`), muted
  abbreviated components (`8787AF`); native path shortening keeps anchors and
  the last two components readable.
- Native informative Git state/counts with the saved symbols/colors, upstream
  information, and branch shortening configured to 24 characters.
- A fixed `❯`, green for success and red for failure. Detailed pipeline/signal
  status remains on the right even when only an earlier pipeline stage failed.
- Duration only above 3000 ms, SSH/root context, background jobs, conditional
  language/cloud context, and the `%r` AM/PM clock.

Edit `conf.d/native-prompt.fish` for context selection, thresholds, clock format,
Git options, and cursor shapes. The default language/cloud items match the
snapshot's effective list. Optional adapters are `zig rustc php crystal elixir`.
For example, append `zig` to `native_prompt_context_items` for Zig projects.

Fish still provides vi editing via the existing `fish_vi_key_bindings` call.
Ghostty displays Fish's line (insert), block (normal/visual), and underscore
(replace) cursor. There is no additional textual mode indicator or custom
mode-switching hook. Keep Ghostty shell integration enabled; no Ghostty change
is part of this PR. Native configuration also restores
`VIRTUAL_ENV_DISABLE_PROMPT`, which Tide removes on uninstall, so activating a
Python virtualenv does not wrap the left prompt a second time.

## Intentional native differences

Git ordering, detached-HEAD descriptions, operation labels, counting semantics,
and truncation belong to `fish_git_prompt`, not a copy of Tide's parser.
`prompt_pwd` shortening is not Tide's shortest-unique-prefix algorithm. Long
anchors can exceed the requested budget; Fish manages wrapping and right-prompt
visibility. The clock refreshes with the prompt, not continuously.

Rendering is synchronous: Git enumeration and applicable runtime/Kubernetes
queries may add latency. No workers, universal-variable cache, or persistent
prompt state is introduced. Per-repository Git prompt overrides still apply;
`git config --local bash.showInformativeStatus false` reduces count detail for a
particularly slow repository. This is not a claim that native rendering is
faster than Tide.

Python project detection checks the current directory unless a virtualenv is
active; other language markers are searched in ancestors, matching the saved
modules. Dormant Tide integrations such as gcloud, Terraform, and direnv are not
silently reimplemented or enabled.

## Verification

From the repository root:

```sh
uv run --no-project scripts/test_native_fish_prompt.py
```

The standard-library test suite requires Fish and Git and uses temporary HOME,
XDG directories, repositories, worktrees, and runtime fixtures. It never
sources your live `config.fish` or edits your actual universal variables. It
checks syntax, status colors, fixed mode-independent chevrons, pipeline
failures, duration boundaries, worktree/Git state, conditional runtime context,
real Python virtualenv activation, path anchors, control-character escaping,
and noninteractive startup silence. A path-scoped macOS CI workflow runs it.

Before accepting visual parity, check a fresh Ghostty tab: home, a repository
and linked worktree, `false | true`, `sleep 4`, vi mode changes, and narrow/wide
windows. Automated output checks do not validate actual Ghostty rendering or
font glyph availability. See the PR's current check results for executed
validation; the original downloadable package was not runtime-tested.

## Removed files and sensitive state

The PR removes Tide's tracked functions, configuration wizard, startup hook,
completion, plugin-manifest entry, and the two obsolete tracked `fishd.tmp.*`
files. It does not erase live universal variables or other plugins. Existing
`.gitignore` rules already exclude Fish variable snapshots.

One old snapshot contained credential-like values. Removing it from the current
tree does not remove it from Git history or revoke credentials. Rotate/revoke
any still-valid values separately; never publish the private backup above.
