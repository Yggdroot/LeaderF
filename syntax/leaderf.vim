" ============================================================================
" File:        leaderf.vim
" Description: LeaderF syntax settings
" Author:      Yggdroot <archofortune@gmail.com>
" Website:     https://github.com/Yggdroot
" Note:
" License:     Apache License, Version 2.0
" ============================================================================

scriptencoding utf-8

if exists("b:current_syntax")
    finish
endif

if has("syntax")
    syn clear
    syn match Lf_hl_help     display '^".*'
    syn match Lf_hl_helpCmd  display '^"\s*\zs.\{-}\ze\s*:' containedin=Lf_hl_help contained
    syn match Lf_hl_nonHelp  display '^[^"].*$'
    if has("win32") || has("win64")
        syn match Lf_hl_filename display '[^\/]*$' containedin=Lf_hl_nonHelp contained
        syn match Lf_hl_dirname  display '^.*[\/]' containedin=Lf_hl_nonHelp contained
    else
        syn match Lf_hl_filename display '[^/]*$' containedin=Lf_hl_nonHelp contained
        syn match Lf_hl_dirname  display '^.*/'   containedin=Lf_hl_nonHelp contained
    endif
endif

let b:current_syntax = "leaderf"

function! g:LfDefineDefaultColors() abort
    highlight def link Lf_hl_popup_cursor Cursor
    highlight def Lf_hl_cursorline guifg=Yellow guibg=NONE gui=NONE ctermfg=226 ctermbg=NONE cterm=NONE

    " the color of matching character
    highlight def Lf_hl_match  guifg=SpringGreen guibg=NONE gui=bold ctermfg=85 ctermbg=NONE cterm=bold

    " the color of matching character in `And mode`
    highlight def Lf_hl_match0 guifg=SpringGreen guibg=NONE gui=bold ctermfg=85 ctermbg=NONE cterm=bold
    highlight def Lf_hl_match1 guifg=#fe8019 guibg=NONE gui=bold ctermfg=208 ctermbg=NONE cterm=bold
    highlight def Lf_hl_match2 guifg=#3ff5d1 guibg=NONE gui=bold ctermfg=50 ctermbg=NONE cterm=bold
    highlight def Lf_hl_match3 guifg=#ff7272 guibg=NONE gui=bold ctermfg=203 ctermbg=NONE cterm=bold
    highlight def Lf_hl_match4 guifg=#43b9f0 guibg=NONE gui=bold ctermfg=74 ctermbg=NONE cterm=bold

    " the color of matching character in nameOnly mode when ';' is typed
    highlight def Lf_hl_matchRefine gui=bold guifg=Magenta cterm=bold ctermfg=201

    " the color of help in normal mode when <F1> is pressed
    highlight def link Lf_hl_help               Comment
    highlight def link Lf_hl_helpCmd            Identifier

    " the color when select multiple lines
    highlight def Lf_hl_selection guifg=Black guibg=#a5eb84 gui=NONE ctermfg=Black ctermbg=156 cterm=NONE

    " the color of `Leaderf buffer`
    highlight def link Lf_hl_bufNumber          Constant
    highlight def link Lf_hl_bufIndicators      Statement
    highlight def link Lf_hl_bufModified        String
    highlight def link Lf_hl_bufNomodifiable    Comment
    highlight def link Lf_hl_bufDirname         Directory

    " the color of `Leaderf tag`
    highlight def link Lf_hl_tagFile            Directory
    highlight def link Lf_hl_tagType            Type
    highlight def link Lf_hl_tagKeyword         Keyword

    " the color of `Leaderf bufTag`
    highlight def link Lf_hl_buftagKind         Title
    highlight def link Lf_hl_buftagScopeType    Keyword
    highlight def link Lf_hl_buftagScope        Type
    highlight def link Lf_hl_buftagDirname      Directory
    highlight def link Lf_hl_buftagLineNum      Constant
    highlight def link Lf_hl_buftagCode         Comment

    " the color of `Leaderf function`
    highlight def link Lf_hl_funcKind           Title
    highlight def link Lf_hl_funcReturnType     Type
    highlight def link Lf_hl_funcScope          Keyword
    highlight def link Lf_hl_funcName           Function
    highlight def link Lf_hl_funcDirname        Directory
    highlight def link Lf_hl_funcLineNum        Constant

    " the color of `Leaderf line`
    highlight def link Lf_hl_lineLocation       Comment

    " the color of `Leaderf self`
    highlight def link Lf_hl_selfIndex          Constant
    highlight def link Lf_hl_selfDescription    Comment

    " the color of `Leaderf help`
    highlight def link Lf_hl_helpTagfile        Comment

    " the color of `Leaderf rg`
    highlight def link Lf_hl_rgFileName         Directory
    highlight def link Lf_hl_rgLineNumber       Constant
    " the color of line number if '-A' or '-B' or '-C' is in the options list
    " of `Leaderf rg`
    highlight def link Lf_hl_rgLineNumber2      Folded
    " the color of column number if '--column' in g:Lf_RgConfig
    highlight def link Lf_hl_rgColumnNumber     Constant
    highlight def Lf_hl_rgHighlight guifg=#000000 guibg=#cccc66 gui=NONE ctermfg=16 ctermbg=185 cterm=NONE

    " the color of `Leaderf gtags`
    highlight def link Lf_hl_gtagsFileName      Directory
    highlight def link Lf_hl_gtagsLineNumber    Constant
    highlight def Lf_hl_gtagsHighlight guifg=#000000 guibg=#cccc66 gui=NONE ctermfg=16 ctermbg=185 cterm=NONE

    highlight def link Lf_hl_previewTitle       Statusline

    highlight def link Lf_hl_winNumber          Constant
    highlight def link Lf_hl_winIndicators      Statement
    highlight def link Lf_hl_winModified        String
    highlight def link Lf_hl_winNomodifiable    Comment
    highlight def link Lf_hl_winDirname         Directory

    highlight def link Lf_hl_quickfixFileName   Directory
    highlight def link Lf_hl_quickfixLineNumber Constant
    highlight def link Lf_hl_quickfixColumnNumber Constant

    highlight def link Lf_hl_loclistFileName    Directory
    highlight def link Lf_hl_loclistLineNumber  Constant
    highlight def link Lf_hl_loclistColumnNumber Constant

    highlight def link Lf_hl_jumpsTitle         Title
    highlight def link Lf_hl_jumpsNumber        Number
    highlight def link Lf_hl_jumpsLineCol       String
    highlight def link Lf_hl_jumpsIndicator     Type
endfunction
