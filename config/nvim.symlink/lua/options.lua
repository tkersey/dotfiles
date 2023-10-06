local options = {
  expandtab = true,
  tabstop = 2,
  softtabstop = 2,
  shiftwidth = 2,
  number = true,
  autoindent = true,
  clipboard = "unnamedplus",
  incsearch = true,
  hlsearch = true,
  updatetime = 100,
  termguicolors = true
}

for k, v in pairs(options) do
  vim.opt[k] = v
end
