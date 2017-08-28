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

    highlight def Lf_hl_selection guibg=#A5EB84 guifg=Black ctermbg=156 ctermfg=Black
    highlight def link Lf_hl_help               comment
    highlight def link Lf_hl_helpCmd            Identifier
    if &background ==? "dark"
        highlight def Lf_hl_match gui=bold guifg=SpringGreen cterm=bold ctermfg=49
        highlight def Lf_hl_matchRefine  gui=bold guifg=Magenta cterm=bold ctermfg=201
    else
        highlight def Lf_hl_match gui=bold guifg=#BB47F5 cterm=bold ctermfg=165
        highlight def Lf_hl_matchRefine  gui=bold guifg=Magenta cterm=bold ctermfg=201
    endif
    highlight def link Lf_hl_bufNumber          Constant
    highlight def link Lf_hl_bufIndicators      Statement
    highlight def link Lf_hl_bufModified        String
    highlight def link Lf_hl_bufNomodifiable    Comment
    highlight def link Lf_hl_bufDirname         Directory
    highlight def link Lf_hl_tagFile            Directory
    highlight def link Lf_hl_tagType            Type
    highlight def link Lf_hl_tagKeyword         Keyword
    highlight def link Lf_hl_buftagKind         Title
    highlight def link Lf_hl_buftagScopeType    Keyword
    highlight def link Lf_hl_buftagScope        Type
    highlight def link Lf_hl_buftagDirname      Directory
    highlight def link Lf_hl_buftagLineNum      Constant
    highlight def link Lf_hl_buftagCode         Comment
    highlight def link Lf_hl_funcKind           Title
    highlight def link Lf_hl_funcReturnType     Type
    highlight def link Lf_hl_funcScope          Keyword
    highlight def link Lf_hl_funcName           Function
    highlight def link Lf_hl_funcDirname        Directory
    highlight def link Lf_hl_funcLineNum        Constant
    highlight def link Lf_hl_lineLocation       Comment
    highlight def link Lf_hl_historyIndex       Constant
    highlight def link Lf_hl_selfIndex          Constant
    highlight def link Lf_hl_selfDescription    Comment
    highlight def link Lf_hl_helpTagfile        Comment
endif

let b:current_syntax = "leaderf"
