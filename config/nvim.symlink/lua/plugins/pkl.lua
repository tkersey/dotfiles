return {
  "nvim-treesitter/nvim-treesitter",
  build = function(_)
    vim.cmd("TSUpdate")
  end,
}, {
  "https://github.com/apple/pkl-neovim",
  lazy = true,
  event = "BufReadPre *.pkl",
  dependencies = {
    "nvim-treesitter/nvim-treesitter",
  },
  build = function()
    vim.cmd("TSInstall! pkl")
  end,
}
