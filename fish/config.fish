fish_add_path /usr/local/sbin
fish_add_path /opt/homebrew/bin
fish_add_path /opt/homebrew/sbin
fish_add_path ~/.local/bin

fzf --fish | source
zoxide init fish | source

if status is-login
    ssh-add >/dev/null 2>&1
end

# VI Prompt
fish_vi_key_bindings

# Abbreviations
abbr --add dotdot --regex '^\.\.+$' --function multicd
abbr -a -g bks 'cd ~/Library/Mobile\ Documents/iCloud\~com\~apple\~iBooks/Documents'
abbr -a -g gti git
abbr -a -g nvim-plugins '~/.local/share/nvim/lazy'

# Variables
set -gx EDITOR nvim

# goenv initialization
set -x GOENV_ROOT $HOME/.goenv
fish_add_path $GOENV_ROOT/bin
goenv init - | source
