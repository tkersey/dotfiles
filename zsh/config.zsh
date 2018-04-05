# completions
fpath=($ZSH/zsh/functions $fpath)
autoload -U $ZSH/zsh/functions/*(:t)

# history
HISTFILE=~/.zsh_history
HISTSIZE=10000
SAVEHIST=10000

# vim mode
bindkey -v

setopt no_kshglob
