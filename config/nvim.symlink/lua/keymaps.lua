vim.keymap.set("", ",", "<Nop>", { desc = "Remap ',' as leader key", noremap = true, silent = true })

vim.g.mapleader = ","
vim.g.maplocalleader = ""

vim.keymap.set("n", "<leader>p", ":bprev<CR>", { desc = "Previous buffer", noremap = true, silent = true })
vim.keymap.set("n", "<leader>n", ":bnext<CR>", { desc = "Next buffer", noremap = true, silent = true })

vim.keymap.set("n", "<leader>sv", ":source $MYVIMRC<CR>", { desc = "source nvim", noremap = true, silent = true })

