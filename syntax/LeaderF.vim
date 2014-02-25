" ============================================================================
" File:        LeaderF.vim
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
    syn match Lf_hl_help        '^".*'
    syn match Lf_hl_helpCmd     '^"\s*\zs.\{-}\ze\s*:' containedin=Lf_hl_help contained
    syn match Lf_hl_nonHelp     '^[^"].*'
    if has("win32") || has("win64")
        syn match Lf_hl_filename '[^\/]*$' containedin=Lf_hl_nonHelp contained
    else
        syn match Lf_hl_filename '[^/]*$'  containedin=Lf_hl_nonHelp contained
    endif

    highlight def link Lf_hl_selection      Todo
    highlight def link Lf_hl_help           comment
    highlight def link Lf_hl_helpCmd        Identifier
    highlight def link Lf_hl_match          String
    highlight def link Lf_hl_stlFunction    Statusline
    highlight def link Lf_hl_stlMode        Statusline
    highlight def link Lf_hl_stlCurDir      Statusline
endif         

let b:current_syntax = "LeaderF"
