local wezterm = require("wezterm")

local config = {}

if wezterm.config_builder then
  config = wezterm.config_builder()
end

config.font = wezterm.font("SF Mono")
config.font_size = 14.0

config.colors = {
  -- Cyberdream
  foreground = "#ffffff",
  background = "#16181a",

  cursor_bg = "#ffffff",
  cursor_fg = "#16181a",
  cursor_border = "#ffffff",

  selection_fg = "#ffffff",
  selection_bg = "#3c4048",

  scrollbar_thumb = "#16181a",
  split = "#16181a",

  ansi = { "#16181a", "#ff6e5e", "#5eff6c", "#f1ff5e", "#5ea1ff", "#bd5eff", "#5ef1ff", "#ffffff" },
  brights = { "#3c4048", "#ff6e5e", "#5eff6c", "#f1ff5e", "#5ea1ff", "#bd5eff", "#5ef1ff", "#ffffff" },
  indexed = { [16] = "#ffbd5e", [17] = "#ff6e5e" },
}

config.hide_tab_bar_if_only_one_tab = true

return config
