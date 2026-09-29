function fish_prompt --description 'Single-line native Fish prompt'
    # Fish renders the right prompt after this function, so preserve the
    # command result before any left-prompt rendering command changes it.
    set -l last_status $status
    set -g __native_prompt_last_status $last_status
    set -g __native_prompt_last_pipestatus $pipestatus
    set -l git_prompt (fish_git_prompt '%s' | string collect)
    set -l columns 80
    set -q COLUMNS[1]; and set columns $COLUMNS
    set -l reserve 34
    set -q native_prompt_min_input_columns[1]; and set reserve $native_prompt_min_input_columns
    # Leave command-entry space; Fish manages right-prompt visibility itself.
    set -l git_width (string length --visible -- "$git_prompt")
    set -l budget (math "max(8, $columns - $reserve - 8 - $git_width)")

    set_color normal
    printf '\uf179 '
    __native_prompt_pwd $budget
    if test -n "$git_prompt"
        set_color 5FD700
        printf ' \uf1d3 %s' "$git_prompt"
    end
    set_color normal
    if test $last_status -eq 0
        set_color 5FD700
    else
        set_color FF0000
    end
    # Deliberately fixed: Fish's cursor, not this character, identifies vi mode.
    printf ' ❯ '
    set_color normal
end
