return {
  "stevearc/conform.nvim",
  opts = function(_, opts)
    -- Add trim_whitespace for all files
    opts.formatters_by_ft["*"] = { "trim_whitespace" }
    opts.formatters = opts.formatters or {}
    opts.formatters.trim_whitespace = { timeout_ms = 5000 }
    return opts
  end,
}