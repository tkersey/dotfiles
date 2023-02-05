local telescope = require("telescope")
local actions = require("telescope.actions")
local fb_actions = telescope.extensions.file_browser.actions
local opts = { noremap = true, silent = true }

vim.keymap.set("n", "<leader><Space>", [[<Cmd>Telescope find_files<CR>]], opts)
vim.keymap.set("n", "<leader>/", [[<Cmd>Telescope live_grep<CR>]], opts)
vim.keymap.set("n", "<leader>tb", [[<Cmd>Telescope buffers<CR>]], opts)
vim.keymap.set("n", "<leader>tc", [[<Cmd>Telescope commands<CR>]], opts)
vim.keymap.set("n", "<leader>gs", [[<Cmd>Telescope git_status<CR>]], opts)
vim.keymap.set("n", "<leader>fh", [[<Cmd>Telescope help_tags<CR>]], opts)
vim.keymap.set("n", "<leader>tt", [[<Cmd>Telescope treesitter<CR>]], opts)
vim.keymap.set("n", "<leader>fb", [[<Cmd>Telescope file_browser<CR>]], opts)
vim.keymap.set("n", "<leader>fB", [[<Cmd>Telescope file_browser path=%:p:h<CR>]], opts)

telescope.load_extension('fzy_native')
telescope.load_extension('file_browser')
telescope.load_extension('zoxide')

telescope.setup({
  extensions = {
    file_browser = {
      theme = "ivy",
      hijack_netrw = false,
      mappings = {
        ["i"] = {
          -- your custom insert mode mappings
        },
        ["n"] = {
          ["<C-a>"] = fb_actions.create,
          ["<C-m>"] = fb_actions.move,
          ["<C-d>"] = fb_actions.remove,
        },
      },
    },
  },
})
