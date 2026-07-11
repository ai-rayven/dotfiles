local wezterm = require("wezterm")

local config = wezterm.config_builder()

config.keys = {
	{
		key = "b",
		mods = "CMD|SHIFT",
		action = wezterm.action_callback(function()
			wezterm.background_child_process({ "open", "-a", "Microsoft Edge" })
		end),
	},
}

config.color_scheme = "rose-pine-moon"
config.font_size = 15.0
config.window_background_opacity = 0.8
config.macos_window_background_blur = 50
config.hide_tab_bar_if_only_one_tab = true
config.window_decorations = "RESIZE"

return config
