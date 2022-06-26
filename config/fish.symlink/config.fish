fish_add_path /usr/local/sbin
direnv hook fish | source

if status is-login
  ssh-add
end
