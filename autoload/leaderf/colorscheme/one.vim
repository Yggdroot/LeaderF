" ============================================================================
" File:        one.vim
" Description:
" Author:      Tomwei7 <tomwei7@163.com>
" Website:     https://github.com/tomwei7
" Note:
" License:     Apache License, Version 2.0
" ============================================================================


let s:palette = {
            \   'stlName': {
            \       'gui': 'bold',
            \       'font': 'NONE',
            \       'guifg': '#3E4452',
            \       'guibg': '#98C379',
            \       'cterm': 'bold',
            \       'ctermfg': '16',
            \       'ctermbg': '76'
            \   },
            \   'stlCategory': {
            \       'gui': 'NONE',
            \       'font': 'NONE',
            \       'guifg': '#3E4452',
            \       'guibg': '#E06C75',
            \       'cterm': 'NONE',
            \       'ctermfg': '16',
            \       'ctermbg': '168'
            \   },
            \   'stlNameOnlyMode': {
            \       'gui': 'NONE',
            \       'font': 'NONE',
            \       'guifg': '#3E4452',
            \       'guibg': '#61AFEF',
            \       'cterm': 'NONE',
            \       'ctermfg': '16',
            \       'ctermbg': '75'
            \   },
            \   'stlFullPathMode': {
            \       'gui': 'NONE',
            \       'font': 'NONE',
            \       'guifg': '#3E4452',
            \       'guibg': '#61AFEF',
            \       'cterm': 'NONE',
            \       'ctermfg': '16',
            \       'ctermbg': '147'
            \   },
            \   'stlFuzzyMode': {
            \       'gui': 'NONE',
            \       'font': 'NONE',
            \       'guifg': '#3E4452',
            \       'guibg': '#E5C07B',
            \       'cterm': 'NONE',
            \       'ctermfg': '16',
            \       'ctermbg': '180'
            \   },
            \   'stlRegexMode': {
            \       'gui': 'NONE',
            \       'font': 'NONE',
            \       'guifg': '#3E4452',
            \       'guibg': '#98C379',
            \       'cterm': 'NONE',
            \       'ctermfg': '16',
            \       'ctermbg': '76'
            \   },
            \   'stlCwd': {
            \       'gui': 'NONE',
            \       'font': 'NONE',
            \       'guifg': '#ABB2BF',
            \       'guibg': '#475265',
            \       'cterm': 'NONE',
            \       'ctermfg': '145',
            \       'ctermbg': '236'
            \   },
            \   'stlBlank': {
            \       'gui': 'NONE',
            \       'font': 'NONE',
            \       'guifg': '#ABB2BF',
            \       'guibg': '#3E4452',
            \       'cterm': 'NONE',
            \       'ctermfg': '145',
            \       'ctermbg': '235'
            \   },
            \   'stlSpin': {
            \       'gui': 'NONE',
            \       'font': 'NONE',
            \       'guifg': '#E6E666',
            \       'guibg': '#3E4452',
            \       'cterm': 'NONE',
            \       'ctermfg': '185',
            \       'ctermbg': '235'
            \   },
            \   'stlLineInfo': {
            \       'gui': 'NONE',
            \       'font': 'NONE',
            \       'guifg': '#3E4452',
            \       'guibg': '#98C379',
            \       'cterm': 'NONE',
            \       'ctermfg': '16',
            \       'ctermbg': '76'
            \   },
            \   'stlTotal': {
            \       'gui': 'NONE',
            \       'font': 'NONE',
            \       'guifg': '#3E4452',
            \       'guibg': '#98C379',
            \       'cterm': 'NONE',
            \       'ctermfg': '16',
            \       'ctermbg': '76'
            \   }
            \ }

let g:leaderf#colorscheme#one#palette = leaderf#colorscheme#mergePalette(s:palette)
