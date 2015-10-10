###########
# GENERAL #
###########
alias l='ls -lah' # l for list style, a for all including hidden, h for human readable file sizes
alias ..='cd ..' # move up 1 dir
alias ...='cd ../..' # move up 2 dirs
alias reload!='. ~/.zshrc'

########
# BREW #
########
alias b="brew"
alias bupo="brew up && brew outdated"

#######
# Git #
#######
alias gti=git
alias git=hub

###############
# DIRECTORIES #
###############
alias cdc="cd ~/Dropbox/code"
alias cdd="cd ~/downloads"

########
# MISC #
########
alias bkoff="cd ~/.bin/backup && git reset --hard origin/master && chmod 755 backup.sh && /bin/bash -l -c '~/.bin/backup/backup.sh'"
