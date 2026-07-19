return {
  {
    'ellisonleao/gruvbox.nvim',
    lazy = false,
    priority = 1000,
    config = function()
      local is_transparent = vim.uv.os_uname().sysname == 'Darwin'
              or string.find(vim.uv.os_uname().sysname, 'Windows') ~= nil
              or string.find(vim.uv.os_uname().release, 'WSL') ~= nil
      require('gruvbox').setup({
        transparent_mode = is_transparent,
        overrides = {
          SnacksPickerDir = { fg = "#a89984"},
        }
      })
      vim.o.background = "dark"
      vim.cmd('colorscheme gruvbox')
    end,
  },
}
