function __native_prompt_collect --description 'Collect one native prompt snapshot as NUL-separated text'
    # Keep Fish's Git semantics and the existing runtime adapters as the only
    # producers. Empty fields preserve the correspondence with context_items.
    printf '%s\0' (fish_git_prompt '%s' | string collect)

    set -l parents "$PWD"
    set -l directory "$PWD"
    while test "$directory" != /
        set directory (path dirname -- "$directory")
        set --append parents "$directory"
    end
    for item in $native_prompt_context_items
        set -l segment (__native_prompt_context $item $parents | string collect)
        printf '%s\0' "$segment"
    end
end
