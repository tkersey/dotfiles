#!/bin/sh
# The prompt itself is Fish. This system-shell launcher only isolates process
# groups: Fish children started inside fish_prompt can share the reader's group.
# Monitor mode gives the collector and its deadline separate groups, so stopping
# an obsolete request never signals the interactive shell or its foreground job.
directory=$1
generation=$2
parent=$3
deadline=$4
shift 4

notify() {
    if test -d "$directory"; then
        : > "$directory/done.$generation"
        kill -USR1 "$parent" 2>/dev/null
    fi
}
set -m
case $- in
    *m*) ;;
    *) notify; exit 1 ;; # Do not attempt group cancellation without isolation.
esac
collector=
timer=
stop() {
    trap - EXIT HUP INT TERM
    # $! covers a signal arriving between launching a child and assigning its PID.
    for pid in "$collector" "$timer" "$!"; do
        if test -n "$pid"; then
            # Read-only collectors are disposable. KILL also stops descendants
            # that ignore TERM, even if their Fish group leader already exited.
            kill -KILL -- "-$pid" 2>/dev/null
            wait "$pid" 2>/dev/null
        fi
    done
}
trap 'stop; exit' HUP INT TERM
trap stop EXIT

"$@" &
collector=$!
(
    sleep "$deadline"
    kill -KILL -- "-$collector" 2>/dev/null
) &
timer=$!

wait "$collector" 2>/dev/null
# Cancel and reap the timer before reporting completion. The result was renamed
# atomically by Fish; a missing result means the collector failed or timed out.
kill -TERM -- "-$timer" 2>/dev/null
wait "$timer" 2>/dev/null
trap - EXIT HUP INT TERM
notify
