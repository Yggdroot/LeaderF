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
                \       'gui': 'bold',
                \       'font': 'NONE',
                \       'guifg': '#ebdbb2',
                \       'guibg': '#7c6f64',
                \       'cterm': 'bold',
                \       'ctermfg': '223',
                \       'ctermbg': '243'
                \   },
                \   'stlCategory': {
                \       'gui': 'NONE',
                \       'font': 'NONE',
                \       'guifg': '#4f3829',
                \       'guibg': '#bdae93',
                \       'cterm': 'NONE',
                \       'ctermfg': '241',
                \       'ctermbg': '248'
                \   },
                \   'stlNameOnlyMode': {
                \       'gui': 'NONE',
                \       'font': 'NONE',
                \       'guifg': '#4f3829',
                \       'guibg': '#d5c4a1',
                \       'cterm': 'NONE',
                \       'ctermfg': '241',
                \       'ctermbg': '250'
                \   },
                \   'stlFullPathMode': {
                \       'gui': 'NONE',
                \       'font': 'NONE',
                \       'guifg': '#4f3829',
                \       'guibg': '#d5c4a1',
                \       'cterm': 'NONE',
                \       'ctermfg': '241',
                \       'ctermbg': '250'
                \   },
                \   'stlFuzzyMode': {
                \       'gui': 'NONE',
                \       'font': 'NONE',
                \       'guifg': '#4f3829',
                \       'guibg': '#d5c4a1',
                \       'cterm': 'NONE',
                \       'ctermfg': '241',
                \       'ctermbg': '250'
                \   },
                \   'stlRegexMode': {
                \       'gui': 'NONE',
                \       'font': 'NONE',
                \       'guifg': '#4f3829',
                \       'guibg': '#d5c4a1',
                \       'cterm': 'NONE',
                \       'ctermfg': '241',
                \       'ctermbg': '250'
                \   },
                \   'stlCwd': {
                \       'gui': 'NONE',
                \       'font': 'NONE',
                \       'guifg': '#4f3829',
                \       'guibg': '#ebdbb2',
                \       'cterm': 'NONE',
                \       'ctermfg': '241',
                \       'ctermbg': '223'
                \   },
                \   'stlBlank': {
                \       'gui': 'NONE',
                \       'font': 'NONE',
                \       'guifg': '#4f3829',
                \       'guibg': '#ebdbb2',
                \       'cterm': 'NONE',
                \       'ctermfg': '241',
                \       'ctermbg': '223'
                \   },
                \   'stlSpin': {
                \       'gui': 'NONE',
                \       'font': 'NONE',
                \       'guifg': '#984c93',
                \       'guibg': '#ebdbb2',
                \       'cterm': 'NONE',
                \       'ctermfg': '96',
                \       'ctermbg': '223'
                \   },
                \   'stlLineInfo': {
                \       'gui': 'NONE',
                \       'font': 'NONE',
                \       'guifg': '#4f3829',
                \       'guibg': '#d5c4a1',
                \       'cterm': 'NONE',
                \       'ctermfg': '241',
                \       'ctermbg': '250'
                \   },
                \   'stlTotal': {
                \       'gui': 'bold',
                \       'font': 'NONE',
                \       'guifg': '#ebdbb2',
                \       'guibg': '#7c6f64',
                \       'cterm': 'bold',
                \       'ctermfg': '223',
                \       'ctermbg': '243'
                \   }
                \ }
else
    let s:palette = {
                \   'stlName': {
                \       'gui': 'bold',
                \       'font': 'NONE',
                \       'guifg': '#282828',
                \       'guibg': '#a89984',
                \       'cterm': 'bold',
                \       'ctermfg': '235',
                \       'ctermbg': '246'
                \   },
                \   'stlCategory': {
                \       'gui': 'NONE',
                \       'font': 'NONE',
                \       'guifg': '#ddc7a1',
                \       'guibg': '#665c54',
                \       'cterm': 'NONE',
                \       'ctermfg': '223',
                \       'ctermbg': '241'
                \   },
                \   'stlNameOnlyMode': {
                \       'gui': 'NONE',
                \       'font': 'NONE',
                \       'guifg': '#ddc7a1',
                \       'guibg': '#504945',
                \       'cterm': 'NONE',
                \       'ctermfg': '223',
                \       'ctermbg': '239'
                \   },
                \   'stlFullPathMode': {
                \       'gui': 'NONE',
                \       'font': 'NONE',
                \       'guifg': '#ddc7a1',
                \       'guibg': '#504945',
                \       'cterm': 'NONE',
                \       'ctermfg': '223',
                \       'ctermbg': '239'
                \   },
                \   'stlFuzzyMode': {
                \       'gui': 'NONE',
                \       'font': 'NONE',
                \       'guifg': '#ddc7a1',
                \       'guibg': '#504945',
                \       'cterm': 'NONE',
                \       'ctermfg': '223',
                \       'ctermbg': '239'
                \   },
                \   'stlRegexMode': {
                \       'gui': 'NONE',
                \       'font': 'NONE',
                \       'guifg': '#ddc7a1',
                \       'guibg': '#504945',
                \       'cterm': 'NONE',
                \       'ctermfg': '223',
                \       'ctermbg': '239'
                \   },
                \   'stlCwd': {
                \       'gui': 'NONE',
                \       'font': 'NONE',
                \       'guifg': '#ddc7a1',
                \       'guibg': '#3c3836',
                \       'cterm': 'NONE',
                \       'ctermfg': '223',
                \       'ctermbg': '237'
                \   },
                \   'stlBlank': {
                \       'gui': 'NONE',
                \       'font': 'NONE',
                \       'guifg': '#ddc7a1',
                \       'guibg': '#3c3836',
                \       'cterm': 'NONE',
                \       'ctermfg': '223',
                \       'ctermbg': '237'
                \   },
                \   'stlSpin': {
                \       'gui': 'NONE',
                \       'font': 'NONE',
                \       'guifg': '#E6E666',
                \       'guibg': '#3c3836',
                \       'cterm': 'NONE',
                \       'ctermfg': '185',
                \       'ctermbg': '227'
                \   },
                \   'stlLineInfo': {
                \       'gui': 'NONE',
                \       'font': 'NONE',
                \       'guifg': '#ddc7a1',
                \       'guibg': '#665c54',
                \       'cterm': 'NONE',
                \       'ctermfg': '223',
                \       'ctermbg': '241'
                \   },
                \   'stlTotal': {
                \       'gui': 'NONE',
                \       'font': 'NONE',
                \       'guifg': '#282828',
                \       'guibg': '#a89984',
                \       'cterm': 'bold',
                \       'ctermfg': '235',
                \       'ctermbg': '246'
                \   }
                \ }
endif

let g:leaderf#colorscheme#gruvbox_material#palette = leaderf#colorscheme#mergePalette(s:palette)
