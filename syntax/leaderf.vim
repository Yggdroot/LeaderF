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
        highlight def Lf_hl_match  gui=bold guifg=SpringGreen cterm=bold ctermfg=48
        highlight def Lf_hl_match0 gui=bold guifg=SpringGreen cterm=bold ctermfg=48
        highlight def Lf_hl_match1 gui=bold guifg=#FE8019 cterm=bold ctermfg=208
        highlight def Lf_hl_match2 gui=bold guifg=#3FF5D1 cterm=bold ctermfg=50
        highlight def Lf_hl_match3 gui=bold guifg=#FF7272 cterm=bold ctermfg=203
        highlight def Lf_hl_match4 gui=bold guifg=#43B9F0 cterm=bold ctermfg=74
        highlight def Lf_hl_matchRefine  gui=bold guifg=Magenta cterm=bold ctermfg=201
    else
        highlight def Lf_hl_match  gui=bold guifg=#1540AD cterm=bold ctermfg=26
        highlight def Lf_hl_match0 gui=bold guifg=#1540AD cterm=bold ctermfg=26
        highlight def Lf_hl_match1 gui=bold guifg=#A52A2A cterm=bold ctermfg=124
        highlight def Lf_hl_match2 gui=bold guifg=#B52BB0 cterm=bold ctermfg=127
        highlight def Lf_hl_match3 gui=bold guifg=#02781A cterm=bold ctermfg=28
        highlight def Lf_hl_match4 gui=bold guifg=#F70505 cterm=bold ctermfg=196
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
    highlight def link Lf_hl_rgFileName         Directory
    highlight def link Lf_hl_rgLineNumber       Constant
    highlight def link Lf_hl_rgLineNumber2      Folded
    highlight def link Lf_hl_rgColumnNumber     Constant
    highlight def Lf_hl_rgHighlight guifg=#000000 guibg=#CCCC66 ctermfg=16 ctermbg=185
endif

let b:current_syntax = "leaderf"
