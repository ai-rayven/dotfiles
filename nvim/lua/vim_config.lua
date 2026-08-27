local o = vim.opt
vim.g.mapleader = ' '          -- space is the leader key
vim.g.loaded_netrw = 1         -- nvim-tree replaces netrw
vim.g.loaded_netrwPlugin = 1
o.expandtab = true             -- spaces, not tabs
o.shiftwidth = 2               -- 2 spaces per indent level
o.number = true                -- absolute number on the cursor line, relative elsewhere
o.relativenumber = true        -- relative line numbers for fast jumps
o.ignorecase = true            -- search is case-insensitive by default
o.smartcase = true             -- case-sensitive only if i type a capital
o.clipboard = 'unnamedplus'    -- share the system clipboard
o.scrolloff = 16               -- keep cursor away from the screen edge
o.undofile = true              -- persistent undo across sessions
o.termguicolors = true
-- nvim 0.12 already enables linematch:40 by default; bump the cap so larger hunks
-- also get intelligent intra-hunk line alignment
o.diffopt:remove('linematch:40')
o.diffopt:append('linematch:60')
