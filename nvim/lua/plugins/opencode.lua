return {
  {
    'nickjvandyke/opencode.nvim',
    version = '*', -- latest stable release
    config = function()
      ---@type opencode.Opts
      vim.g.opencode_opts = {}

      -- reload buffers live when opencode edits files
      vim.o.autoread = true

      local oc = function() return require('opencode') end
      vim.keymap.set({ 'n', 'x' }, '<C-a>', function() oc().ask('@this: ') end, { desc = 'Ask OpenCode' })
      vim.keymap.set({ 'n', 'x' }, '<C-x>', function() oc().select() end, { desc = 'Select OpenCode' })
      vim.keymap.set({ 'n', 'x' }, 'go', function() return oc().operator('@this ') end, { desc = 'Append range to OpenCode', expr = true })
      vim.keymap.set({ 'n' }, 'goo', function() return oc().operator('@this ') .. '_' end, { desc = 'Append line to OpenCode', expr = true })
      vim.keymap.set({ 'n' }, '<S-C-u>', function() oc().command('session.half.page.up') end, { desc = 'Scroll OpenCode up' })
      vim.keymap.set({ 'n' }, '<S-C-d>', function() oc().command('session.half.page.down') end, { desc = 'Scroll OpenCode down' })
    end,
  },
}
