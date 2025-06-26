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
      javascript = { { "eslint_d", "eslint" }, { "prettierd", "prettier" } },
      typescript = { { "eslint_d", "eslint" }, { "prettierd", "prettier" } },
      javascriptreact = { { "eslint_d", "eslint" }, { "prettierd", "prettier" } },
      typescriptreact = { { "eslint_d", "eslint" }, { "prettierd", "prettier" } },
      json = { { "prettierd", "prettier" } },
      css = { { "prettierd", "prettier" } },
      html = { { "prettierd", "prettier" } },
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
          "eslint.config.js",
          "eslint.config.mjs",
        }),
        condition = function(self, ctx)
          return vim.fs.find({
            ".eslintrc",
            ".eslintrc.js",
            ".eslintrc.json",
            ".eslintrc.yml",
            ".eslintrc.yaml",
            "eslint.config.js",
            "eslint.config.mjs",
            "package.json",
          }, { path = ctx.filename, upward = true })[1]
        end,
      },
      -- Use global .prettierrc file instead of trying to configure via env vars
      prettierd = {
        command = "prettierd",
        args = { "$FILENAME" },
        condition = function(self, ctx)
          return vim.fs.find({
            ".prettierrc",
            ".prettierrc.js",
            ".prettierrc.json",
            ".prettierrc.yml",
            ".prettierrc.yaml",
            "prettier.config.js",
            "prettier.config.mjs",
            "package.json",
          }, { path = ctx.filename, upward = true })[1]
        end,
      },
      trim_whitespace = {
        timeout_ms = 5000, -- Increase timeout to 5 seconds
      },
    },
  },
}
