###########
# GENERAL #
###########
alias l='ls -lah' # l for list style, a for all including hidden, h for human readable file sizes
alias ..='cd ..' # move up 1 dir
alias ...='cd ../..' # move up 2 dirs
alias ....='cd ../../..' # move up 3 dirs
alias .....='cd ../../../..' # move up 4 dirs
alias reload!='. ~/.zshrc'

########
# BREW #
########
alias b="brew"
alias bo="brew outdated"
alias bu="brew update && brew outdated && brew upgrade && brew cleanup"

#######
# Git #
#######
alias gti=git
alias git=hub

###############
# DIRECTORIES #
###############
alias cdc="cd ~/Documents/code"
alias cdd="cd ~/Downloads"
alias cdw="cd ~/workspace"

########
# MISC #
########
alias bkoff="cd ~/.bin/backup && git fetch && git reset --hard origin/master && chmod 755 backup.sh && /bin/bash -l -c '~/.bin/backup/backup.sh'"
alias sshadd="ssh-add -K ~/.ssh/id_rsa"

#########
# SWIFT #
#########
alias xcode-swift="xcrun launch-with-toolchain /Library/Developer/Toolchains/swift-latest.xctoolchain/"

