-- save by pressing Escape
vim.keymap.set('n', '<Esc>', ':w<CR>', { desc = 'Save' })
-- pasting over a selection no longer clobbers your clipboard
vim.cmd([[ xnoremap <expr> p 'pgv"'.v:register.'y' ]])

