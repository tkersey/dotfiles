return {
  "sindrets/diffview.nvim",
  dependencies = { "nvim-lua/plenary.nvim" },
  cmd = { "DiffviewOpen", "DiffviewFileHistory" },
  keys = {
    { "<leader>gd", "<cmd>DiffviewOpen<CR>", desc = "Open DiffView" },
    { "<leader>gh", "<cmd>DiffviewFileHistory<CR>", desc = "Open File History" },
    { "<leader>gc", "<cmd>DiffviewClose<CR>", desc = "Close DiffView" },
  },
  opts = {
    view = {
      default = {
        layout = "diff2_horizontal",
      },
    },
    keymaps = {
      disable_defaults = false,
      view = {
        ["<tab>"] = "select_next_entry",
        ["<s-tab>"] = "select_prev_entry",
        ["gf"] = "goto_file_edit",
        ["<C-w><C-f>"] = "goto_file_split",
        ["<C-w>gf"] = "goto_file_tab",
        ["<leader>e"] = "focus_files",
        ["<leader>b"] = "toggle_files",
      },
      file_panel = {
        ["j"] = "next_entry",
        ["k"] = "prev_entry",
        ["<cr>"] = "select_entry",
        ["<tab>"] = "select_next_entry",
        ["<s-tab>"] = "select_prev_entry",
        ["-"] = "toggle_stage_entry",
        ["S"] = "stage_all",
        ["U"] = "unstage_all",
        ["X"] = "restore_entry",
        ["R"] = "refresh_files",
        ["<leader>e"] = "focus_files",
        ["<leader>b"] = "toggle_files",
      },
      file_history_panel = {
        ["j"] = "next_entry",
        ["k"] = "prev_entry",
        ["<cr>"] = "select_entry",
        ["<tab>"] = "select_next_entry",
        ["<s-tab>"] = "select_prev_entry",
        ["y"] = "copy_hash",
        ["<leader>e"] = "focus_files",
        ["<leader>b"] = "toggle_files",
      },
    },
  },
}

