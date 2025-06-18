return {
  {
    "nvim-neotest/neotest",
    dependencies = {
      "adrigzr/neotest-mocha",
    },
    opts = {
      adapters = {
        ["neotest-mocha"] = {
          command = "npm test --",
          env = { CI = true },
          cwd = function(path)
            return vim.fn.getcwd()
          end,
        },
      },
    },
  },
}