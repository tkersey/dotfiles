function nvim-nightly
  brew cleanup luajit neovim tree-sitter --prune=1
  brew reinstall luajit neovim tree-sitter
end
