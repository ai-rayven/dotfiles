return {
  {
    'nvim-treesitter/nvim-treesitter',
    lazy = false,
    build = ':TSUpdate',
    config = function()
      local ensure_installed = { 'bicep', 'lua', 'vim', 'bash', 'json', 'yaml' }
      require('nvim-treesitter').install(ensure_installed)

      vim.api.nvim_create_autocmd('FileType', {
        pattern = ensure_installed,
        callback = function() vim.treesitter.start() end,
      })
    end,
  },
}
