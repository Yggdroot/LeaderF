" ============================================================================
" File:        powerline.vim
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
            \       'guifg': '#005F00',
            \       'guibg': '#AFDF00',
            \       'cterm': 'bold,nocombine',
            \       'ctermfg': '22',
            \       'ctermbg': '148'
            \   },
            \   'stlCategory': {
            \       'gui': 'nocombine',
            \       'font': 'NONE',
            \       'guifg': '#870000',
            \       'guibg': '#FF8700',
            \       'cterm': 'nocombine',
            \       'ctermfg': '88',
            \       'ctermbg': '208'
            \   },
            \   'stlNameOnlyMode': {
            \       'gui': 'nocombine',
            \       'font': 'NONE',
            \       'guifg': '#005D5D',
            \       'guibg': '#FFFFFF',
            \       'cterm': 'nocombine',
            \       'ctermfg': '23',
            \       'ctermbg': '231'
            \   },
            \   'stlFullPathMode': {
            \       'gui': 'nocombine',
            \       'font': 'NONE',
            \       'guifg': '#FFFFFF',
            \       'guibg': '#FF2929',
            \       'cterm': 'nocombine',
            \       'ctermfg': '231',
            \       'ctermbg': '196'
            \   },
            \   'stlFuzzyMode': {
            \       'gui': 'nocombine',
            \       'font': 'NONE',
            \       'guifg': '#004747',
            \       'guibg': '#FFFFFF',
            \       'cterm': 'nocombine',
            \       'ctermfg': '23',
            \       'ctermbg': '231'
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
            \       'guifg': '#FFFFFF',
            \       'guibg': '#585858',
            \       'cterm': 'nocombine',
            \       'ctermfg': '231',
            \       'ctermbg': '240'
            \   },
            \   'stlBlank': {
            \       'gui': 'nocombine',
            \       'font': 'NONE',
            \       'guifg': 'NONE',
            \       'guibg': '#303136',
            \       'cterm': 'nocombine',
            \       'ctermfg': 'NONE',
            \       'ctermbg': '236'
            \   },
            \   'stlSpin': {
            \       'gui': 'nocombine',
            \       'font': 'NONE',
            \       'guifg': '#E6E666',
            \       'guibg': '#303136',
            \       'cterm': 'nocombine',
            \       'ctermfg': '185',
            \       'ctermbg': '236'
            \   },
            \   'stlLineInfo': {
            \       'gui': 'nocombine',
            \       'font': 'NONE',
            \       'guifg': '#C9C9C9',
            \       'guibg': '#585858',
            \       'cterm': 'nocombine',
            \       'ctermfg': '251',
            \       'ctermbg': '240'
            \   },
            \   'stlTotal': {
            \       'gui': 'nocombine',
            \       'font': 'NONE',
            \       'guifg': '#545454',
            \       'guibg': '#D0D0D0',
            \       'cterm': 'nocombine',
            \       'ctermfg': '240',
            \       'ctermbg': '252'
            \   }
            \ }

let g:leaderf#colorscheme#powerline#palette = leaderf#colorscheme#mergePalette(s:palette)
