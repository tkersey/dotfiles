-- Keymaps are automatically loaded on the VeryLazy event
-- Default keymaps that are always set: https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/keymaps.lua
-- Add any additional keymaps here

-- LSP keybindings
vim.api.nvim_create_autocmd("LspAttach", {
  desc = "LSP Actions",
  callback = function(args)
    vim.keymap.set("n", "K", vim.lsp.buf.hover, { noremap = true, silent = true })
    vim.keymap.set("n", "gd", vim.lsp.buf.definition, { noremap = true, silent = true })
  end,
})
