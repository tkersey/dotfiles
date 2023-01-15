nnoremap <leader><Space> <cmd>lua require('telescope.builtin').find_files()<cr>
nnoremap <leader>/ <cmd>lua require('telescope.builtin').live_grep()<cr>
nnoremap <leader>tb <cmd>lua require('telescope.builtin').buffers()<cr>
nnoremap <Leader>tc :lua require('telescope.builtin').commands()<CR>
nnoremap <Leader>gs :lua require('telescope.builtin').git_status()<CR>
nnoremap <leader>fh <cmd>lua require('telescope.builtin').help_tags()<cr>
nnoremap <Leader>tt :lua require('telescope.builtin').treesitter()<CR>
nnoremap <leader>fb :lua require('telescope').extensions.file_browser.file_browser()<CR>
nnoremap <leader>fB :lua require('telescope').extensions.file_browser.file_browser({path = "%:p:h"})<CR>

lua << END
  local fb_actions = require "telescope".extensions.file_browser.actions
  require("telescope").setup {
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
  }

  require('telescope').load_extension('fzy_native')
  require('telescope').load_extension('file_browser')
  require('telescope').load_extension('zoxide')
END
