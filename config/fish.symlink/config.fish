fish_add_path /usr/local/sbin
fish_add_path /opt/homebrew/bin
fish_add_path /opt/homebrew/sbin
direnv hook fish | source
zoxide init fish | source

if status is-login
  ssh-add >/dev/null 2>&1
end

# VI Prompt
fish_vi_key_bindings

# Prompt color scheme
set -g hydro_symbol_prompt '❯'
set -g hydro_symbol_git_dirty '*'
set -g hydro_symbol_git_ahead '⇡'
set -g hydro_symbol_git_behind '⇣'
set -g hydro_color_pwd brblue
set -g hydro_color_git ffafd7 --bold
set -g hydro_color_error brred --bold
set -g hydro_color_prompt brgreen
set -g hydro_color_duration bryellow --bold

# Abbreviations
abbr --add dotdot --regex '^\.\.+$' --function multicd
abbr -a -g bks 'cd ~/Library/Mobile\ Documents/iCloud\~com\~apple\~iBooks/Documents'
abbr -a -g gti 'git'
