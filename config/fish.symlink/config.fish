source /usr/local/share/chruby/chruby.fish
source /usr/local/share/chruby/auto.fish

if not pgrep -f ssh-agent > /dev/null
  eval (ssh-agent -c)
  set -Ux SSH_AUTH_SOCK $SSH_AUTH_SOCK
  set -Ux SSH_AGENT_PID $SSH_AGENT_PID
  set -Ux SSH_AUTH_SOCK $SSH_AUTH_SOCK
end

direnv hook fish | source
fish_add_path /usr/local/sbin
