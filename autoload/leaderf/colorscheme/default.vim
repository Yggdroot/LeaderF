" ============================================================================
" File:        default.vim
" Description:
" Author:      Yggdroot <archofortune@gmail.com>
" Website:     https://github.com/Yggdroot
" Note:
" License:     Apache License, Version 2.0
" ============================================================================

let s:palette = {
            \   'stlName': {
            \       'gui': 'bold,nocombine',
            \       'font': 'NONE',
            \       'guifg': '#2F5C00',
            \       'guibg': '#BAFFA3',
            \       'cterm': 'bold,nocombine',
            \       'ctermfg': '22',
            \       'ctermbg': '157'
            \   },
            \   'stlCategory': {
            \       'gui': 'nocombine',
            \       'font': 'NONE',
            \       'guifg': '#000000',
            \       'guibg': '#F28379',
            \       'cterm': 'nocombine',
            \       'ctermfg': '16',
            \       'ctermbg': '210'
            \   },
            \   'stlNameOnlyMode': {
            \       'gui': 'nocombine',
            \       'font': 'NONE',
            \       'guifg': '#000000',
            \       'guibg': '#E8ED51',
            \       'cterm': 'nocombine',
            \       'ctermfg': '16',
            \       'ctermbg': '227'
            \   },
            \   'stlFullPathMode': {
            \       'gui': 'nocombine',
            \       'font': 'NONE',
            \       'guifg': '#000000',
            \       'guibg': '#AAAAFF',
            \       'cterm': 'nocombine',
            \       'ctermfg': '16',
            \       'ctermbg': '147'
            \   },
            \   'stlFuzzyMode': {
            \       'gui': 'nocombine',
            \       'font': 'NONE',
            \       'guifg': '#000000',
            \       'guibg': '#E8ED51',
            \       'cterm': 'nocombine',
            \       'ctermfg': '16',
            \       'ctermbg': '227'
            \   },
            \   'stlRegexMode': {
            \       'gui': 'nocombine',
            \       'font': 'NONE',
            \       'guifg': '#000000',
            \       'guibg': '#7FECAD',
            \       'cterm': 'nocombine',
            \       'ctermfg': '16',
            \       'ctermbg': '121'
            \   },
            \   'stlCwd': {
            \       'gui': 'nocombine',
            \       'font': 'NONE',
            \       'guifg': '#EBFFEF',
            \       'guibg': '#606168',
            \       'cterm': 'nocombine',
            \       'ctermfg': '195',
            \       'ctermbg': '241'
            \   },
            \   'stlBlank': {
            \       'gui': 'nocombine',
            \       'font': 'NONE',
            \       'guifg': 'NONE',
            \       'guibg': '#3B3E4C',
            \       'cterm': 'nocombine',
            \       'ctermfg': 'NONE',
            \       'ctermbg': '237'
            \   },
            \   'stlSpin': {
            \       'gui': 'nocombine',
            \       'font': 'NONE',
            \       'guifg': '#E6E666',
            \       'guibg': '#3B3E4C',
            \       'cterm': 'nocombine',
            \       'ctermfg': '185',
            \       'ctermbg': '237'
            \   },
            \   'stlLineInfo': {
            \       'gui': 'nocombine',
            \       'font': 'NONE',
            \       'guifg': '#000000',
            \       'guibg': '#EBFFEF',
            \       'cterm': 'nocombine',
            \       'ctermfg': '16',
            \       'ctermbg': '195'
            \   },
            \   'stlTotal': {
            \       'gui': 'nocombine',
            \       'font': 'NONE',
            \       'guifg': '#000000',
            \       'guibg': '#BCDC5C',
            \       'cterm': 'nocombine',
            \       'ctermfg': '16',
            \       'ctermbg': '149'
            \   }
            \ }

let g:leaderf#colorscheme#default#palette = leaderf#colorscheme#mergePalette(s:palette)
