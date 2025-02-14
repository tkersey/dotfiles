return {
  { "neovim/nvim-lspconfig" },
  {
    "williamboman/mason.nvim",
    config = function()
      require("mason").setup({})
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

      -- Configure Mason-LSPconfig
      require("mason-lspconfig").setup({
        automatic_installation = true,
        ensure_installed = { "basedpyright" },
        filetypes = { "python" },
        handlers = {
          basedpyright = function()
            lspconfig.basedpyright.setup({
              capabilities = capabilities,
              autostart = true,
              settings = {
                python = {
                  pythonPath = ".venv/bin/python",
                  analysis = {
                    typeCheckingMode = "basic", -- or "strict" if you prefer
                    diagnosticMode = "workspace",
                    useLibraryCodeForTypes = true,
                    autoImportCompletions = true,
                    reportUnusedImport = false,
                    reportMissingImports = false,
                  },
                },
              },
            })
          end,
        },
      })
    end,
  },
}
