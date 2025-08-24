return {
  "stevearc/conform.nvim",
  opts = function(_, opts)
    -- Add trim_whitespace for all files
    opts.formatters_by_ft["*"] = { "trim_whitespace" }
    
    -- Use prettierd instead of prettier for supported file types
    local prettier_ft = {
      "javascript",
      "javascriptreact",
      "typescript",
      "typescriptreact",
      "vue",
      "css",
      "scss",
      "less",
      "html",
      "json",
      "jsonc",
      "yaml",
      "markdown",
      "markdown.mdx",
      "graphql",
      "handlebars",
    }
    
    for _, ft in ipairs(prettier_ft) do
      opts.formatters_by_ft[ft] = { "prettierd" }
    end
    
    opts.formatters = opts.formatters or {}
    opts.formatters.trim_whitespace = { timeout_ms = 5000 }
    return opts
  end,
}