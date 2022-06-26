nnoremap <leader><Space> <cmd>lua require('telescope.builtin').find_files()<cr>
nnoremap <leader>/ <cmd>lua require('telescope.builtin').live_grep()<cr>
nnoremap <leader>tb <cmd>lua require('telescope.builtin').buffers()<cr>
nnoremap <Leader>gs :lua require('telescope.builtin').git_status()<CR>
nnoremap <leader>fh <cmd>lua require('telescope.builtin').help_tags()<cr>

lua << END
  require('telescope').load_extension('fzy_native')
END
