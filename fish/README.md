# Native Fish prompt

A single-line replacement for the effective saved Tide setup, using Fish's
`fish_prompt`, `fish_right_prompt`, `fish_git_prompt`, `prompt_pwd`, and builtins.
No Tide, Starship, plugin manager, or new runtime dependency is required.
Use Fish 4.1 or newer for native transient rendering.

## Install and update

`links.conf` symlinks this entire directory to `~/.config/fish`. The repository's
normal installer establishes that link; Fish loads the prompt functions and
`conf.d/native-prompt.fish` directly. There is no plugin installation or manifest
to maintain.

Once the native prompt is installed, update from a clean dotfiles checkout on
`main` and start a fresh Fish session:

```fish
git pull --ff-only
exec fish
```

No prompt-specific uninstall, installer rerun, manual file copy, or migration
stash is needed for this cleanup. Save unrelated local edits before updating.
The native prompt, vi bindings, Ghostty configuration, and unrelated custom
functions are unchanged. Ignored local `fish_variables` is not deleted or edited;
removing tracked files does not uninstall locally installed Homebrew formulae.

For an older installation that still runs Tide, follow the original migration
in [PR #315](https://github.com/tkersey/dotfiles/pull/315) before updating. Do not
repeat that uninstall against an already-installed native prompt.

## Appearance and behavior

The baseline was the repository's saved Tide-variable snapshot, not a read of
your currently running shell. Its effective left items were `os pwd git
character`; effective right items were `status cmd_duration context jobs node
python java ruby go kubectl aws time`.

- One line, no frame or extra blank line. Apple and directory/home/lock glyphs
  retain the saved code points. After a command is accepted, Fish replaces its
  prompt with a compact path, cached Git state, identity/failures, and chevron;
  the right prompt disappears from scrollback.
- Blue directories (`0087AF`), bold cyan project anchors (`00AFFF`), muted
  abbreviated components (`8787AF`); native path shortening keeps anchors and
  the last two components readable.
- Native informative Git state/counts with the saved symbols/colors, upstream
  information, and full branch names. Detached HEAD
  uses amber (`D7AF00`) instead of the branch's green.
- A fixed `❯`, green for success and red for failure. Detailed pipeline/signal
  status and SSH/root identity stay on the left, including in narrow windows.
- The right side admits whole segments in priority order: Kubernetes/AWS context,
  background jobs, duration above 3000 ms, language versions, then the `%r` AM/PM
  clock. It reserves 34 columns for input. Fish hides the right prompt when the
  command line needs more room.
- **Ctrl+Alt+P** toggles language versions and the clock for the current session,
  preserving cloud context, jobs, duration, and the last command's status. The
  binding works in vi insert, normal, and visual modes.

Edit `conf.d/native-prompt.fish` for context selection, thresholds, clock format,
Git options, and cursor shapes. The default language/cloud items include the
snapshot's effective list plus Zig and Rust. Versions appear in directories with
a `build.zig` or `Cargo.toml` file, respectively, and their descendants.
Optional adapters are `php crystal elixir`.

Git and runtime/cloud details load asynchronously. A dim `…` marks a pending
snapshot; `?` means collection failed or exceeded the five-second deadline.
The next command retries. Repainting preserves the command being typed and its
cursor, plus the previous command's status, pipeline result, and duration.
Changing directories or starting a command cancels the old collection, so a
late result cannot appear in a different directory or replace a newer result.

To disable individual features in `conf.d/native-prompt.fish`, set
`fish_transient_prompt` to `0`, `native_prompt_show_details` to `0`, or
`native_prompt_async` to `0`. The last option restores synchronous collection
for troubleshooting. `native_prompt_async_timeout_seconds` controls the
positive, whole-second collection deadline.

Fish still provides vi editing via the existing `fish_vi_key_bindings` call.
Ghostty displays Fish's line (insert), block (normal/visual), and underscore
(replace) cursor. There is no additional textual mode indicator or custom
mode-switching hook. Keep Ghostty shell integration enabled; no extra Ghostty
configuration is required. Native configuration also sets
`VIRTUAL_ENV_DISABLE_PROMPT`, which Tide removes on uninstall, so activating a
Python virtualenv does not wrap the left prompt a second time.

## Intentional native differences

Git ordering, detached-HEAD descriptions, operation labels, counting semantics,
and truncation belong to `fish_git_prompt`, not a copy of Tide's parser.
`prompt_pwd` shortening is not Tide's shortest-unique-prefix algorithm. Long
anchors can exceed the requested budget; Fish manages wrapping and right-prompt
visibility. The clock refreshes with the prompt, not continuously.

Interactive readers use one background Fish collector and a small system-shell
supervisor that isolates cancellation from the interactive shell's jobs. The
collector calls the same native Git prompt and runtime adapters. Each shell owns
one private temporary directory, removes completed/cancelled requests, and
removes that directory on exit. There is no universal-variable cache or
persistent prompt state. Noninteractive/direct rendering stays synchronous.
Per-repository Git prompt overrides still apply;
`git config --local bash.showInformativeStatus false` reduces count detail for a
particularly slow repository. Async collection improves input readiness; full
details may arrive later because worker startup and repaint add overhead.

Python project detection checks the current directory unless a virtualenv is
active; other language markers are searched in ancestors, matching the saved
modules. Dormant Tide integrations such as gcloud, Terraform, and direnv are not
silently reimplemented or enabled.

## Verification

From the repository root:

```sh
uv run --no-project scripts/test_native_fish_prompt.py
```

The standard-library test suite requires Fish, Git, and `hub` (already in the
Brewfile for the existing `git` wrapper). It uses temporary HOME,
XDG directories, repositories, worktrees, and runtime fixtures. It never
sources your live `config.fish` or edits your actual universal variables. It
checks syntax, status colors, fixed mode-independent chevrons, pipeline
failures, duration boundaries, worktree/Git state, detached-HEAD color,
conditional runtime context, real Python virtualenv activation, path anchors,
control-character escaping, transient rendering, narrow-window priorities,
detail toggling, and noninteractive startup silence. Real pseudo-terminal tests
also cover typing during collection, repaint/status preservation, directory
invalidation, timeout recovery, and worker/file cleanup, including a runtime that
ignores termination signals.

Before accepting visual parity, check a fresh Ghostty tab: home, a repository
and linked worktree, `false | true`, `sleep 4`, vi mode changes, and narrow/wide
windows. Automated output checks do not validate actual Ghostty rendering or
font glyph availability.

## Removed files and sensitive state

The old Tide implementation and obsolete tracked `fishd.tmp.*` snapshots have
been removed. Repository cleanup does not erase live universal variables or
unrelated custom functions. Existing `.gitignore` rules exclude Fish variable
snapshots.

One old snapshot contained credential-like values. Removing it from the current
tree does not remove it from Git history or revoke credentials. Rotate/revoke
any still-valid values separately; never publish private configuration backups.
