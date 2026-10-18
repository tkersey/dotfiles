# Ghostty

The installer links `ghostty/config` to
`~/Library/Application Support/com.mitchellh.ghostty/config`. Edit the repository
file to change the installed configuration. The existing filename remains
supported; this change does not move it or add another configuration layer.

## Themes

Rosé Pine Moon is still the selected built-in theme:

```ini
theme = Rose Pine Moon
```

Only the unused `theme.rose-pine` fragment was removed. It repeated this assignment
and was never included by the main configuration. Theme support is unchanged.

Browse and preview installed themes:

```fish
/Applications/Ghostty.app/Contents/MacOS/ghostty +list-themes
```

Use `/` to search, arrows to preview, and Enter to view the theme's configuration
line. Replace the existing `theme = ...` line in `ghostty/config` with that line,
then press **Cmd+Shift+,** in Ghostty to reload. This keeps the choice in dotfiles;
there is no need to save a separate auto-theme file or add a `config-file` include.

For automatic switching with macOS appearance, replace the single-theme line
with:

```ini
theme = light:Rose Pine Dawn,dark:Rose Pine Moon
```

Custom color files are also supported: set `theme` to the file's absolute path.
See [Ghostty's theme documentation](https://ghostty.org/docs/features/theme).

## Agent sessions

| Action | Shortcut or behavior |
| --- | --- |
| Insert a multiline prompt | Native Shift+Enter in current Fish, Codex, and Claude Code |
| Split right | Cmd+D or the retained Cmd+Shift+H alias |
| Split down | Cmd+Shift+D |
| Equalize splits | Cmd+Control+= or the retained Cmd+Shift+E alias |
| Move between splits | Cmd+Option+arrows or Cmd+[ / Cmd+] |
| Zoom a split | Cmd+Shift+Enter; navigating to another split keeps it zoomed |
| Search scrollback | Cmd+F, then Cmd+G / Cmd+Shift+G |
| Jump between shell prompts | Cmd+Shift+Up / Cmd+Shift+Down |
| Name a project/worktree tab | Cmd+Shift+P, then Change Tab Title |
| Export scrollback | Cmd+Shift+P, then Copy scrollback path |

The global Shift+Enter-to-Ctrl+J workaround is removed so applications receive the
original key event. Verify your installed clients, including any tmux or SSH path
you actually use. The custom Cmd+Shift+V split binding is also removed, restoring
Ghostty's default Paste Selection shortcut. Its contents depend on the selection
clipboard and the installed version; ordinary Cmd+V paste is unchanged.

Inactive splits retain 80% opacity to make adjacent agents readable. Fish continues
to own vi cursor shapes through its native configuration. Ghostty's automatic
shell integration and working-directory inheritance remain enabled.

Commands that run at least 30 seconds and finish in an unfocused terminal request
a desktop notification without a bell. macOS must allow Ghostty notifications.
This detects shell-command completion: an interactive agent's turn finishing is
different from its process exiting. Use the agent's own notifications for turns
and permission requests. Prompt navigation likewise follows shell commands, not
individual agent turns.

The export action creates a temporary text snapshot and copies its path. Open that
path in Micro from another shell or attach the snapshot where needed. Ghostty's
`write_scrollback_file:open` action uses the macOS default text application rather
than `$EDITOR`. Copy a snapshot elsewhere if it must be retained permanently.

## Memory and updates

`scrollback-limit = 10000000` sets a 10 MB logical allowance per terminal surface,
allocated lazily. It is not a cap on total Ghostty memory. This preserves the
stable 1.3.1 allowance while avoiding dependence on changing tip defaults. Current
development builds accept this spelling as an alias for `scrollback-limit-bytes`;
leave their default scrollback compression enabled. The allowance applies to new
surfaces. Raise it deliberately if useful history is being discarded, and use
agent transcripts for durable history.

The Brewfile installs `ghostty@tip`, matching `auto-update-channel = tip`.
`auto-update = check` checks for updates without automatically downloading them.
Install updates between sessions and record the actual app version when comparing
behavior. The channel alone does not prove which build is running.

VSync, the embedded font, background rendering, clipboard protections, image
storage, and shell integration retain their defaults. The removed quick-terminal
animation setting had outlived the shortcut that opened that terminal.

## One-time migration

### Existing stable Homebrew cask

The stable and tip casks conflict. If `brew list --cask ghostty` reports the
stable cask installed, finish your terminal sessions and quit Ghostty. From
Terminal.app or another terminal, run:

```sh
brew uninstall --cask ghostty
brew install --cask ghostty@tip
```

Use normal uninstall, without `--zap`, to retain Ghostty configuration and
preferences. Do this before the next `brew bundle` or full `./install`. Fresh
installs and existing `ghostty@tip` installations do not need this migration.
See the [tip cask](https://formulae.brew.sh/cask/ghostty@tip).

### Retire the unused theme link

After updating, run this in Fish from the dotfiles repository root:

```fish
begin
    set -l ghostty_dotfiles_root (pwd -P)
    set -l ghostty_old_theme "$HOME/Library/Application Support/com.mitchellh.ghostty/theme.rose-pine"
    if test -L "$ghostty_old_theme"
        set -l ghostty_old_target (readlink "$ghostty_old_theme")
        if test "$ghostty_old_target" = "$ghostty_dotfiles_root/ghostty/theme.rose-pine"
            command rm -- "$ghostty_old_theme"
        end
    end
end
```

This removes only a symlink with the exact expected target, including a dangling
link. Ordinary files and other targets are preserved. If the checkout was
installed through a different logical path, inspect the link manually. The normal
installer creates listed mappings but does not retire removed mappings.

## Local validation

Run against the installed app:

```fish
/Applications/Ghostty.app/Contents/MacOS/ghostty +version
/Applications/Ghostty.app/Contents/MacOS/ghostty +validate-config
/Applications/Ghostty.app/Contents/MacOS/ghostty +show-config --changes-only=false
/Applications/Ghostty.app/Contents/MacOS/ghostty +list-keybinds --plain
```

To validate this repository file in isolation, run from the repository root:

```fish
/Applications/Ghostty.app/Contents/MacOS/ghostty +validate-config --config-file=ghostty/config
```

The effective configuration can also include XDG files and a local
`config.ghostty`. Inspect it if a repository change appears ineffective.
Use `+show-config --default --docs` for the installed build's option documentation.

Reload, then use new surfaces for checks that affect newly created terminals.
Check Shift+Enter in Fish and your agent clients, vi cursor shapes, zoomed split
navigation, inherited working directories, theme selection, and a command such as
`sleep 31` while another terminal is focused. Verify scrollback export through the
command palette. These checks require the actual Mac; source inspection does not
establish a measured performance improvement.

## Optional direct-Fish startup experiment

For an Apple Silicon Homebrew installation, first verify
`/opt/homebrew/bin/fish --version`, then temporarily add:

```ini
command = direct:/opt/homebrew/bin/fish --login
```

This skips Ghostty's intermediate Bash invocation while retaining macOS
`login` handling. Keep `--login`: this repository loads SSH keys from Fish's
login-only startup block. Shell integration still detects Fish. The explicit path
also fixes Ghostty to Fish rather than following future system-shell changes.

This is an unmeasured experiment, not an enabled default. Compare repeated fresh
tabs with the same directory and environment, checking login status, command
paths, cursor shapes, and working-directory inheritance. Remove the line to
restore default shell selection. Keep it only if the result justifies it.
The relevant mechanism is in
[Ghostty's macOS command execution](https://github.com/ghostty-org/ghostty/blob/v1.3.1/src/termio/Exec.zig).

Profile Fish startup separately from prompt generation:

```fish
/opt/homebrew/bin/fish --login --interactive --profile-startup /tmp/ghostty-fish-startup.prof --command exit
sort -nk2 /tmp/ghostty-fish-startup.prof

/opt/homebrew/bin/fish --login --interactive --profile /tmp/ghostty-fish-prompt.prof --command 'fish_prompt; fish_right_prompt' >/dev/null
sort -nk2 /tmp/ghostty-fish-prompt.prof
```

Run the prompt profile from home and a representative repository. These commands
measure shell work, not Ghostty first paint or GPU latency. Runtime-version, Git,
and Kubernetes context queries can dominate a synchronous prompt. No additional
benchmark framework or fixture suite is required.
