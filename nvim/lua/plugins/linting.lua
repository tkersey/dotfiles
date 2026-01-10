-- Configure nvim-lint to use eslint_d instead of eslint
return {
  {
    "mfussenegger/nvim-lint",
    opts = function(_, opts)
      -- Replace eslint with eslint_d for JavaScript/TypeScript files
      opts.linters_by_ft = opts.linters_by_ft or {}
      local eslint_filetypes = {
        "javascript",
        "javascriptreact", 
        "typescript",
        "typescriptreact",
        "vue",
        "svelte",
      }
      
      for _, ft in ipairs(eslint_filetypes) do
        opts.linters_by_ft[ft] = { "eslint_d" }
      end
      
      return opts
    end,
  },
}