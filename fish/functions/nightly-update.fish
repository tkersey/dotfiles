function nightly-update
    brew cleanup luajit neovim tree-sitter-cli --prune=1
    brew uninstall --force --ignore-dependencies luajit neovim tree-sitter-cli
    brew install luajit tree-sitter-cli
    brew install --HEAD neovim
end
