" ============================================================================
" File:        leaderf.vim
" Description: LeaderF syntax settings
" Author:      Yggdroot <archofortune@gmail.com>
" Website:     https://github.com/Yggdroot
" Note:
" License:     This script is released under the Vim License.
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
    highlight def Lf_hl_match gui=bold guifg=LightGreen cterm=bold ctermfg=LightGreen
    highlight def Lf_hl_matchRefine  gui=bold guifg=Magenta cterm=bold ctermfg=Magenta
    highlight def link Lf_hl_bufNumber          Constant
    highlight def link Lf_hl_bufIndicators      Statement
    highlight def link Lf_hl_bufModified        String
    highlight def link Lf_hl_bufNomodifiable    Comment
    highlight def link Lf_hl_bufDirname         Directory
endif

let b:current_syntax = "leaderf"
