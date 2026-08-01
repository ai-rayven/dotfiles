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

      -- python: basedpyright owns types, ruff owns lint/format.
      -- basedpyright defaults to "recommended", which reports every untyped
      -- expression and missing stub; "standard" matches upstream pyright.
      vim.lsp.config('basedpyright', {
        settings = {
          basedpyright = {
            analysis = {
              typeCheckingMode = 'standard',
              diagnosticSeverityOverrides = {
                -- ruff already reports these, don't double up
                reportUnusedImport = 'none',
                reportUnusedVariable = 'none',
              },
            },
          },
        },
      })

      -- ruff's hover is a stub; let basedpyright answer hover requests
      vim.lsp.config('ruff', {
        on_attach = function(client)
          client.server_capabilities.hoverProvider = false
        end,
      })
    end,
  },
}
