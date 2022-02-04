fpath+=$HOME/.zsh/pure

autoload -U promptinit; promptinit
prompt pure

zstyle ':completion:*:*:git:*' script ~/.zsh/git-completion.bash
fpath=(~/.zsh $fpath)

autoload -Uz compinit && compinit

#### VIM
bindkey -v

######
alias l='ls -lah' # l for list style, a for all including hidden, h for human readable file sizes
alias ..='cd ..' # move up 1 dir
alias ...='cd ../..' # move up 2 dirs
alias ....='cd ../../..' # move up 3 dirs
alias .....='cd ../../../..' # move up 4 dirs
alias reload!='. ~/.zshrc'
alias gti=git
alias cdd='cd ~/Downloads'
alias cdw='cd ~/workspace'
alias dot='cd ~/.dotfiles'

eval "$(hub alias -s)"

[ -f ~/.fzf.zsh ] && source ~/.fzf.zsh

eval "$(direnv hook zsh)"
