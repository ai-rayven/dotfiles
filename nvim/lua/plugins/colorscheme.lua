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
              -- Full-line diff backgrounds are kept subtle so a mostly-added/removed file
              -- doesn't become a wall of color that drowns the syntax highlighting; the
              -- gutter sign bars still mark every changed line. Only DiffText (the exact
              -- changed words) uses a strong, high-contrast color so real edits pop.
              DiffAdd    = { bg = "#16261c", fg = "NONE" },
              DiffChange = { bg = "#1c2230", fg = "NONE" },
              DiffDelete = { bg = "#2a1a1e", fg = "NONE" },
              DiffText   = { bg = "#1f4d7a", fg = "#ffffff", bold = true },
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
