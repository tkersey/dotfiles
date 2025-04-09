fish_add_path /usr/local/sbin
fish_add_path /opt/homebrew/bin
fish_add_path /opt/homebrew/sbin
direnv hook fish | source
fzf --fish | source
zoxide init fish | source
source (goenv init - | psub)

if status is-login
    ssh-add >/dev/null 2>&1
end

# VI Prompt
fish_vi_key_bindings

# Abbreviations
abbr --add dotdot --regex '^\.\.+$' --function multicd
abbr -a -g bks 'cd ~/Library/Mobile\ Documents/iCloud\~com\~apple\~iBooks/Documents'
abbr -a -g gti git
