return {
  {
    "neovim/nvim-lspconfig",
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

      -- Sourcekit setup
      lspconfig.sourcekit.setup({
        capabilities = capabilities,
      })

      -- Pyright setup
      lspconfig.pyright.setup({
        capabilities = capabilities,
        settings = {
          python = {
            analysis = {
              typeCheckingMode = "recommended",
              autoSearchPaths = true,
              useLibraryCodeForTypes = true,
            },
          },
        },
      })

      -- LSP keybindings
      vim.api.nvim_create_autocmd("LspAttach", {
        desc = "LSP Actions",
        callback = function(args)
          vim.keymap.set("n", "K", vim.lsp.buf.hover, { noremap = true, silent = true })
          vim.keymap.set("n", "gd", vim.lsp.buf.definition, { noremap = true, silent = true })
        end,
      })
    end,
  },
}
