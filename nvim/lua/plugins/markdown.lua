return {
  {
    'MeanderingProgrammer/render-markdown.nvim',
    dependencies = { 'nvim-treesitter/nvim-treesitter', 'nvim-tree/nvim-web-devicons' },
    ft = { 'markdown' },
    opts = {},  -- renders headings, code blocks, tables, checkboxes inline
    keys = {
      { '<leader>m', '<cmd>RenderMarkdown toggle<cr>', desc = 'Toggle Markdown Render', ft = 'markdown' },
    },
  },
}
