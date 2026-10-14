function fish_right_prompt --description 'Space-aware context, jobs, duration, and optional details'
    contains -- --final-rendering $argv; and return
    if not set -q __native_prompt_snapshot_set
        __native_prompt_refresh
    end

    set -l columns 80
    set -q COLUMNS[1]; and set columns $COLUMNS
    set -l left_width 0
    set -q __native_prompt_left_width[1]; and set left_width $__native_prompt_left_width
    set -l reserve 34
    set -q native_prompt_min_input_columns[1]; and set reserve $native_prompt_min_input_columns
    set -l remaining (math "max(0, $columns - $left_width - $reserve - 1)")
    set -l candidates

    # Environment identity has priority over routine language versions.
    set -l index 0
    for item in $native_prompt_context_items
        set index (math $index + 1)
        if contains -- "$item" kubectl aws
            set --append candidates "$__native_prompt_context_segments[$index]"
        end
    end
    if jobs --query
        set -l job_count (jobs --pid | count)
        if test $job_count -ge 1000
            set --append candidates (__native_prompt_segment 5FAF00 " $job_count" | string collect)
        else
            set --append candidates (__native_prompt_segment 5FAF00 '' | string collect)
        end
    end

    set -l duration "$CMD_DURATION"
    set -q __native_prompt_last_duration[1]; and set duration "$__native_prompt_last_duration"
    set -l threshold 3000
    set -q native_prompt_duration_threshold[1]; and set threshold $native_prompt_duration_threshold
    if test -n "$duration"; and test "$duration" -gt $threshold
        set -l seconds (math --scale=0 "$duration / 1000")
        set -l hours (math --scale=0 "$seconds / 3600")
        set -l minutes (math --scale=0 "$seconds / 60 % 60")
        set seconds (math "$seconds % 60")
        set -l elapsed "$seconds"s
        test $minutes -gt 0; and set elapsed "$minutes"m" $elapsed"
        if test $hours -gt 0
            set elapsed "$hours"h" $minutes"m" $seconds"s
        end
        set --append candidates (__native_prompt_segment 87875F " $elapsed" | string collect)
    end

    if test "$native_prompt_show_details" != 0
        set index 0
        for item in $native_prompt_context_items
            set index (math $index + 1)
            if not contains -- "$item" kubectl aws
                set --append candidates "$__native_prompt_context_segments[$index]"
            end
        end
        set -l time_format '%r'
        set -q native_prompt_time_format[1]; and set time_format "$native_prompt_time_format"
        set --append candidates (__native_prompt_segment 5F8787 (command date "+$time_format") | string collect)
    end

    # Admit whole colored segments only; never slice an escape sequence or name.
    for segment in $candidates
        set -l width (string length --visible -- "$segment")
        if test $width -le $remaining
            printf '%s' "$segment"
            set remaining (math "$remaining - $width")
        end
    end
end
