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
      python = { "ruff_fix", "ruff_format" },
      sh = { "shellcheck" },
      toml = { "taplo" },
      ["*"] = { "trim_whitespace" },
    },
  },
}
