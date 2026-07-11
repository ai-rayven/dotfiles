return {
  {
    'NeogitOrg/neogit',
    dependencies = { 'nvim-lua/plenary.nvim', 'sindrets/diffview.nvim' },
    keys = { { '<leader>g', function() require('neogit').open() end, desc = 'Neogit' } },
  },
  {
    'sindrets/diffview.nvim',
    cmd = { 'DiffviewOpen', 'DiffviewClose', 'DiffviewFileHistory' },
    keys = {
      {
        '<leader>d',
        function()
          if next(require('diffview.lib').views) == nil then
            vim.cmd('DiffviewOpen')
          else
            vim.cmd('DiffviewClose')
          end
        end,
        desc = 'Diff View (toggle)',
      },
    },
    opts = function()
      local actions = require('diffview.actions')
      -- remap file panel toggle off <leader>b (taken by Buffers)
      local overrides = {
        { 'n', '<leader>o', actions.toggle_files, { desc = 'Toggle the file panel' } },
      }
      return {
        keymaps = {
          view = overrides,
          file_panel = overrides,
          file_history_panel = overrides,
        },
      }
    end,
  },
  {
    'lewis6991/gitsigns.nvim',
    event = 'BufWinEnter',
    opts = { current_line_blame = true },  -- who last touched this line
  },
}

