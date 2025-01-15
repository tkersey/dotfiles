return {
  "stevanmilic/nvim-lspimport", -- imports only for pyright server
  config = function()
    vim.keymap.set("n", "<leader>li", require("lspimport").import, { noremap = true }) -- lsp import code action
  end,
}
