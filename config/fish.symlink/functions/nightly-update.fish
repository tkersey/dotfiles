function nightly-update
    brew cleanup luajit neovim tree-sitter --prune=1
    brew uninstall --ignore-dependencies luajit neovim tree-sitter
    brew install luajit neovim tree-sitter
    brew upgrade --cask wezterm@nightly --no-quarantine --greedy-latest
end
