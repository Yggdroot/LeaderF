" ============================================================================
" File:        autoload/leaderf/colorscheme/gruvbox_material.vim
" Description: Gruvbox with Material Palette
" Author:      Sainnhe Park <sainnhe@gmail.com>
" Website:     https://github.com/sainnhe/gruvbox-material/
" Note:
" License:     MIT, Anti-996
" ============================================================================


if &background ==# 'light'
    let s:palette = {
                \   'stlName': {
                \       'gui': 'bold,nocombine',
                \       'font': 'NONE',
                \       'guifg': '#ebdbb2',
                \       'guibg': '#7c6f64',
                \       'cterm': 'bold,nocombine',
                \       'ctermfg': '223',
                \       'ctermbg': '243'
                \   },
                \   'stlCategory': {
                \       'gui': 'nocombine',
                \       'font': 'NONE',
                \       'guifg': '#4f3829',
                \       'guibg': '#bdae93',
                \       'cterm': 'nocombine',
                \       'ctermfg': '241',
                \       'ctermbg': '248'
                \   },
                \   'stlNameOnlyMode': {
                \       'gui': 'nocombine',
                \       'font': 'NONE',
                \       'guifg': '#4f3829',
                \       'guibg': '#d5c4a1',
                \       'cterm': 'nocombine',
                \       'ctermfg': '241',
                \       'ctermbg': '250'
                \   },
                \   'stlFullPathMode': {
                \       'gui': 'nocombine',
                \       'font': 'NONE',
                \       'guifg': '#4f3829',
                \       'guibg': '#d5c4a1',
                \       'cterm': 'nocombine',
                \       'ctermfg': '241',
                \       'ctermbg': '250'
                \   },
                \   'stlFuzzyMode': {
                \       'gui': 'nocombine',
                \       'font': 'NONE',
                \       'guifg': '#4f3829',
                \       'guibg': '#d5c4a1',
                \       'cterm': 'nocombine',
                \       'ctermfg': '241',
                \       'ctermbg': '250'
                \   },
                \   'stlRegexMode': {
                \       'gui': 'nocombine',
                \       'font': 'NONE',
                \       'guifg': '#4f3829',
                \       'guibg': '#d5c4a1',
                \       'cterm': 'nocombine',
                \       'ctermfg': '241',
                \       'ctermbg': '250'
                \   },
                \   'stlCwd': {
                \       'gui': 'nocombine',
                \       'font': 'NONE',
                \       'guifg': '#4f3829',
                \       'guibg': '#ebdbb2',
                \       'cterm': 'nocombine',
                \       'ctermfg': '241',
                \       'ctermbg': '223'
                \   },
                \   'stlBlank': {
                \       'gui': 'nocombine',
                \       'font': 'NONE',
                \       'guifg': '#4f3829',
                \       'guibg': '#ebdbb2',
                \       'cterm': 'nocombine',
                \       'ctermfg': '241',
                \       'ctermbg': '223'
                \   },
                \   'stlSpin': {
                \       'gui': 'nocombine',
                \       'font': 'NONE',
                \       'guifg': '#984c93',
                \       'guibg': '#ebdbb2',
                \       'cterm': 'nocombine',
                \       'ctermfg': '96',
                \       'ctermbg': '223'
                \   },
                \   'stlLineInfo': {
                \       'gui': 'nocombine',
                \       'font': 'NONE',
                \       'guifg': '#4f3829',
                \       'guibg': '#d5c4a1',
                \       'cterm': 'nocombine',
                \       'ctermfg': '241',
                \       'ctermbg': '250'
                \   },
                \   'stlTotal': {
                \       'gui': 'bold,nocombine',
                \       'font': 'NONE',
                \       'guifg': '#ebdbb2',
                \       'guibg': '#7c6f64',
                \       'cterm': 'bold,nocombine',
                \       'ctermfg': '223',
                \       'ctermbg': '243'
                \   }
                \ }
else
    let s:palette = {
                \   'stlName': {
                \       'gui': 'bold,nocombine',
                \       'font': 'NONE',
                \       'guifg': '#282828',
                \       'guibg': '#a89984',
                \       'cterm': 'bold,nocombine',
                \       'ctermfg': '235',
                \       'ctermbg': '246'
                \   },
                \   'stlCategory': {
                \       'gui': 'nocombine',
                \       'font': 'NONE',
                \       'guifg': '#ddc7a1',
                \       'guibg': '#665c54',
                \       'cterm': 'nocombine',
                \       'ctermfg': '223',
                \       'ctermbg': '241'
                \   },
                \   'stlNameOnlyMode': {
                \       'gui': 'nocombine',
                \       'font': 'NONE',
                \       'guifg': '#ddc7a1',
                \       'guibg': '#504945',
                \       'cterm': 'nocombine',
                \       'ctermfg': '223',
                \       'ctermbg': '239'
                \   },
                \   'stlFullPathMode': {
                \       'gui': 'nocombine',
                \       'font': 'NONE',
                \       'guifg': '#ddc7a1',
                \       'guibg': '#504945',
                \       'cterm': 'nocombine',
                \       'ctermfg': '223',
                \       'ctermbg': '239'
                \   },
                \   'stlFuzzyMode': {
                \       'gui': 'nocombine',
                \       'font': 'NONE',
                \       'guifg': '#ddc7a1',
                \       'guibg': '#504945',
                \       'cterm': 'nocombine',
                \       'ctermfg': '223',
                \       'ctermbg': '239'
                \   },
                \   'stlRegexMode': {
                \       'gui': 'nocombine',
                \       'font': 'NONE',
                \       'guifg': '#ddc7a1',
                \       'guibg': '#504945',
                \       'cterm': 'nocombine',
                \       'ctermfg': '223',
                \       'ctermbg': '239'
                \   },
                \   'stlCwd': {
                \       'gui': 'nocombine',
                \       'font': 'NONE',
                \       'guifg': '#ddc7a1',
                \       'guibg': '#3c3836',
                \       'cterm': 'nocombine',
                \       'ctermfg': '223',
                \       'ctermbg': '237'
                \   },
                \   'stlBlank': {
                \       'gui': 'nocombine',
                \       'font': 'NONE',
                \       'guifg': '#ddc7a1',
                \       'guibg': '#3c3836',
                \       'cterm': 'nocombine',
                \       'ctermfg': '223',
                \       'ctermbg': '237'
                \   },
                \   'stlSpin': {
                \       'gui': 'nocombine',
                \       'font': 'NONE',
                \       'guifg': '#E6E666',
                \       'guibg': '#3c3836',
                \       'cterm': 'nocombine',
                \       'ctermfg': '185',
                \       'ctermbg': '227'
                \   },
                \   'stlLineInfo': {
                \       'gui': 'nocombine',
                \       'font': 'NONE',
                \       'guifg': '#ddc7a1',
                \       'guibg': '#665c54',
                \       'cterm': 'nocombine',
                \       'ctermfg': '223',
                \       'ctermbg': '241'
                \   },
                \   'stlTotal': {
                \       'gui': 'nocombine',
                \       'font': 'NONE',
                \       'guifg': '#282828',
                \       'guibg': '#a89984',
                \       'cterm': 'bold,nocombine',
                \       'ctermfg': '235',
                \       'ctermbg': '246'
                \   }
                \ }
endif

let g:leaderf#colorscheme#gruvbox_material#palette = leaderf#colorscheme#mergePalette(s:palette)
