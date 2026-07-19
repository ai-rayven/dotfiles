return {
  {
    'neovim/nvim-lspconfig',
    dependencies = {
      { 'mason-org/mason.nvim', opts = {} },
      'mason-org/mason-lspconfig.nvim',
    },
    config = function()
      -- mason-lspconfig installs these and, by default, auto-enables each
      -- installed server via vim.lsp.enable() so it attaches to matching buffers.
      require('mason-lspconfig').setup({
        ensure_installed = {
          'lua_ls',      -- lua
          'basedpyright', -- python (type checking / definitions)
          'ruff',        -- python (lint / format)
          'bashls',      -- bash
          'jsonls',      -- json
          'yamlls',      -- yaml
          'bicep',       -- bicep (needs dotnet runtime)
        },
      })
    end,
  },
}
