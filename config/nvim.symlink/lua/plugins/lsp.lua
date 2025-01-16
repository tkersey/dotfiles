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
        ensure_installed = { "basedpyright" },
        handlers = {
          basedpyright = function()
            lspconfig.basedpyright.setup({
              capabilities = capabilities,
              settings = {
                basedpyright = {
                  analysis = {
                    autoImportCompletions = true,
                    autoSearchPaths = true,
                    diagnosticMode = "openFilesOnly",
                    useLibraryCodeForTypes = true,
                    typeCheckingMode = "basic",
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
