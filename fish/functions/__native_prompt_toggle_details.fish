function __native_prompt_toggle_details --description 'Toggle runtime versions and the prompt clock'
    if test "$native_prompt_show_details" = 0
        set -g native_prompt_show_details 1
    else
        set -g native_prompt_show_details 0
    end
    commandline --function repaint
end
