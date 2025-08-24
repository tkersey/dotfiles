return {
  {
    "neovim/nvim-lspconfig",
    opts = {
      servers = {
        sourcekit = {
          filetypes = { "swift" },
        },
        basedpyright = {
          settings = {
            basedpyright = {
              pythonPath = ".venv/bin/python",
              analysis = {
                typeCheckingMode = "off",
                diagnosticMode = "workspace",
              },
            },
          },
        },
      },
    },
  },
  {
    "WhoIsSethDaniel/mason-tool-installer.nvim",
    config = function()
      require("mason-tool-installer").setup({
        ensure_installed = {
          "eslint_d",   -- Fast ESLint daemon for linting
          "prettierd",  -- Fast Prettier daemon for formatting
        },
        auto_update = true,
        run_on_start = true,
      })
    end,
  },
}