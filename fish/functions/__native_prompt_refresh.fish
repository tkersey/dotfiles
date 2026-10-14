function __native_prompt_refresh --description 'Refresh one directory-bound native prompt snapshot'
    set -q __native_prompt_generation; or set -g __native_prompt_generation 0
    set -g __native_prompt_async_active 0
    if test "$native_prompt_async" = 1; and status is-interactive; and isatty stdin
        set -g __native_prompt_async_active 1
    end

    if test $__native_prompt_async_active -eq 0
        __native_prompt_stop_worker
        set -l snapshot (__native_prompt_collect | string split0)
        set -g __native_prompt_git "$snapshot[1]"
        set -g __native_prompt_context_segments $snapshot[2..-1]
        set -g __native_prompt_snapshot_set 1
        set -g __native_prompt_pending 0
        set -g __native_prompt_unavailable 0
        return
    end

    set -g __native_prompt_at_prompt 1
    if test "$__native_prompt_request_pwd" = "$PWD"; and test "$__native_prompt_request_generation" = "$__native_prompt_generation"
        return
    end
    __native_prompt_stop_worker
    # A directory change in a key binding need not execute a command.
    if test "$__native_prompt_request_generation" = "$__native_prompt_generation"
        set -g __native_prompt_generation (math $__native_prompt_generation + 1)
    end
    set -g __native_prompt_request_generation $__native_prompt_generation
    set -g __native_prompt_request_pwd "$PWD"
    set -g __native_prompt_git ''
    set -g __native_prompt_context_segments
    set -g __native_prompt_snapshot_set 1
    set -g __native_prompt_pending 1
    set -g __native_prompt_unavailable 0

    if not set -q __native_prompt_directory
        set -l temporary_root /tmp
        if set -q TMPDIR[1]; and test -n "$TMPDIR"
            set temporary_root (string trim --right --chars=/ -- "$TMPDIR")
        end
        set -g __native_prompt_directory (command mktemp -d "$temporary_root/fish-prompt.XXXXXXXXXX")
        if not test -d "$__native_prompt_directory"
            set -e __native_prompt_directory
            set -g __native_prompt_pending 0
            set -g __native_prompt_unavailable 1
            return
        end
    end
    set -l generation $__native_prompt_generation
    set -l directory "$__native_prompt_directory/$generation"
    command mkdir -m 700 -- "$directory"; or begin
        set -g __native_prompt_pending 0
        set -g __native_prompt_unavailable 1
        return
    end
    set -g __native_prompt_request_directory "$directory"
    # Each request has its own file so a cancelled reader cannot see a successor's
    # script. Serialize only shell-owned settings; results are always plain data.
    begin
        for name in fish_function_path fish_term24bit fish_term256 native_prompt_context_items \
            VIRTUAL_ENV AWS_PROFILE AWS_DEFAULT_PROFILE AWS_REGION AWS_DEFAULT_REGION KUBECONFIG \
            (set --names | string match --regex '^__fish_git_prompt_(show.*|char_.*|color_.*|shorten_branch_len|describe_style|use_informative_chars)$')
            if set -q $name
                printf 'set -g %s' "$name"
                set -l values $$name
                if set -q values[1]
                    printf ' %s' (string escape -- $values)
                end
                printf '\n'
            end
        end
        printf 'cd -- %s; or exit 1\n' (string escape -- "$PWD")
        printf '__native_prompt_collect > "$argv[1]/result.$argv[2].tmp"\n'
        printf 'and command mv -f -- "$argv[1]/result.$argv[2].tmp" "$argv[1]/result.$argv[2]"\n'
    end >"$directory/request.$generation.fish"

    set -l deadline 5
    if string match --quiet --regex '^[1-9][0-9]*$' -- "$native_prompt_async_timeout_seconds"
        set deadline $native_prompt_async_timeout_seconds
    end
    set -l launcher (path resolve (status dirname)/../native-prompt-worker.sh)
    command sh "$launcher" "$directory" "$generation" "$fish_pid" "$deadline" \
        (status fish-path) --no-config "$directory/request.$generation.fish" "$directory" "$generation" </dev/null >/dev/null 2>&1 &
    set -g __native_prompt_worker_pid $last_pid
    disown $__native_prompt_worker_pid 2>/dev/null
end

function __native_prompt_stop_worker --description 'Cancel only the prompt-owned launcher'
    if set -q __native_prompt_worker_pid
        # The launcher traps TERM and stops its own isolated collector/deadline.
        command kill -TERM $__native_prompt_worker_pid 2>/dev/null
        set -e __native_prompt_worker_pid
    end
    if set -q __native_prompt_request_directory
        command rm -rf -- "$__native_prompt_request_directory"
        set -e __native_prompt_request_directory
    end
end

function __native_prompt_before_command --on-event fish_preexec
    set -g __native_prompt_at_prompt 0
    set -q __native_prompt_generation; or set -g __native_prompt_generation 0
    set -g __native_prompt_generation (math $__native_prompt_generation + 1)
    __native_prompt_stop_worker
end

function __native_prompt_cancelled --on-event fish_cancel
    __native_prompt_before_command
end

function __native_prompt_completed --on-signal USR1
    set -q __native_prompt_request_directory; or return
    set -l generation $__native_prompt_request_generation
    set -l directory "$__native_prompt_request_directory"
    test -f "$directory/done.$generation"; or return
    if test "$generation" != "$__native_prompt_generation"; or test "$__native_prompt_request_pwd" != "$PWD"; or test "$__native_prompt_at_prompt" != 1
        return
    end
    set -e __native_prompt_worker_pid
    set -g __native_prompt_pending 0
    set -g __native_prompt_unavailable 1
    if test -f "$directory/result.$generation"
        set -l snapshot (string split0 < "$directory/result.$generation")
        if test (count $snapshot) -eq (math 1 + (count $native_prompt_context_items))
            set -g __native_prompt_git "$snapshot[1]"
            set -g __native_prompt_context_segments $snapshot[2..-1]
            set -g __native_prompt_unavailable 0
        end
    end
    command rm -rf -- "$directory"
    set -e __native_prompt_request_directory
    commandline -f repaint
end

function __native_prompt_cleanup --on-event fish_exit
    set -g __native_prompt_at_prompt 0
    __native_prompt_stop_worker
    if set -q __native_prompt_directory
        command rm -rf -- "$__native_prompt_directory"
        set -e __native_prompt_directory
    end
end
