source /usr/local/share/chruby/chruby.fish
source /usr/local/share/chruby/auto.fish

fish_add_path /usr/local/sbin

# ssh agent
if test -f ~/.ssh/id_ed25519
  killer ssh-agent > /dev/null 2>&1
  eval (ssh-agent -c) > /dev/null 2>&1
  ssh-add ~/.ssh/id_ed25519 > /dev/null 2>&1
end

direnv hook fish | source
