# Added by devenv/mac-dev-setup Sat Apr  3 18:11:18 EDT 2021
export PATH="${PATH}:/Users/tkersey/work/devenv/bin"
[ -f "/Users/tkersey/work/devenv/lib/eh_functions.sh" ] && . /Users/tkersey/work/devenv/lib/eh_functions.sh
export OCI_REGISTRY=689723035205.dkr.ecr.us-east-1.amazonaws.com
export AWS_ACCESS_KEY_ID=foo
export AWS_SECRET_ACCESS_KEY=bar
export AWS_DEFAULT_REGION=baz

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
alias git=hub
alias cdd='cd ~/Downloads'
alias cdw='cd ~/work'


[ -f ~/.fzf.zsh ] && source ~/.fzf.zsh
