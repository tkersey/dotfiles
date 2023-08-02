function nvim-nightly
  brew cleanup luajit neovim tree-sitter --prune=1
  brew uninstall --ignore-dependencies luajit neovim tree-sitter
  brew install luajit neovim tree-sitter
end
