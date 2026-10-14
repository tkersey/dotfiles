function fish_prompt --description 'Single-line native Fish prompt'
    # Capture both together before any command can replace the pipeline result.
    set -l command_result $status $pipestatus
    set -l command_duration "$CMD_DURATION"
    set -l final_rendering 0
    contains -- --final-rendering $argv; and set final_rendering 1
    if test $final_rendering -eq 0
        __native_prompt_refresh
        # An async repaint is still the same command result, not a new command.
        if test "$__native_prompt_async_active" != 1; or test "$__native_prompt_render_generation" != "$__native_prompt_generation"
            set -g __native_prompt_last_status $command_result[1]
            set -g __native_prompt_last_pipestatus $command_result[2..-1]
            set -g __native_prompt_last_duration "$command_duration"
            set -g __native_prompt_render_generation "$__native_prompt_generation"
        end
    end
    set -l last_status $command_result[1]
    set -q __native_prompt_last_status[1]; and set last_status $__native_prompt_last_status
    set -l pipeline_status $__native_prompt_last_pipestatus
    set -q pipeline_status[1]; or set pipeline_status $last_status

    # These are consequential even in a narrow split, so keep them on the left.
    set -l critical
    set -l identity_color ''
    if set -q SSH_TTY; or set -q SSH_CONNECTION
        set identity_color D7AF87
    else if fish_is_root_user
        set identity_color D7AF00
    end
    if test -n "$identity_color"
        set -l host (string split --max=1 . -- "$hostname")[1]
        set --append critical (__native_prompt_segment $identity_color "$USER@$host" | string collect)
    end
    if string match --quiet --invert 0 -- $pipeline_status
        # A simple exit 1 is already represented by the red chevron.
        if test (count $pipeline_status) -ne 1; or test "$pipeline_status[1]" != 1
            set -l summary (fish_status_to_signal $pipeline_status | string replace SIG '' | string join '|')
            if test $last_status -eq 0
                set --append critical (__native_prompt_segment 5FAF00 "✔ $summary" | string collect)
            else
                set --append critical (__native_prompt_segment D70000 "✘ $summary" | string collect)
            end
        end
    end
    set -l critical_text (string join '' -- $critical)
    set -l git_prompt "$__native_prompt_git"
    if test "$__native_prompt_pending" = 1
        set git_prompt (set_color 8787AF)'…'(set_color normal)
    else if test "$__native_prompt_unavailable" = 1
        set git_prompt (set_color 8787AF)'?'(set_color normal)
    end
    set -l columns 80
    set -q COLUMNS[1]; and set columns $COLUMNS
    set -l reserve 34
    set -q native_prompt_min_input_columns[1]; and set reserve $native_prompt_min_input_columns
    set -l git_width (string length --visible -- "$git_prompt")
    set -l critical_width (string length --visible -- "$critical_text")
    set -l budget (math "max(8, $columns - $reserve - 8 - $git_width - $critical_width)")

    set -l rendered (begin
        set_color normal
        if test $final_rendering -eq 1
            # Final rendering uses only the existing snapshot and a cheap path.
            set_color 0087AF
            set -l compact_path (prompt_pwd --dir-length=1 --full-length-dirs=1 | string collect)
            set compact_path (string replace --all --regex '[\x00-\x1f\x7f-\x9f]' '?' -- "$compact_path")
            printf '%s' "$compact_path"
        else
            printf '\uf179 '
            __native_prompt_pwd $budget
        end
        if test -n "$git_prompt"
            set_color 5FD700
            if test $final_rendering -eq 1; or test "$__native_prompt_pending" = 1; or test "$__native_prompt_unavailable" = 1
                printf ' %s' "$git_prompt"
            else
                printf ' \uf1d3 %s' "$git_prompt"
            end
        end
        printf '%s' "$critical_text"
        set_color normal
        if test $last_status -eq 0
            set_color 5FD700
        else
            set_color FF0000
        end
        # Fish's cursor, not this fixed character, identifies vi mode.
        printf ' ❯ '
        set_color normal
    end | string collect)
    # The right prompt budgets against what was actually displayed on the left.
    set -g __native_prompt_left_width (string length --visible -- "$rendered")
    printf '%s' "$rendered"
end
