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
            \       'gui': 'bold,nocombine',
            \       'font': 'NONE',
            \       'guifg': '#3E4452',
            \       'guibg': '#98C379',
            \       'cterm': 'bold,nocombine',
            \       'ctermfg': '16',
            \       'ctermbg': '76'
            \   },
            \   'stlCategory': {
            \       'gui': 'nocombine',
            \       'font': 'NONE',
            \       'guifg': '#3E4452',
            \       'guibg': '#E06C75',
            \       'cterm': 'nocombine',
            \       'ctermfg': '16',
            \       'ctermbg': '168'
            \   },
            \   'stlNameOnlyMode': {
            \       'gui': 'nocombine',
            \       'font': 'NONE',
            \       'guifg': '#3E4452',
            \       'guibg': '#61AFEF',
            \       'cterm': 'nocombine',
            \       'ctermfg': '16',
            \       'ctermbg': '75'
            \   },
            \   'stlFullPathMode': {
            \       'gui': 'nocombine',
            \       'font': 'NONE',
            \       'guifg': '#3E4452',
            \       'guibg': '#61AFEF',
            \       'cterm': 'nocombine',
            \       'ctermfg': '16',
            \       'ctermbg': '147'
            \   },
            \   'stlFuzzyMode': {
            \       'gui': 'nocombine',
            \       'font': 'NONE',
            \       'guifg': '#3E4452',
            \       'guibg': '#E5C07B',
            \       'cterm': 'nocombine',
            \       'ctermfg': '16',
            \       'ctermbg': '180'
            \   },
            \   'stlRegexMode': {
            \       'gui': 'nocombine',
            \       'font': 'NONE',
            \       'guifg': '#3E4452',
            \       'guibg': '#98C379',
            \       'cterm': 'nocombine',
            \       'ctermfg': '16',
            \       'ctermbg': '76'
            \   },
            \   'stlCwd': {
            \       'gui': 'nocombine',
            \       'font': 'NONE',
            \       'guifg': '#ABB2BF',
            \       'guibg': '#475265',
            \       'cterm': 'nocombine',
            \       'ctermfg': '145',
            \       'ctermbg': '236'
            \   },
            \   'stlBlank': {
            \       'gui': 'nocombine',
            \       'font': 'NONE',
            \       'guifg': '#ABB2BF',
            \       'guibg': '#3E4452',
            \       'cterm': 'nocombine',
            \       'ctermfg': '145',
            \       'ctermbg': '235'
            \   },
            \   'stlSpin': {
            \       'gui': 'nocombine',
            \       'font': 'NONE',
            \       'guifg': '#E6E666',
            \       'guibg': '#3E4452',
            \       'cterm': 'nocombine',
            \       'ctermfg': '185',
            \       'ctermbg': '235'
            \   },
            \   'stlLineInfo': {
            \       'gui': 'nocombine',
            \       'font': 'NONE',
            \       'guifg': '#3E4452',
            \       'guibg': '#98C379',
            \       'cterm': 'nocombine',
            \       'ctermfg': '16',
            \       'ctermbg': '76'
            \   },
            \   'stlTotal': {
            \       'gui': 'nocombine',
            \       'font': 'NONE',
            \       'guifg': '#3E4452',
            \       'guibg': '#98C379',
            \       'cterm': 'nocombine',
            \       'ctermfg': '16',
            \       'ctermbg': '76'
            \   }
            \ }

let g:leaderf#colorscheme#one#palette = leaderf#colorscheme#mergePalette(s:palette)
