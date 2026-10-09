# Native Fish prompt. No plugin manager or background renderer required.
status is-interactive; or return

# config.fish already enables fish_vi_key_bindings. Fish owns editing modes;
# Ghostty renders these cursor shapes. The prompt has no textual mode indicator.
set -g fish_cursor_default block
set -g fish_cursor_insert line
set -g fish_cursor_replace_one underscore
set -g fish_cursor_replace underscore
set -g fish_cursor_visual block

# Saved Tide context items, with Zig and Rust version reporting enabled.
# Optional additional supported items: php crystal elixir.
set -g native_prompt_context_items node python rustc java ruby go zig kubectl aws
set -g native_prompt_duration_threshold 3000
set -g native_prompt_time_format '%r'
set -g native_prompt_min_input_columns 34
set -g fish_transient_prompt 0
# Tide removes this on uninstall; keep virtualenv from wrapping our prompt.
set -gx VIRTUAL_ENV_DISABLE_PROMPT 1

# Public configuration of Fish's shipped Git prompt, not a custom Git parser.
set -g __fish_git_prompt_show_informative_status true
set -g __fish_git_prompt_showdirtystate true
set -g __fish_git_prompt_showuntrackedfiles true
set -g __fish_git_prompt_showstashstate true
set -g __fish_git_prompt_showupstream informative
set -g __fish_git_prompt_shorten_branch_len 24
set -g __fish_git_prompt_showcolorhints true
set -g __fish_git_prompt_char_stateseparator ''
set -g __fish_git_prompt_char_cleanstate ''
set -g __fish_git_prompt_char_dirtystate ' !'
set -g __fish_git_prompt_char_stagedstate ' +'
set -g __fish_git_prompt_char_invalidstate ' ~'
set -g __fish_git_prompt_char_untrackedfiles ' ?'
set -g __fish_git_prompt_char_stashstate ' *'
set -g __fish_git_prompt_char_upstream_ahead ' ⇡'
set -g __fish_git_prompt_char_upstream_behind ' ⇣'
set -g __fish_git_prompt_char_upstream_prefix ''
set -g __fish_git_prompt_color_branch 5FD700
set -g __fish_git_prompt_color_branch_dirty 5FD700
set -g __fish_git_prompt_color_branch_staged 5FD700
set -g __fish_git_prompt_color_branch_detached 5FD700
set -g __fish_git_prompt_color_merging FF0000
set -g __fish_git_prompt_color_dirtystate D7AF00
set -g __fish_git_prompt_color_stagedstate D7AF00
set -g __fish_git_prompt_color_invalidstate FF0000
set -g __fish_git_prompt_color_untrackedfiles 00AFFF
set -g __fish_git_prompt_color_stashstate 5FD700
set -g __fish_git_prompt_color_upstream 5FD700
