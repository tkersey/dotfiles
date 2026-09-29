function __native_prompt_pwd --description 'Native path shortening with saved prompt colors'
    set -l full (prompt_pwd --dir-length=0 | string collect)
    set -l shown "$full"
    if test (string length --visible -- "$full") -gt $argv[1]
        set shown (prompt_pwd --dir-length=1 --full-length-dirs=2 | string collect)
    end
    set -l original (string split / -- "$full")
    set -l shortened (string split / -- "$shown")
    set -l markers .bzr .citc .git .hg .node-version .python-version .ruby-version \
        .shorten_folder_marker .svn .terraform Cargo.toml composer.json CVS \
        go.mod package.json build.zig
    set -l absolute ''
    set -l index 0

    set_color 0087AF
    if not test -w .
        printf '\uf023 '
    else if test "$PWD" = "$HOME"
        printf '\uf015 '
    else
        printf '\uf07c '
    end

    for part in $original
        set index (math $index + 1)
        if test $index -eq 1; and test "$part" = '~'
            set absolute "$HOME"
        else if test "$absolute" = /
            set absolute "/$part"
        else
            set absolute "$absolute/$part"
        end
        set -l anchor false
        if test $index -eq (count $original)
            set anchor true
        else
            for marker in $markers
                if test -e "$absolute/$marker"
                    set anchor true
                    break
                end
            end
        end
        if test $index -gt 1
            set_color normal
            set_color 0087AF
            printf /
        end
        set -l segment "$shortened[$index]"
        set_color normal
        if test "$anchor" = true
            # Keep repository/project roots and the final component readable.
            set segment "$part"
            set_color --bold 00AFFF
        else if test "$segment" != "$part"
            set_color 8787AF
        else
            set_color 0087AF
        end
        # A directory name must not inject terminal control characters.
        set segment (string replace --all --regex '[\x00-\x1f\x7f-\x9f]' '?' -- "$segment")
        printf '%s' "$segment"
    end
    set_color normal
end
