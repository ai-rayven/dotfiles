return {
  {
    'projekt0n/github-nvim-theme',
    name = 'github-theme',
    lazy = false,
    priority = 1000,
    config = function()
      local uname = vim.uv.os_uname()
      local is_transparent = uname.sysname == 'Darwin'
              or string.find(uname.sysname, 'Windows') ~= nil
              or string.find(uname.release, 'WSL') ~= nil

      -- transparency is only wanted in dark mode; in light mode it would leak the
      -- terminal's dark background through and defeat the point of the light theme
      local function apply(background)
        require('github-theme').setup({
          options = {
            transparent = is_transparent and background == 'dark',
          },
          groups = {
            all = {
              ["@string.documentation"] = { link = "Comment" },  -- docstrings render gray + italic like comments
            },
          },
        })
        vim.o.background = background
        vim.cmd('colorscheme github_' .. background)
      end

      apply('dark')

      vim.keymap.set('n', '<leader>t', function()
        apply(vim.o.background == 'dark' and 'light' or 'dark')
      end, { desc = 'Toggle light/dark theme' })
    end,
  },
}
