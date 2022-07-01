fish_add_path /usr/local/sbin
direnv hook fish | source

if status is-login
  ssh-add >/dev/null 2>&1
end
