return {
  "nvim-lualine/lualine.nvim",
  config = function()
    require("lualine").setup({
      -- ... other config
      options = {
        theme = "auto", -- "auto" will set the theme dynamically based on the colorscheme
      },
      -- ... other config
    })
  end,
}
