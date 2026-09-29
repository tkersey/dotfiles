function __native_prompt_segment --argument-names color text --description 'Print one right-prompt item'
    test -n "$text"; or return
    # Treat names and command output as text, never terminal instructions.
    set text (string replace --all --regex '[\x00-\x1f\x7f-\x9f]' '?' -- "$text")
    set_color normal
    set_color $color
    printf ' %s' "$text"
    set_color normal
end
