return {
  "nvim-neotest/neotest",
  dependencies = {
    "nvim-neotest/neotest-python",
    "nvim-treesitter/nvim-treesitter",
    "nvim-neotest/nvim-nio",
    "nvim-lua/plenary.nvim",
  },
  config = function()
    require("neotest").setup({
      adapters = {
        require("neotest-python")({
          runner = "pytest",
        }),
      },
    })
  end,
}
