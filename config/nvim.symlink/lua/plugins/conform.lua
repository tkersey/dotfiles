return {
  "stevearc/conform.nvim",
  tag = "stable",
  event = { "BufWritePre" },
  cmd = { "ConformInfo" },
  keys = {
    {
      "gf",
      function()
        require("conform").format({ async = true, lsp_fallback = true })
      end,
      mode = "",
      desc = "Format buffer",
    },
  },
  opts = {
    -- https://github.com/stevearc/conform.nvim#formatters
    -- :help conform-formatters
    formatters_by_ft = {
      lua = { "stylua" },
      --      python = { "ruff_fix", "ruff_format" },
      sh = { "shellcheck" },
      toml = { "taplo" },
      javascript = { "prettierd", "eslint_d" },
      typescript = { "prettierd", "eslint_d" },
      javascriptreact = { "prettierd", "eslint_d" },
      typescriptreact = { "prettierd", "eslint_d" },
      json = { "prettierd" },
      css = { "prettierd" },
      html = { "prettierd" },
      ["*"] = { "trim_whitespace" },
    },

    formatters = {
      eslint_d = {
        -- Make eslint_d respect .eslintrc.js
        command = "eslint_d",
        args = {
          "--fix-to-stdout",
          "--stdin",
          "--stdin-filename",
          "$FILENAME",
        },
        cwd = require("conform.util").root_file({
          ".eslintrc",
          ".eslintrc.js",
          ".eslintrc.json",
          ".eslintrc.yml",
          ".eslintrc.yaml",
        }),
      },
      -- Use global .prettierrc file instead of trying to configure via env vars
      prettierd = {
        command = "prettierd",
        args = { "$FILENAME" },
      },
    },
  },
}
