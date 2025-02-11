local use_anthropic = true -- Default to Claude 3 Sonnet

local function get_opts()
  return {
    adaptor = use_anthropic and "anthropic" or "openai",
    model = use_anthropic and "claude-3-sonnet-20240229" or "gpt-4o",
    api_key = os.getenv(use_anthropic and "ANTHROPIC_API_KEY" or "OPENAI_API_KEY"),
  }
end

return {
  "olimorris/codecompanion.nvim",
  event = "VeryLazy",
  dependencies = { "nvim-lua/plenary.nvim" },
  opts = get_opts(),
  keys = {
    { "<leader>cc", "<cmd>CodeCompanion<cr>", desc = "Code Companion Chat" },
    { "<leader>ce", "<cmd>CodeCompanionExplain<cr>", desc = "Explain Code" },
    { "<leader>cf", "<cmd>CodeCompanionFix<cr>", desc = "Fix Code" },
    { "<leader>cg", "<cmd>CodeCompanionGenerate<cr>", desc = "Generate Code" },
    {
      "<leader>cs",
      function()
        use_anthropic = not use_anthropic
        require("codecompanion").setup(get_opts())
      end,
      desc = "Switch AI Model",
    },
  },
}
