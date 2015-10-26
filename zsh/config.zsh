# completions
fpath=($ZSH/zsh/functions $fpath)
autoload -U $ZSH/zsh/functions/*(:t)

# history
HISTFILE=~/.zsh_history
HISTSIZE=10000
SAVEHIST=10000

# vim mode
bindkey -v

# ssh-agent
SSHAGENT=/usr/bin/ssh-agent
SSHAGENTARGS="-s"
if [ -z "$SSH_AUTH_SOCK" -a -x "$SSHAGENT" ]; then
eval `$SSHAGENT $SSHAGENTARGS` > /dev/null
  trap "kill $SSH_AGENT_PID" 0
fi

setopt no_kshglob
