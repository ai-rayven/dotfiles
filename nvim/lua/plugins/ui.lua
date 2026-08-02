return {
  {
    'folke/which-key.nvim',
    lazy = false,
    config = true,  -- popup that shows what my leader keys do
  },
  {
    'nvim-tree/nvim-web-devicons',
    opts = {}
  },
  {
    'shortcuts/no-neck-pain.nvim',
    keys = { { '<leader>c', '<cmd>NoNeckPain<cr>', desc = 'Toggle Centered Text' } },
    opts = {}
  }
}

