return {
  { "neovim/nvim-lspconfig" },
  {
    "williamboman/mason.nvim",
    config = function()
      require("mason").setup({})
    end,
  },
  {
    "WhoIsSethDaniel/mason-tool-installer.nvim",
    config = function()
      require("mason-tool-installer").setup({
        ensure_installed = {
          -- Formatters
          "eslint_d",
          "prettierd",
          "stylua",
          --          "ruff",
          "shellcheck",
          "taplo",

          -- LSP servers are handled by mason-lspconfig
        },
        auto_update = true,
        run_on_start = true,
      })
    end,
  },
  {
    "williamboman/mason-lspconfig.nvim",
    config = function()
      local lspconfig = require("lspconfig")

      -- Common capabilities for all LSP servers
      local capabilities = {
        workspace = {
          didChangeWatchedFiles = {
            dynamicRegistration = true,
          },
        },
      }

      -- Configure Mason-LSPconfig for servers that can be installed via Mason
      require("mason-lspconfig").setup({
        automatic_installation = true,
        ensure_installed = { "basedpyright" },
      })

      -- Set up the servers
      -- Python
      lspconfig.basedpyright.setup({
        capabilities = capabilities,
        autostart = true,
        settings = {
          basedpyright = {
            pythonPath = ".venv/bin/python",
            analysis = {
              typeCheckingMode = "off", -- or "strict" if you prefer
              diagnosticMode = "workspace",
              useLibraryCodeForTypes = true,
              autoImportCompletions = true,
              reportUnusedImport = false,
              reportMissingImports = false,
            },
          },
        },
      })

      -- Swift
      lspconfig.sourcekit.setup({
        capabilities = capabilities,
        autostart = true,
        filetypes = { "swift" },
        cmd = { "sourcekit-lsp" },
      })
    end,
  },
}
