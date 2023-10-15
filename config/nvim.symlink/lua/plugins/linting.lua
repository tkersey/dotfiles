return {
  {
    "mfussenegger/nvim-lint",
    opts = {
      linters_by_ft = {
        javascript = { "eslint" },
        javascriptreact = { "eslint" },
        markdown = { "markdownlint" },
        sh = { "shellcheck" },
        typescript = { "eslint" },
        typescriptreact = { "eslint" },
      },
    },
  },
}
