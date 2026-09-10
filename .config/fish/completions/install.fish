# Fish shell completions for the dotfiles install script

# Disable file completions for this command since we only have specific flags
complete -c install -f

# Define the available flags
complete -c install -l dotfiles -d 'Process .symlink files'
complete -c install -l symlink-files -d 'Process custom symlinks from links.conf'
complete -c install -l homebrew -d 'Run homebrew installation/update'
complete -c install -l help -d 'Show help message'

# If the install script is not in the PATH, you may need to add completions for the full path
complete -c ./install -f
complete -c ./install -l dotfiles -d 'Process .symlink files'
complete -c ./install -l symlink-files -d 'Process custom symlinks from links.conf'
complete -c ./install -l homebrew -d 'Run homebrew installation/update'
complete -c ./install -l help -d 'Show help message'