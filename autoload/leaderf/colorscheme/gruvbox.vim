" ============================================================================
" File:        gruvbox.vim
" Description:
" Author:      yebenny <yebenmmy@protonmail.com>
" Website:     https://github.com/bennyyip
" Note:
" License:     Apache License, Version 2.0
" ============================================================================

" NOTE: THIS COLOR ONLY WORKS WHEN USING GRUVBOX

function! s:getTermColor(group)
  let termColor = synIDattr(hlID(a:group), "fg", "cterm")
  return  termColor
endfunction

function! s:getGuiColor(group)
  let guiColor = synIDattr(hlID(a:group), "fg", "gui")
  return guiColor
endfunction

  let s:termbg0  = s:getTermColor('GruvboxBg0')
  let s:termbg1  = s:getTermColor('GruvboxBg1')
  let s:termbg2  = s:getTermColor('GruvboxBg2')
  let s:termbg4  = s:getTermColor('GruvboxBg4')
  let s:termfg1  = s:getTermColor('GruvboxFg1')
  let s:termfg4  = s:getTermColor('GruvboxFg4')

  let s:guibg0  = s:getGuiColor('GruvboxBg0')
  let s:guibg1  = s:getGuiColor('GruvboxBg1')
  let s:guibg2  = s:getGuiColor('GruvboxBg2')
  let s:guibg4  = s:getGuiColor('GruvboxBg4')
  let s:guifg1  = s:getGuiColor('GruvboxFg1')
  let s:guifg4  = s:getGuiColor('GruvboxFg4')


  let s:termyellow = s:getTermColor('GruvboxYellow')
  let s:termblue   = s:getTermColor('GruvboxBlue')
  let s:termaqua   = s:getTermColor('GruvboxAqua')
  let s:termorange = s:getTermColor('GruvboxOrange')
  let s:termgreen  = s:getTermColor('GruvboxGreen')
  let s:termred    = s:getTermColor('GruvboxRed')
  let s:termpurple = s:getTermColor('GruvboxPurple')

  let s:guiyellow = s:getGuiColor('GruvboxYellow')
  let s:guiblue   = s:getGuiColor('GruvboxBlue')
  let s:guiaqua   = s:getGuiColor('GruvboxAqua')
  let s:guiorange = s:getGuiColor('GruvboxOrange')
  let s:guigreen  = s:getGuiColor('GruvboxGreen')
  let s:guired    = s:getGuiColor('GruvboxRed')
  let s:guipurple = s:getGuiColor('GruvboxPurple')

let s:palette = {
            \   'stlName': {
            \       'gui': 'bold',
            \       'font': 'NONE',
            \       'guifg': s:guibg0,
            \       'guibg': s:guiyellow,
            \       'cterm': 'bold',
            \       'ctermfg': s:termbg0,
            \       'ctermbg': s:termyellow
            \   },
            \   'stlCategory': {
            \       'gui': 'NONE',
            \       'font': 'NONE',
            \       'guifg': s:guibg0,
            \       'guibg': s:guiaqua,
            \       'cterm': 'NONE',
            \       'ctermfg': s:termbg0,
            \       'ctermbg': s:termaqua
            \   },
            \   'stlNameOnlyMode': {
            \       'gui': 'NONE',
            \       'font': 'NONE',
            \       'guifg': s:guibg0,
            \       'guibg': s:guiblue,
            \       'cterm': 'NONE',
            \       'ctermfg': s:termbg0,
            \       'ctermbg': s:termblue
            \   },
            \   'stlFullPathMode': {
            \       'gui': 'NONE',
            \       'font': 'NONE',
            \       'guifg': s:guibg0,
            \       'guibg': s:guipurple,
            \       'cterm': 'NONE',
            \       'ctermfg': s:termbg0,
            \       'ctermbg': s:termpurple
            \   },
            \   'stlFuzzyMode': {
            \       'gui': 'NONE',
            \       'font': 'NONE',
            \       'guifg': s:guibg0,
            \       'guibg': s:guired,
            \       'cterm': 'NONE',
            \       'ctermfg': s:termbg0,
            \       'ctermbg': s:termred
            \   },
            \   'stlRegexMode': {
            \       'gui': 'NONE',
            \       'font': 'NONE',
            \       'guifg': s:guibg0,
            \       'guibg': s:guigreen,
            \       'cterm': 'NONE',
            \       'ctermfg': s:termbg0,
            \       'ctermbg': s:termgreen
            \   },
            \   'stlCwd': {
            \       'gui': 'NONE',
            \       'font': 'NONE',
            \       'guifg': s:guifg1,
            \       'guibg': s:guibg2,
            \       'cterm': 'NONE',
            \       'ctermfg': s:termfg1,
            \       'ctermbg': s:termbg2
            \   },
            \   'stlBlank': {
            \       'gui': 'NONE',
            \       'font': 'NONE',
            \       'guifg': s:guifg4,
            \       'guibg': s:guibg2,
            \       'cterm': 'NONE',
            \       'ctermfg': s:termbg4,
            \       'ctermbg': s:termbg2
            \   }
            \ }

let s:palette.stlLineInfo = s:palette.stlCwd
let s:palette.stlTotal = s:palette.stlName

let g:leaderf#colorscheme#gruvbox#palette = leaderf#colorscheme#mergePalette(s:palette)
