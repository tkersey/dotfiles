function nightly-update
    brew cleanup luajit neovim tree-sitter tree-sitter-cli --prune=1
    brew uninstall --ignore-dependencies luajit neovim tree-sitter tree-sitter-cli
    brew install luajit neovim tree-sitter tree-sitter-cli
end
