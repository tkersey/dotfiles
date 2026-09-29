function fish_right_prompt --description 'Status, duration, context, and clock'
    # Capture both simultaneously: subsequent commands can change $status.
    set -l previous $status $pipestatus
    set -l last_status $previous[1]
    set -l pipeline_status $previous[2..-1]
    set -q pipeline_status[1]; or set pipeline_status $last_status

    # Like the saved prompt, simple exit 1 is represented by the red chevron.
    # An earlier pipeline failure remains visible even when its last stage succeeds.
    if string match --quiet --invert 0 -- $pipeline_status
        if test (count $pipeline_status) -ne 1; or test "$pipeline_status[1]" != 1
            set -l summary (fish_status_to_signal $pipeline_status | string replace SIG '' | string join '|')
            if test $last_status -eq 0
                __native_prompt_segment 5FAF00 "✔ $summary"
            else
                __native_prompt_segment D70000 "✘ $summary"
            end
        end
    end

    set -l threshold 3000
    set -q native_prompt_duration_threshold[1]; and set threshold $native_prompt_duration_threshold
    if set -q CMD_DURATION[1]; and test "$CMD_DURATION" -gt $threshold
        set -l seconds (math --scale=0 "$CMD_DURATION / 1000")
        set -l hours (math --scale=0 "$seconds / 3600")
        set -l minutes (math --scale=0 "$seconds / 60 % 60")
        set seconds (math "$seconds % 60")
        set -l elapsed "$seconds"s
        test $minutes -gt 0; and set elapsed "$minutes"m" $elapsed"
        if test $hours -gt 0
            set elapsed "$hours"h" $minutes"m" $seconds"s
        end
        __native_prompt_segment 87875F " $elapsed"
    end

    set -l context_color ''
    if set -q SSH_TTY; or set -q SSH_CONNECTION
        set context_color D7AF87
    else if fish_is_root_user
        set context_color D7AF00
    end
    if test -n "$context_color"
        set -l host (string split --max=1 . -- "$hostname")[1]
        __native_prompt_segment $context_color "$USER@$host"
    end
    if jobs --query
        set -l job_count (jobs --pid | count)
        if test $job_count -ge 1000
            __native_prompt_segment 5FAF00 " $job_count"
        else
            __native_prompt_segment 5FAF00 ''
        end
    end

    # Compute ancestor paths once; no persistent cache or PWD event hooks.
    set -l parents "$PWD"
    set -l dir "$PWD"
    while test "$dir" != /
        set dir (path dirname -- "$dir")
        set --append parents "$dir"
    end
    for item in $native_prompt_context_items
        __native_prompt_context $item $parents
    end

    set -l time_format '%r'
    set -q native_prompt_time_format[1]; and set time_format "$native_prompt_time_format"
    __native_prompt_segment 5F8787 (command date "+$time_format")
end
