" options

syntax on
filetype plugin indent on " load filetype specific indent files
set expandtab             " tabs are spaces
set tabstop=2             " number of visual spaces per TAB
set softtabstop=2         " number of spaces in tab when editing
set shiftwidth=2          " number of spaces used when indenting
set number                " show line numbers
set autoindent            " enables auto indent
set clipboard=unnamedplus " use system clipboard
set nobackup              " Don't create annoying backup files
set incsearch             " search as characters are entered
set hlsearch              " highlight matches
set updatetime=100        " default updatetime is 4000ms and not good for async

" remap
let mapleader=","          " leader is comma

" Install vim-plug if not found
if empty(glob('~/.local/share/nvim/site/autoload/plug.vim'))
  silent !curl -fLo ~/.local/share/nvim/site/autoload/plug.vim --create-dirs
    \ https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
  autocmd VimEnter * PlugInstall --sync | source $MYVIMRC
endif

call plug#begin('~/.vim/plugged')
" telescope
Plug 'nvim-lua/plenary.nvim'
Plug 'nvim-telescope/telescope.nvim'
Plug 'nvim-telescope/telescope-fzy-native.nvim'

" color scheme
Plug 'beikome/cosme.vim'

" lsp
Plug 'neovim/nvim-lspconfig'

" completion
Plug 'hrsh7th/nvim-cmp'
Plug 'hrsh7th/cmp-nvim-lsp'
Plug 'hrsh7th/cmp-path'
Plug 'hrsh7th/cmp-buffer'
Plug 'hrsh7th/cmp-cmdline'

" statusline
Plug 'nvim-lualine/lualine.nvim'

" treesitter
Plug 'nvim-treesitter/nvim-treesitter', {'do': ':TSUpdate'}
Plug 'nvim-treesitter/nvim-treesitter-context'

" cursor
Plug 'mg979/vim-visual-multi', {'branch': 'master'}

" git
Plug 'mhinz/vim-signify'

call plug#end()

" config
source ~/.config/nvim/modules/colorscheme.vim
source ~/.config/nvim/modules/completion.vim
source ~/.config/nvim/modules/lsp.vim
source ~/.config/nvim/modules/statusline.vim
source ~/.config/nvim/modules/telescope.vim
source ~/.config/nvim/modules/treesitter.vim
source ~/.config/nvim/modules/treesitter-context.vim
source ~/.config/nvim/modules/autocommands/yank.vim
